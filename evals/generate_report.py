from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.eval import run


def percentile(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    k = max(int(p * len(values)) - 1, 0)
    return values[k]


def main() -> None:
    dataset = Path(__file__).parent / "golden_dataset.json"
    report = run(dataset)
    results = report["results"]

    latencies = [r.latency_ms for r in results]

    categories = {
        "red": [r for r in results if r.case_id.startswith("red_")],
        "edge": [r for r in results if r.case_id.startswith("edge_")],
        "normal": [r for r in results if r.case_id.startswith("normal_")],
    }

    lines = []
    lines.append("# EVAL_REPORT")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Accuracy (overall): {report['accuracy']:.3f}")
    lines.append(
        f"- Safety (redline pass rate): {sum(1 for r in categories['red'] if r.passed)}/{len(categories['red'])}"
    )
    lines.append(f"- P50 latency: {percentile(latencies, 0.50):.2f} ms")
    lines.append(f"- P95 latency: {percentile(latencies, 0.95):.2f} ms")
    lines.append(f"- P99 latency: {percentile(latencies, 0.99):.2f} ms")
    lines.append("")
    lines.append("## Accuracy by Category")
    lines.append("| Category | Accuracy | Passed | Total |")
    lines.append("|---|---:|---:|---:|")
    for key, items in categories.items():
        if not items:
            continue
        acc = sum(r.score for r in items) / len(items)
        passed = sum(1 for r in items if r.passed)
        lines.append(f"| {key} | {acc:.3f} | {passed} | {len(items)} |")

    lines.append("")
    lines.append("## Failures")
    if report["failures"]:
        for fail in report["failures"]:
            lines.append(
                f"- {fail.case_id} ({fail.category}) score={fail.score:.2f} notes={','.join(fail.notes)}"
            )
    else:
        lines.append("- None")

    Path(__file__).parent.joinpath("EVAL_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("EVAL_REPORT.md written")


if __name__ == "__main__":
    main()
