"""
Create compact JSONL views of experiment runs.

For each record, keep only:
- persona_id
- question_id
- model_id
- question_text
- response_text
"""

import json
from pathlib import Path
from typing import Dict, Any


def compact_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Return a compact view of a single run record."""
    persona_id = record.get("persona_id")
    question_id = record.get("question_id")
    model_id = record.get("model_id")

    qmeta = record.get("question_metadata", {})
    question_text = qmeta.get("text", "")

    response_text = record.get("response_text", "")

    return {
        "persona_id": persona_id,
        "question_id": question_id,
        "model_id": model_id,
        "question_text": question_text,
        "response_text": response_text,
    }


def compact_file(input_path: Path, output_path: Path) -> None:
    """Read input JSONL and write a compact JSONL file."""
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    count_in = 0
    count_out = 0

    with open(input_path, "r", encoding="utf-8") as fin, open(
        output_path, "w", encoding="utf-8"
    ) as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            count_in += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line {count_in}: {e}")
                continue

            compact = compact_record(record)
            fout.write(json.dumps(compact, ensure_ascii=False) + "\n")
            count_out += 1

    print(
        f"Compacted {count_out}/{count_in} records from {input_path} "
        f"into {output_path}"
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Create compact JSONL views of experiment runs."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input JSONL file (e.g., output/raw/trinity/four_by_four_runs.jsonl)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output compact JSONL file.",
    )

    args = parser.parse_args()
    compact_file(args.input, args.output)


if __name__ == "__main__":
    main()

