# Sources

Every input of the reproduction, where it comes from and why it is the right copy.
All links were checked on 2026-11-02. `download.py` fetches the **auto** ones;
`reference/REFERENCE_MANIFEST.json` holds their SHA-256 as fetched on the dev machine.

## The paper

| | |
|---|---|
| Citation | Kuwano M., Okuma M., Okada S., Mitsunaga T. "The Attacker Might Also Do Next: ATT&CK Behavior Forecasting by Attacker-based Collaborative Filtering and Graph Databases." *J. Information Processing* 31, 802–811, Dec. 2023 |
| DOI | `10.2197/ipsjjip.31.802` |
| Landing page | https://www.jstage.jst.go.jp/article/ipsjjip/31/0/31_802/_article |
| PDF (auto) | https://www.jstage.jst.go.jp/article/ipsjjip/31/0/31_802/_pdf/-char/en |
| Code | **None released.** The paper has no repository or code link. The method is Algorithm 1 (p. 806). |
| Preliminary version | Kuwano et al., ICOCO 2022, pp. 191–197, DOI `10.1109/ICOCO56118.2022.10032036` (IEEE, paywalled). Only needed to reproduce their *baseline* curves (kNN, k = 40), which appear in Figs. 9–11 only. Optional. |

## Training data: MITRE ATT&CK Enterprise (STIX 2.0)

The paper says ATT&CK v11 (April 25, 2022), 133 groups, 191 techniques, but cites the
website accessed 2023-01-31, when v12.1 was live. So three versions are fetched: the one
named, and two for sensitivity. Pinned by git tag in MITRE's official repository, so the
bytes do not change.

| id | Version | URL (auto) |
|---|---|---|
| `attack_v11.0` | **v11.0, primary** | https://raw.githubusercontent.com/mitre/cti/ATT%26CK-v11.0/enterprise-attack/enterprise-attack.json |
| `attack_v11.3` | v11.3, last v11 patch | https://raw.githubusercontent.com/mitre/cti/ATT%26CK-v11.3/enterprise-attack/enterprise-attack.json |
| `attack_v12.1` | v12.1, live at access date | https://raw.githubusercontent.com/mitre/cti/ATT%26CK-v12.1/enterprise-attack/enterprise-attack.json |

Repository: https://github.com/mitre/cti (tags `ATT&CK-v11.0` … `ATT&CK-v12.1`).
STIX 2.1 mirror, same content, not used: https://github.com/mitre-attack/attack-stix-data

## Test data: three CISA advisories

The **primary** copies are Internet Archive snapshots taken closest to the paper's access
date (2023-01-31). The `id_` form of the URL returns the page exactly as archived, without
the Wayback toolbar. Each advisory's "Last Revised" date is before 2023-01-31, so the
current page should match the snapshot; the audit checks that.

| Advisory | Title | Paper uses | Last revised | Primary (auto) |
|---|---|---|---|---|
| AA22-277A | Impacket and Exfiltration Tool Used to Steal Sensitive Information from Defense Industrial Base Organization | 26 techniques | 2022-10-05 | http://web.archive.org/web/20230129215752id_/https://www.cisa.gov/uscert/ncas/alerts/aa22-277a |
| AA22-138B | Threat Actors Chaining Unpatched VMware Vulnerabilities for Full System Control | 13 listed, 12 used | 2022-06-02 | http://web.archive.org/web/20230129001025id_/https://www.cisa.gov/uscert/ncas/alerts/aa22-138b |
| AA22-174A | Malicious Cyber Actors Continue to Exploit Log4Shell in VMware Horizon Systems | 13 techniques | 2022-07-18 | http://web.archive.org/web/20230201002818id_/https://www.cisa.gov/uscert/ncas/alerts/aa22-174a |

**Manual cross-checks.** cisa.gov answers scripted requests with HTTP 403. Open each link
in a browser and save it at the path `download.py` prints (`data/raw/<id>/<file>`), then
rerun `download.py` so it is hashed into the manifest.

| id | URL |
|---|---|
| `cisa_aa22-277a_live` | https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-277a |
| `cisa_aa22-138b_live` | https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-138b |
| `cisa_aa22-174a_live` | https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-174a |
| `cisa_aa22-277a_pdf` | https://www.cisa.gov/sites/default/files/publications/aa22-277a-impacket-and-exfiltration-tool-used-to-steal-sensitive-information-from-defense-industrial-base-organization.pdf |
| `cisa_aa22-138b_pdf` | https://www.cisa.gov/sites/default/files/publications/AA22-138B_Threat_Actors_Chaining_VMware_Unpatched_Vulnerabilities_for_Full_System_Control.pdf |
| `cisa_aa22-174a_pdf` | https://www.cisa.gov/sites/default/files/publications/AA22-174A_Joint_CSA_Malicious_Cyber_Actors_Exploiting_Log4Shell_in_Unpatched_VMware_Horizon_Systems_FINAL.pdf |
| `cisa_aa22-138b_stix` | https://www.cisa.gov/sites/default/files/publications/AA22-138B.stix.xml |
| `cisa_aa22-174a_stix` | https://www.cisa.gov/sites/default/files/publications/AA22-174A.stix.xml |

AA22-277A has no advisory-level STIX file; its page links only malware-analysis STIX
(MAR-10365227), which is not needed.

## The reproduction target

`paper/tables_5_7.csv`: the paper's Tables 5–7 (TP/FP/TN/FN at every input count, all
three advisories, 48 rows), typed in from the PDF. Checked by script against the PDF text:
0 mismatches. Every row also satisfies Prediction = TP + FP and TP + FN = N − input
(N = 26, 12, 13).
