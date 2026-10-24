# PDF — session papers

Readable write-ups of what happened in a working session, for understanding
rather than for the thesis text itself.

## Naming

```
YYYY-MM-DD_<Topic>_<Language>.pdf
```

e.g. `2026-10-24_CAMLDS_Session_Bangla.pdf`

## Contents

| File | What it covers |
|---|---|
| `2026-10-24_CAMLDS_Session_Bangla.pdf` | Using the real CAM-LDS release: playbooks vs logs, the audit, the verification that overturned four of my claims, the extractor, and the split decision. In Bangla. |

## How these are made

HTML written to the scratchpad, rendered with headless Chrome:

```bash
chrome --headless --disable-gpu --no-pdf-header-footer \
       --print-to-pdf="PDF/<name>.pdf" "file:///<path>.html"
```

Bangla needs `font-family: 'Nirmala UI', 'Kalpurush', sans-serif` — both ship
with Windows. Always screenshot the HTML and look at it before trusting the
PDF; a missing font fails silently as boxes.

## Rule

Every number in these papers is verified against a file or a published record
at the time of writing. Where something is carried over rather than verified,
the paper says so. They are explanations, not claims.
