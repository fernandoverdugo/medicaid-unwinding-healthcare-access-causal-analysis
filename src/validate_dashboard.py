from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "index.html"


def main():
    if not INDEX.exists():
        raise RuntimeError("Dashboard index.html was not generated.")

    content = INDEX.read_text(encoding="utf-8")

    required = [
        "Medicaid Unwinding & Healthcare Access",
        "Primary effect per +10 pp exposure",
        "Robustness results",
        "Pre-treatment diagnostics",
        "Event study",
        "Median state uninsured rate",
        "Final report",
        "Research design",
        "Robustness",
    ]

    missing = [text for text in required if text not in content]
    if missing:
        raise RuntimeError(
            "Dashboard is missing required content: "
            + ", ".join(missing)
        )

    if "−0.095" not in content and "-0.095" not in content:
        raise RuntimeError("Dashboard does not contain the primary estimate.")

    print("Dashboard validation passed.")


if __name__ == "__main__":
    main()
