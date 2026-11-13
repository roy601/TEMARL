"""Read capture metadata and explicitly labelled telemetry without inventing attacks."""
import csv
import json
import os
import re
import gzip
import io
import zipfile
from contextlib import nullcontext
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml
import config

TECHNIQUE = re.compile(r"(?<![A-Za-z0-9])T\d{4}(?:\.\d{3})?(?![A-Za-z0-9.])", re.I)
LABEL_KEYS = {"technique_id", "technique_ids", "mitre_technique", "mitre_techniques", "attack_technique", "attack_techniques", "ruleName".lower()}
TIME_KEYS = ("_time", "@timestamp", "timestamp", "utctime", "eventtime", "systemtime", "time", "eventtimems")
HOST_KEYS = ("computer", "computername", "hostname", "host", "device_name", "deviceid")
TEXT_SUFFIXES = {".json", ".jsonl", ".ndjson", ".log", ".csv", ".txt", ".xml", ".raw"}


def fields(record):
    values = {}
    def visit(obj):
        for key, value in obj.items():
            if not isinstance(key, str):
                continue
            key = key.lower()
            if isinstance(value, dict):
                visit(value)
                if key == "host" and isinstance(value.get("name"), str):
                    values.setdefault("host", []).append(value["name"])
            else:
                values.setdefault(key, []).append(value)
    visit(record)
    # Conflicting nested fields must not be silently overwritten.
    return {key: items[0] for key, items in values.items() if all(v == items[0] for v in items)}


def parse_timestamp(value):
    if value is None or value == "":
        return None
    try:
        number = float(value)
        # Only plausible Unix dates, never line numbers or arbitrary digit substrings.
        if 1e12 <= number < 1e14:
            number /= 1000
        if not 946684800 <= number < 4102444800:
            return None
        return datetime.fromtimestamp(number, timezone.utc).timestamp()
    except (ValueError, TypeError, OverflowError):
        try:
            dt = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
            if "T" not in str(value) and " " not in str(value):
                return None
            return dt.replace(tzinfo=dt.tzinfo or timezone.utc).timestamp()
        except (ValueError, TypeError, OverflowError):
            return None


def extract_timestamp(record):
    flat = fields(record) if isinstance(record, dict) else {}
    for key in TIME_KEYS:
        ts = parse_timestamp(flat.get(key))
        if ts is not None:
            return ts
    return None


def techniques(value):
    return sorted(set(m.upper() for m in TECHNIQUE.findall(str(value))))


def read_records(path, audit, handle=None):
    """JSON, JSONL, CSV, and Windows XML events (including concatenated XML)."""
    with (nullcontext(handle) if handle is not None else path.open(encoding="utf-8-sig", errors="replace")) as handle:
        prefix = handle.read(256)
        handle.seek(0)
        if prefix.startswith("version https://git-lfs.github.com/spec"):
            audit["lfs_pointers"] += 1
            return
        if path.suffix.lower() == ".csv":
            yield from csv.DictReader(handle)
            return
        if prefix.lstrip().startswith("<"):
            buffer = ""
            for line in handle:
                buffer += line
                while "</Event>" in buffer:
                    end = buffer.index("</Event>") + len("</Event>")
                    chunk, buffer = buffer[:end], buffer[end:]
                    start = re.search(r"<Event(?:\s|>)", chunk)
                    if not start:
                        continue
                    try:
                        event = ET.fromstring(chunk[start.start():])
                        record = {}
                        for element in event.iter():
                            tag = element.tag.split("}")[-1]
                            if tag == "Data":
                                record[element.get("Name", "Data")] = element.text
                            elif tag == "TimeCreated":
                                record["SystemTime"] = element.get("SystemTime")
                            elif tag == "Computer":
                                record["Computer"] = element.text
                        yield record
                    except ET.ParseError:
                        audit["malformed_records"] += 1
                if len(buffer) > 4_000_000:
                    audit["unsupported_xml_chunks"] += 1
                    buffer = ""
            if buffer.strip() not in {"", "</Events>"}:
                audit["unparsed_xml_trailers"] += 1
            return
        if path.suffix.lower() == ".json" or prefix.lstrip().startswith("["):
            try:
                data = json.load(handle)
                if isinstance(data, dict):
                    yield data
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            yield item
                        else:
                            audit["unsupported_records"] += 1
                else:
                    audit["unsupported_records"] += 1
                return
            except json.JSONDecodeError:
                handle.seek(0)
        for line in handle:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if isinstance(record, dict):
                    yield record
                else:
                    audit["unsupported_records"] += 1
            except json.JSONDecodeError:
                audit["unparsed_lines"] += 1


