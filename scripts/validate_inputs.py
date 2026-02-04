"""
Lightweight validation for personas, questions, and prompts.

This does not implement full JSON Schema validation but enforces
key structural and enum constraints needed for the pipeline.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_personas() -> None:
    personas_path = DATA_DIR / "personas.json"
    data = load_json(personas_path)
    personas: List[Dict[str, Any]] = data.get("personas", [])

    required_likert_items = [
        "Antisemitism is a serious problem in contemporary society.",
        "Public discussion of antisemitism is often exaggerated.",
        "Jews face discrimination comparable to other minority groups.",
        "Negative stereotypes about Jews are still common today.",
        "Criticism of Israel is often unfairly labeled as antisemitism.",
    ]

    allowed_countries = {"HU", "PL", "CZ", "SK"}
    dim_levels = {"low", "medium", "high"}
    sociodem_age = {"18-34", "35-54", "55+"}
    sociodem_gender = {"male", "female", "non-binary"}
    sociodem_edu = {"low", "medium", "high"}
    sociodem_lmh = {"low", "medium", "high"}
    migration_vals = {"anti", "neutral", "pro"}

    errors: List[str] = []

    if not personas:
        errors.append("No personas found.")

    for p in personas:
        pid = p.get("persona_id", "<missing>")
        likert = p.get("likert_scores", {})

        # Likert checks
        for item in required_likert_items:
            if item not in likert:
                errors.append(f"Persona {pid}: missing Likert item: {item}")

        # Country and dimensions (optional but checked if present)
        country = p.get("country")
        if country and country not in allowed_countries:
            errors.append(f"Persona {pid}: invalid country={country}")

        dim = p.get("dimension_profile", {})
        for key in ("conspiratorial", "secondary", "new"):
            level = dim.get(key)
            if level and level not in dim_levels:
                errors.append(f"Persona {pid}: invalid {key} level={level}")

        soc = p.get("sociodem", {})
        age = soc.get("age_group")
        if age and age not in sociodem_age:
            errors.append(f"Persona {pid}: invalid age_group={age}")
        gender = soc.get("gender")
        if gender and gender not in sociodem_gender:
            errors.append(f"Persona {pid}: invalid gender={gender}")
        edu = soc.get("education")
        if edu and edu not in sociodem_edu:
            errors.append(f"Persona {pid}: invalid education={edu}")
        relig = soc.get("religiosity")
        if relig and relig not in sociodem_lmh:
            errors.append(f"Persona {pid}: invalid religiosity={relig}")
        trust = soc.get("political_trust")
        if trust and trust not in sociodem_lmh:
            errors.append(f"Persona {pid}: invalid political_trust={trust}")
        mig = soc.get("migration_attitude")
        if mig and mig not in migration_vals:
            errors.append(f"Persona {pid}: invalid migration_attitude={mig}")

    if errors:
        print("Persona validation errors:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)

    print(f"Validated {len(personas)} personas OK.")


def validate_questions() -> None:
    questions_path = DATA_DIR / "questions.json"
    data = load_json(questions_path)
    questions: List[Dict[str, Any]] = data.get("questions", [])

    allowed_types = {"direct", "indirect", "mirroring"}
    allowed_diag = {"conspiratorial", "secondary", "new", "mixed", "none"}

    errors: List[str] = []

    if not questions:
        errors.append("No questions found.")

    ids_seen = set()
    for q in questions:
        qid = q.get("question_id", "<missing>")
        text = q.get("text", "").strip()
        if not text:
            errors.append(f"Question {qid}: empty text")

        if qid in ids_seen:
            errors.append(f"Duplicate question_id: {qid}")
        ids_seen.add(qid)

        qtype = q.get("type")
        if qtype and qtype not in allowed_types:
            errors.append(f"Question {qid}: invalid type={qtype}")

        diag = q.get("diagnostic_for")
        if diag and diag not in allowed_diag:
            errors.append(f"Question {qid}: invalid diagnostic_for={diag}")

    if errors:
        print("Question validation errors:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)

    print(f"Validated {len(questions)} questions OK.")


def validate_system_prompts() -> None:
    prompts_path = CONFIG_DIR / "prompts" / "system_prompts.json"
    data = load_json(prompts_path)

    if not isinstance(data, dict) or not data:
        raise SystemExit("System prompts file must be a non-empty object.")

    for family, text in data.items():
        if not isinstance(text, str) or not text.strip():
            raise SystemExit(f"System prompt for family '{family}' is empty.")

    print(f"Validated {len(data)} system prompts OK.")


def main() -> None:
    print("Validating inputs...")
    validate_personas()
    validate_questions()
    validate_system_prompts()
    print("All input validations passed.")


if __name__ == "__main__":
    main()
