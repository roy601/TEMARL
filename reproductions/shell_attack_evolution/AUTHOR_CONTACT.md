# Author contact log

No e-mail address is published in the paper, the repository or CITATION.cff. Corresponding authors:
Shichao Lv and Limin Sun (Institute of Information Engineering, CAS). Channel: an issue on
https://github.com/zyw-286/shell-attack-evolution-dataset, sent by the user (not sent by Claude).

| date | to | question (decision #) | reply or "no reply after N days" |
|---|---|---|---|
| (not sent yet) | repository issue | Q1–Q7 below | — |

## Draft (for the user to send)

> Thank you for releasing the data and code of "Unveiling Evolving Threats" (SRDS 2025). We are
> reproducing the paper's numbers from the released `dataset/` and would be grateful for six
> clarifications:
>
> 1. Table V, "Average Session Length" (12.65 / 5.00): the mean number of commands over all sessions,
>    or over session kinds / patterns? (decisions 5, 9)
> 2. Table V: how are "Session Kinds" (4,161 / 3,118), "Session pattern" (144 / 245) and "Number of
>    Session Patterns" (145 / 156) defined? (decisions 6–8)
> 3. Tables VI and VII: is a technique counted once per session (as Section IV.D says), once per
>    occurrence, or weighted by the number of commands ("command-weighted" in
>    `build_paper_tables.py`)? How are tactic shares derived from technique counts? (decisions 10, 11)
> 4. 2021–2022 sessions: Table I gives 5,365 and Table V 5,363. Which is final? (decision 4)
> 5. Table VIII is headed "2020–2021". Is this the 2021–2022 data? (inconsistency 3)
> 6. T1424 and T1655 are Mobile ATT&CK IDs, while Table VIII uses T1036. Were Enterprise T1057 and
>    T1036 intended? (inconsistency 4)
> 7. Running `analysis/period_2024/` on the released `2024/cowrie/` logs (commit d5f7fe1), step 07a
>    stops with `KeyError` for the pattern `('-o', ';', '>', '&&', 'cd', ';', '(', '/bin/busybox',
>    'echo', '-e', '||', 'echo', '-e', ')')`, and the read step loads 5,598,628 records against
>    3,914,173 in Table I. Which preprocessing happens before 07a, and could it be released? The
>    2021–2022 raw logs are also not in the repository. (REPORT_ROUTE_B.md)
