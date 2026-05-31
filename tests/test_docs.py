"""Documentation health checks."""

from pathlib import Path

DOC_FILES = [
    "README.md",
    "README-zh.md",
    "AI_GUIDE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "docs/live-testing.md",
    "docs/api-compatibility.md",
]
MOJIBAKE_MARKERS = ["鈥", "涓", "骞", "鍙", "鐨", "鑷", "閰"]


def test_docs_are_utf8_without_common_mojibake() -> None:
    for file_name in DOC_FILES:
        text = Path(file_name).read_text(encoding="utf-8")
        markers = [marker for marker in MOJIBAKE_MARKERS if marker in text]
        assert not markers, f"{file_name} contains possible mojibake markers: {markers}"
