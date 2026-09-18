# -*- coding: utf-8 -*-
"""
TEMARL v3 — Deterministic topology generator
============================================
Supplies the variable-topology substrate for the entity-based environment,
following the methodology of

    Symes Thompson, Caron, Hicks & Mavroudis (2024),
    "Entity-based Reinforcement Learning for Autonomous Cyber Defence",
    arXiv:2410.17647

That work decomposes observation and action spaces into discrete entities and
trains over a DISTRIBUTION of topologies. We port the formulation, not the
Yawning Titan implementation: TEMARL keeps its own D3FEND payoff, CAM-LDS
attacker profiles, and Dec-POMDP credit assignment.

WHY THIS EXISTS
---------------
env_v2 trains on ONE fixed 5-zone map. The reference paper reports that a
Transformer policy "matches performance when training on a single network" and
only "significantly outperforms" simpler policies "across fixed-size networks of
varying topologies". A topology distribution is therefore the specific
experimental condition under which an attention-based network encoder has a
stated mechanism to win. This module produces that distribution.

GUARANTEES
----------
Every generated topology is validated to be
  * connected (all zones reachable from the attacker entry zone),
  * in possession of exactly one attacker entry host,
  * in possession of at least one critical asset,
  * consistent with its firewall rules (no edge that a rule forbids),
  * free of unreachable or invalid hosts,
  * reproducible from (seed, config) alone, and
  * serialisable together with its seed and a content hash.

`canonical_topology()` reproduces env_v2's fixed 5-zone map exactly and is the
scientific CONTROL configuration.

All paths are resolved relative to this file or supplied on the command line.
No absolute or machine-specific path appears anywhere in this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# ── static vocabularies (fixed so the entity feature width never varies) ─────
NODE_TYPES = ["attacker", "dns", "server", "fileshare", "client", "admin",
              "database", "workstation"]
NODE_TYPE_ID = {t: i for i, t in enumerate(NODE_TYPES)}
N_NODE_TYPES = len(NODE_TYPES)

SERVICES = ["http", "https", "ssh", "smb", "dns", "rdp", "sql", "ftp"]
SERVICE_ID = {s: i for i, s in enumerate(SERVICES)}
N_SERVICES = len(SERVICES)

MAX_ZONES = 16          # zone one-hot width; topologies may use fewer
MAX_VULNS = 5           # vulnerability count is normalised by this

# ── canonical (control) definition, mirroring env_v2 exactly ─────────────────
CANONICAL_ZONES = ["Internet", "DMZ", "LAN", "User", "Admin"]
CANONICAL_HOSTS: List[Tuple[str, str, str, List[str], int, bool]] = [
    # (name, zone, node_type, services, n_vulns, is_critical)
    ("CorpDNS",          "Internet", "dns",       ["dns"],            1, False),
    ("PublicDNS",        "Internet", "dns",       ["dns"],            1, False),
    ("Attacker",         "Internet", "attacker",  [],                 0, False),
    ("DockerServer",     "DMZ",      "server",    ["http", "ssh"],    2, False),
    ("RepositoryServer", "DMZ",      "server",    ["https", "ssh"],   2, False),
    ("VideoServer",      "DMZ",      "server",    ["http"],           2, False),
    ("FileShare",        "LAN",      "fileshare", ["smb"],            1, True),
    ("AdminLAN",         "LAN",      "admin",     ["ssh", "rdp"],     1, False),
    ("Client",           "User",     "client",    ["http"],           1, False),
    ("AdminHost",        "Admin",    "admin",     ["rdp", "ssh"],     1, True),
]


@dataclass
class Host:
    hid: int
    name: str
    zone: int
    node_type: str
    services: List[str]
    n_vulns: int
    is_critical: bool
    is_entry: bool
    defender_owned: bool


@dataclass
class Topology:
    """An immutable, hashable network description."""
    name: str
    seed: Optional[int]
    zones: List[str]
    hosts: List[Host]
    zone_adj: List[List[int]]          # symmetric, zone-level reachability
    entry_zone: int
    n_agents: int
    agent_of_zone: Dict[int, int]      # defended zone -> owning agent index
    firewall_blocked: List[List[int]] = field(default_factory=list)
    config: Dict = field(default_factory=dict)

    # ── derived helpers ─────────────────────────────────────────────────────
    @property
    def n_zones(self) -> int:
        return len(self.zones)

    @property
    def n_hosts(self) -> int:
        return len(self.hosts)

    @property
    def defended_zones(self) -> List[int]:
        return sorted(self.agent_of_zone)

    def hosts_in_zone(self, z: int) -> List[Host]:
        return [h for h in self.hosts if h.zone == z]

    def zone_of_agent(self, a: int) -> List[int]:
        return [z for z, ag in self.agent_of_zone.items() if ag == a]

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["agent_of_zone"] = {str(k): v for k, v in self.agent_of_zone.items()}
        return d

    def content_hash(self) -> str:
        """Stable hash over the STRUCTURE (not the name), so two topologies with
        the same wiring hash equal regardless of what they are called."""
        d = self.to_dict()
        d.pop("name", None)
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:16]

    @staticmethod
    def from_dict(d: Dict) -> "Topology":
        hosts = [Host(**h) for h in d["hosts"]]
        return Topology(
            name=d["name"], seed=d["seed"], zones=d["zones"], hosts=hosts,
            zone_adj=d["zone_adj"], entry_zone=d["entry_zone"],
            n_agents=d["n_agents"],
            agent_of_zone={int(k): v for k, v in d["agent_of_zone"].items()},
            firewall_blocked=d.get("firewall_blocked", []),
            config=d.get("config", {}))


# ── construction ─────────────────────────────────────────────────────────────

def canonical_topology(n_agents: int = 4) -> Topology:
    """Reproduce env_v2's fixed 5-zone map. This is the CONTROL configuration.

    env_v2 routes every cross-zone move through a firewall hub: from Internet the
    attacker may enter any defended zone, and from a defended zone it may reach
    any other defended zone. The zone adjacency below encodes exactly that, so
    the entity environment's movement model reduces to env_v2._move() when run on
    this topology.
    """
    zid = {z: i for i, z in enumerate(CANONICAL_ZONES)}
    hosts = []
    for i, (nm, zn, nt, sv, nv, crit) in enumerate(CANONICAL_HOSTS):
        hosts.append(Host(hid=i, name=nm, zone=zid[zn], node_type=nt,
                          services=list(sv), n_vulns=nv, is_critical=crit,
                          is_entry=(nm == "Attacker"),
                          defender_owned=(zn != "Internet")))
    n = len(CANONICAL_ZONES)
    adj = [[0] * n for _ in range(n)]
    defended = [zid[z] for z in CANONICAL_ZONES if z != "Internet"]
    for a in defended:                       # firewall hub: defended <-> defended
        for b in defended:
            if a != b:
                adj[a][b] = 1
    for d in defended:                       # Internet -> every defended zone
        adj[zid["Internet"]][d] = adj[d][zid["Internet"]] = 1

    # one zone per agent, in the same order env_v2 uses (DEFENDED_ZONES)
    agent_of_zone = {z: i % n_agents for i, z in enumerate(defended)}
    return Topology(name="canonical_5zone", seed=None, zones=list(CANONICAL_ZONES),
                    hosts=hosts, zone_adj=adj, entry_zone=zid["Internet"],
                    n_agents=n_agents, agent_of_zone=agent_of_zone,
                    firewall_blocked=[],
                    config={"canonical": True, "n_zones": n})


def generate_topology(seed: int, n_zones: int = 5, hosts_per_zone: Tuple[int, int] = (1, 3),
                      n_agents: int = 4, p_firewall_block: float = 0.15,
                      n_critical: int = 1, name: Optional[str] = None) -> Topology:
    """Sample a valid topology deterministically from `seed`.

    n_zones counts the attacker's Internet zone, so n_zones=5 gives 4 defended
    zones -- matching the canonical control's shape while varying its wiring,
    host counts, services, and vulnerabilities.
    """
    if n_zones < 3:
        raise ValueError("n_zones must be >= 3 (Internet + at least 2 defended)")
    if n_zones > MAX_ZONES:
        raise ValueError(f"n_zones {n_zones} exceeds MAX_ZONES {MAX_ZONES}")
    # QMIX mixes a FIXED number of agents, so the agent count must stay constant
    # across every topology in an experiment. That forces n_agents <= defended
    # zones; otherwise some agent would own nothing, and its action mask would be
    # entirely invalid. Callers vary the number of ENTITIES, not of agents.
    if n_agents > n_zones - 1:
        raise ValueError(f"n_agents {n_agents} exceeds defended zones {n_zones - 1}; "
                         f"use n_zones >= n_agents + 1")
    rng = np.random.default_rng(seed)

    zones = ["Internet"] + [f"Zone{i}" for i in range(1, n_zones)]
    defended = list(range(1, n_zones))

    # ── zone graph: firewall hub, then remove some defended<->defended edges ──
    adj = [[0] * n_zones for _ in range(n_zones)]
    for a in defended:
        for b in defended:
            if a != b:
                adj[a][b] = 1
    for d in defended:
        adj[0][d] = adj[d][0] = 1

    blocked: List[List[int]] = []
    for i, a in enumerate(defended):
        for b in defended[i + 1:]:
            if rng.random() < p_firewall_block:
                # only block if the graph stays connected without it
                adj[a][b] = adj[b][a] = 0
                if _zone_connected(adj, 0, n_zones):
                    blocked.append([a, b])
                else:
                    adj[a][b] = adj[b][a] = 1      # restore: would disconnect

    # ── hosts ───────────────────────────────────────────────────────────────
    hosts: List[Host] = []
    hid = 0
    hosts.append(Host(hid=hid, name="Attacker", zone=0, node_type="attacker",
                      services=[], n_vulns=0, is_critical=False, is_entry=True,
                      defender_owned=False))
    hid += 1
    n_int = int(rng.integers(1, 3))                # extra Internet-side hosts
    for k in range(n_int):
        hosts.append(Host(hid=hid, name=f"ExtDNS{k}", zone=0, node_type="dns",
                          services=["dns"], n_vulns=int(rng.integers(0, 2)),
                          is_critical=False, is_entry=False, defender_owned=False))
        hid += 1

    defended_types = [t for t in NODE_TYPES if t != "attacker"]
    for z in defended:
        k = int(rng.integers(hosts_per_zone[0], hosts_per_zone[1] + 1))
        for j in range(k):
            nt = defended_types[int(rng.integers(0, len(defended_types)))]
            n_sv = int(rng.integers(1, 4))
            sv = sorted(rng.choice(N_SERVICES, size=n_sv, replace=False).tolist())
            hosts.append(Host(hid=hid, name=f"Z{z}H{j}", zone=z, node_type=nt,
                              services=[SERVICES[i] for i in sv],
                              n_vulns=int(rng.integers(0, MAX_VULNS + 1)),
                              is_critical=False, is_entry=False,
                              defender_owned=True))
            hid += 1

    # ── critical assets: only on defended hosts ─────────────────────────────
    cand = [h for h in hosts if h.defender_owned]
    n_crit = max(1, min(n_critical, len(cand)))
    for i in rng.choice(len(cand), size=n_crit, replace=False):
        cand[int(i)].is_critical = True

    agent_of_zone = {z: i % n_agents for i, z in enumerate(defended)}
    topo = Topology(name=name or f"gen_s{seed}_z{n_zones}", seed=seed, zones=zones,
                    hosts=hosts, zone_adj=adj, entry_zone=0, n_agents=n_agents,
                    agent_of_zone=agent_of_zone, firewall_blocked=blocked,
                    config={"canonical": False, "n_zones": n_zones,
                            "hosts_per_zone": list(hosts_per_zone),
                            "p_firewall_block": p_firewall_block,
                            "n_critical": n_critical})
    ok, problems = validate_topology(topo)
    if not ok:
        raise RuntimeError(f"generated invalid topology (seed={seed}): {problems}")
    return topo


# ── validation ───────────────────────────────────────────────────────────────

def _zone_connected(adj: Sequence[Sequence[int]], src: int, n: int) -> bool:
    seen, stack = {src}, [src]
    while stack:
        u = stack.pop()
        for v in range(n):
            if adj[u][v] and v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == n


def validate_topology(t: Topology) -> Tuple[bool, List[str]]:
    """Return (ok, problems). Every requirement is checked explicitly."""
    p: List[str] = []
    n = t.n_zones

    if not _zone_connected(t.zone_adj, t.entry_zone, n):
        p.append("zone graph is not connected from the entry zone")

    for i in range(n):
        if t.zone_adj[i][i] != 0:
            p.append(f"zone {i} has a self-loop")
        for j in range(n):
            if t.zone_adj[i][j] != t.zone_adj[j][i]:
                p.append(f"zone adjacency not symmetric at ({i},{j})")

    entries = [h for h in t.hosts if h.is_entry]
    if len(entries) != 1:
        p.append(f"expected exactly 1 entry host, found {len(entries)}")
    elif entries[0].zone != t.entry_zone:
        p.append("entry host is not in the entry zone")

    if not any(h.is_critical for h in t.hosts):
        p.append("no critical asset")
    if any(h.is_critical and not h.defender_owned for h in t.hosts):
        p.append("a critical asset is not defender-owned")

    for h in t.hosts:
        if not (0 <= h.zone < n):
            p.append(f"host {h.name} has out-of-range zone {h.zone}")
        if h.node_type not in NODE_TYPE_ID:
            p.append(f"host {h.name} has unknown node_type {h.node_type}")
        for s in h.services:
            if s not in SERVICE_ID:
                p.append(f"host {h.name} has unknown service {s}")
        if not (0 <= h.n_vulns <= MAX_VULNS):
            p.append(f"host {h.name} vuln count {h.n_vulns} out of range")

    if len({h.hid for h in t.hosts}) != len(t.hosts):
        p.append("duplicate host ids")

    for z in range(n):
        if not t.hosts_in_zone(z):
            p.append(f"zone {z} ({t.zones[z]}) contains no hosts (unreachable)")

    for a, b in t.firewall_blocked:
        if t.zone_adj[a][b]:
            p.append(f"firewall rule ({a},{b}) is blocked but the edge exists")

    defended = set(t.agent_of_zone)
    if t.entry_zone in defended:
        p.append("the attacker entry zone must not be defender-owned")
    if defended != set(range(n)) - {t.entry_zone}:
        p.append("agent_of_zone must cover exactly the non-entry zones")
    for z, a in t.agent_of_zone.items():
        if not (0 <= a < t.n_agents):
            p.append(f"zone {z} assigned to out-of-range agent {a}")
    owned = {a: t.zone_of_agent(a) for a in range(t.n_agents)}
    for a, zs in owned.items():
        if not zs:
            p.append(f"agent {a} owns no zone (its action mask would be empty)")

    return (len(p) == 0), p


# ── families & serialisation ─────────────────────────────────────────────────

def topology_family(seeds: Sequence[int], n_zones: int = 5, **kw) -> List[Topology]:
    return [generate_topology(seed=s, n_zones=n_zones, **kw) for s in seeds]


def save_topologies(topos: Sequence[Topology], path: str) -> None:
    payload = {"n": len(topos),
               "topologies": [{**t.to_dict(), "content_hash": t.content_hash()}
                              for t in topos]}
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)


def load_topologies(path: str) -> List[Topology]:
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    out = []
    for td in d["topologies"]:
        want = td.pop("content_hash", None)
        t = Topology.from_dict(td)
        if want is not None and t.content_hash() != want:
            raise ValueError(f"topology {t.name}: content hash mismatch "
                             f"({t.content_hash()} != {want})")
        out.append(t)
    return out


# ── self-test ────────────────────────────────────────────────────────────────

def _self_test() -> bool:
    ok = True
    print("=" * 84)
    print("  TEMARL v3 — TOPOLOGY GENERATOR SELF-TEST")
    print("=" * 84)

    c = canonical_topology()
    v, probs = validate_topology(c)
    print(f"  canonical: {c.n_zones} zones, {c.n_hosts} hosts, "
          f"{c.n_agents} agents, hash {c.content_hash()}")
    print(f"  canonical valid: {'PASS' if v else 'FAIL ' + str(probs)}")
    ok &= v

    # canonical must match env_v2's constants exactly
    import env_v2 as e2
    same_zones = c.zones == e2.ZONES
    same_def = c.defended_zones == sorted(e2.DEFENDED_ZONES)
    same_entry = c.entry_zone == e2.ATTACKER_ZONE
    same_agents = c.n_agents == e2.N_AGENTS
    same_map = all(c.agent_of_zone[z] == e2.ZONE_TO_AGENT[z]
                   for z in e2.DEFENDED_ZONES)
    same_hosts = all(sorted(h.name for h in c.hosts_in_zone(c.zones.index(z)))
                     == sorted(e2.ZONE_HOSTS[z]) for z in e2.ZONES)
    print(f"  matches env_v2 (zones/defended/entry/n_agents/map/hosts): "
          f"{same_zones}/{same_def}/{same_entry}/{same_agents}/{same_map}/{same_hosts}"
          f"   {'PASS' if all([same_zones, same_def, same_entry, same_agents, same_map, same_hosts]) else 'FAIL'}")
    ok &= all([same_zones, same_def, same_entry, same_agents, same_map, same_hosts])

    # determinism
    a, b = generate_topology(seed=7), generate_topology(seed=7)
    det = a.content_hash() == b.content_hash()
    diff = generate_topology(seed=8).content_hash() != a.content_hash()
    print(f"  determinism: same seed -> same hash {det}   "
          f"different seed -> different hash {diff}   "
          f"{'PASS' if det and diff else 'FAIL'}")
    ok &= det and diff

    # a spread of sizes, all valid
    bad = []
    for nz in (3, 4, 5, 6, 8, 10, 12):
        for s in range(6):
            t = generate_topology(seed=1000 * nz + s, n_zones=nz,
                                  n_agents=min(4, nz - 1))
            v2_, pr = validate_topology(t)
            if not v2_:
                bad.append((nz, s, pr))
    print(f"  42 topologies across 7 sizes all valid: "
          f"{'PASS' if not bad else 'FAIL ' + str(bad[:2])}")
    ok &= not bad

    # round-trip
    fam = topology_family(range(4), n_zones=6, n_agents=4)
    here = os.path.dirname(os.path.abspath(__file__))
    tmp = os.path.join(here, "results_v3", "_selftest_topologies.json")
    save_topologies(fam, tmp)
    back = load_topologies(tmp)
    rt = all(x.content_hash() == y.content_hash() for x, y in zip(fam, back))
    os.remove(tmp)
    print(f"  save/load round-trip preserves hashes: {'PASS' if rt else 'FAIL'}")
    ok &= rt

    print("=" * 84)
    print(f"  TOPOLOGY GENERATOR: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    print("=" * 84)
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="TEMARL v3 topology generator")
    ap.add_argument("--emit", metavar="PATH",
                    help="write a topology family to PATH (repo-relative ok)")
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--zones", type=int, default=5)
    args = ap.parse_args()
    if args.emit:
        fam = topology_family(args.seeds, n_zones=args.zones)
        save_topologies(fam, args.emit)
        print(f"wrote {len(fam)} topologies -> {args.emit}")
    else:
        raise SystemExit(0 if _self_test() else 1)
