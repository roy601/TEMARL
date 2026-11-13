"""Plain ASCII summary shared by all dataset reports."""
import statistics


def summary_box(lengths, vocabulary_size):
    count = len(lengths)
    long_count = sum(n > 16 for n in lengths)
    rows = [
        ("Total sequences:", str(count)),
        ("Average length:", f"{statistics.mean(lengths) if lengths else 0:.1f}"),
        ("Median length:", f"{statistics.median(lengths) if lengths else 0:.1f}"),
        ("Min length:", str(min(lengths, default=0))),
        ("Max length:", str(max(lengths, default=0))),
        ("Std-dev length:", f"{statistics.pstdev(lengths) if lengths else 0:.1f}"),
        ("Sequences > 16 techniques:", f"{long_count} ({100 * long_count / count if count else 0:.1f}%)"),
        ("Technique vocabulary:", str(vocabulary_size)),
    ]
    body = [f"  {label:<29} {value:>14}  " for label, value in rows]
    width = max(49, *(len(row) for row in body))
    border = "+" + "-" * width + "+"
    return "\n".join([border, "|" + "SUMMARY METRICS".center(width) + "|", border,
                      *("|" + row.ljust(width) + "|" for row in body), border])