def telemetry_records(path, audit):
    """Read archives in place; never extract or execute their contents."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                if Path(member.filename).suffix.lower() not in TEXT_SUFFIXES:
                    audit["unsupported_archive_members"] += 1
                    continue
                with archive.open(member) as raw, io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace") as stream:
                    for index, record in enumerate(read_records(Path(member.filename), audit, stream), 1):
                        yield member.filename, index, record
    elif path.suffix.lower() == ".gz":
        if path.name.lower().endswith(".tar.gz"):
            audit["unsupported_archives"] += 1
            return
        with gzip.open(path, "rt", encoding="utf-8-sig", errors="replace") as stream:
            for index, record in enumerate(read_records(Path(path.stem), audit, stream), 1):
                yield "", index, record
    else:
        for index, record in enumerate(read_records(path, audit), 1):
            yield "", index, record


def find_repository(repo_path=None):
    explicit = repo_path or os.environ.get("SPLUNK_ATTACK_DATA_DIR")
    if explicit:
        if not Path(explicit).is_dir():
            raise FileNotFoundError(f"Requested attack_data directory does not exist: {explicit}")
        return Path(explicit).resolve()
    candidates = [repo_path or os.environ.get("SPLUNK_ATTACK_DATA_DIR"),
                  Path(config.DATA_DIR) / "attack_data", Path(config.BASE_DIR) / "attack_data",
                  Path(config.BASE_DIR).parent / "attack_data",
                  Path("C:/Users/Riton/Downloads/attack_data")]
    for candidate in candidates:
        if candidate and Path(candidate).is_dir():
            return Path(candidate).resolve()
    raise FileNotFoundError("No attack_data checkout found. Pass --repo PATH or set SPLUNK_ATTACK_DATA_DIR. Generated output is never used as input.")


def scan_splunk_datasets(repo_path=None, no_logs=False):
    repo = find_repository(repo_path)
    source = repo / "datasets" if (repo / "datasets").is_dir() else repo
    audit = Counter()
    audit["telemetry_scan_skipped"] = int(no_logs)
    captures, events, ownership, coverage = [], [], {}, []
    metadata_paths = sorted(set(source.rglob("*.yml")) | set(source.rglob("*.yaml")))
    for path in metadata_paths:
        if path.name.lower() in {"template.yml", "template.yaml"}:
            audit["templates_skipped"] += 1
            continue
        if any(part in {".git", "output", "output_verified", "__pycache__"} for part in path.relative_to(source).parts):
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        except (OSError, yaml.YAMLError) as error:
            audit["metadata_errors"] += 1
            print(f"[!] {path}: {error}")
            continue
        if not isinstance(data, dict) or not isinstance(data.get("datasets"), list):
            continue
        capture_id = path.relative_to(repo).as_posix()
        labels = techniques(data.get("mitre_technique", []))
        captures.append({"capture_id": capture_id, "metadata_id": data.get("id"),
                         "techniques": labels, "label_source": "metadata", "ordered": False})
        for dataset in data["datasets"]:
            if not isinstance(dataset, dict) or not dataset.get("path"):
                continue
            raw = str(dataset["path"]).replace("\\", "/")
            target = (repo / raw.lstrip("/")) if raw.lstrip("/").startswith("datasets/") else (path.parent / raw)
            target = target.resolve()
            if not target.is_relative_to(repo):
                audit["external_paths_skipped"] += 1
                continue
            ownership.setdefault(target, set()).add(capture_id)
    if not no_logs:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            if any(part in {".git", "output", "output_verified", "__pycache__"} for part in path.relative_to(source).parts) or path.name in {"splunk_attack_data_ground_truth.json", "scan_audit.json", "capture_inventory.json", "sequences.json", "statistics.json", "session_audit.json"}:
                continue
            relative = path.relative_to(repo).as_posix()
            if path.suffix.lower() in {".yaml", ".yml"}:
                continue
            audit["files_inventoried"] += 1
            if path.suffix.lower() not in TEXT_SUFFIXES | {".zip", ".gz"}:
                audit["unsupported_files"] += 1
                coverage.append({"file": relative, "status": "unsupported_extension"})
                continue
            audit["files_scanned"] += 1
            file_audit = Counter()
            owners = ownership.get(path, set())
            # Ambiguous/unmapped telemetry is isolated by file, never merged by folder.
            capture = next(iter(owners)) if len(owners) == 1 else "file:" + relative
            if len(owners) > 1:
                audit["ambiguous_capture_files"] += 1
            try:
                for member, index, record in telemetry_records(path, file_audit):
                    file_audit["records_parsed"] += 1
                    flat = fields(record)
                    labels = sorted({t for key in LABEL_KEYS for t in techniques(flat.get(key, ""))})
                    if not labels:
                        file_audit["unlabelled_records"] += 1
                        continue
                    host = next((str(flat[k]).strip().lower() for k in HOST_KEYS if flat.get(k)), None)
                    timestamp = extract_timestamp(record)
                    event_file = relative + ("::" + member if member else "")
                    event_capture = capture if len(owners) == 1 else "file:" + event_file
                    events.append({"capture_id": event_capture, "host": host, "timestamp": timestamp,
                                   "technique_ids": labels, "file": event_file, "record_index": index,
                                   "label_source": "explicit_event_field"})
                    file_audit["labelled_records"] += 1
                    if timestamp is None:
                        file_audit["labelled_records_missing_time"] += 1
                    if host is None:
                        file_audit["labelled_records_missing_host"] += 1
            except (OSError, EOFError, ValueError, RuntimeError, csv.Error, zipfile.BadZipFile) as error:
                file_audit["file_errors"] += 1
                print(f"[!] {relative}: {error}")
            audit.update(file_audit)
            coverage.append({"file": relative, "counts": dict(file_audit)})
            print(f"[{audit['files_scanned']}] {relative}: parsed={file_audit['records_parsed']}, labelled={file_audit['labelled_records']}", flush=True)
    audit["metadata_captures"] = len(captures)
    audit["referenced_files_missing"] = sum(not path.is_file() for path in ownership)
    missing = [str(path.relative_to(repo)) for path in ownership if not path.is_file()]
    payload = {"schema_version": 2, "repository": str(repo), "events": events, "captures": captures, "audit": dict(audit)}
    Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
    destination = Path(config.DATA_DIR) / "splunk_attack_data_ground_truth.json"
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (Path(config.DATA_DIR) / "scan_audit.json").write_text(json.dumps(dict(audit), indent=2), encoding="utf-8")
    (Path(config.DATA_DIR) / "file_coverage.json").write_text(json.dumps({"files": coverage, "missing_references": missing}, indent=2), encoding="utf-8")
    print(f"[+] {len(captures)} capture definitions; {len(events)} explicitly labelled events. Audit: {dict(audit)}")
    return str(destination)


def run_download(no_logs=False, repo_path=None):
    return [scan_splunk_datasets(repo_path, no_logs)]


if __name__ == "__main__":
    run_download()
