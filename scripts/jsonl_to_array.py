"""
Convert JSONL files into JSON array files for easier viewing.

Many JSON viewers expect a single JSON value per file (often an array),
not a JSONL stream. This script reads a JSONL file (one JSON object per
line) and writes out a JSON array containing all those objects.
"""

import json
from pathlib import Path
from typing import Any, List


def jsonl_to_array(input_path: Path, output_path: Path) -> None:
    """Convert a JSONL file to a JSON array file."""
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    records: List[Any] = []
    count_in = 0
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            count_in += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line {count_in}: {e}")
                continue
            records.append(obj)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(
        f"Wrote {len(records)} records from JSONL {input_path} "
        f"into JSON array file {output_path}"
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert a JSONL file (one JSON object per line) "
        "into a JSON array file."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input JSONL file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output JSON array file.",
    )

    args = parser.parse_args()
    jsonl_to_array(args.input, args.output)


if __name__ == "__main__":
    main()

