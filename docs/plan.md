# Task 1 Plan — Neutrality-Testing Script

## Actionable Steps

1. **Define inputs and schemas**
   - Create JSON schema for personas (ID + Likert items + numeric scores).
   - Create a fixed question list file (immutable ordering, wording, punctuation).
   - Create model pre-prompt registry (per model family, version-controlled).

2. **Implement prompt assembly and integrity checks**
   - Build canonical prompt constructor: system pre-prompt + user block (persona metadata block + question text only).
   - Enforce strict persona formatting and fixed Likert ordering.
   - Compute and store prompt hash; verify pre-prompt and question byte identity.

3. **Execution engine**
   - Iterate Cartesian product: personas × questions × models.
   - Send prompts, capture full raw responses, token usage, timestamps, and errors.
   - Store append-only raw records (no streaming, no truncation, no edits).

4. **Neutrality testing layer (post-generation)**
   - Implement detectors: persona leakage, roleplay adoption, safety flag.
   - Compute soft signals: hedging frequency, certainty markers, moral language intensity, prescriptive verbs.

5. **Output products**
   - Maintain append-only raw output file as ground truth.
   - Optionally generate flattened analysis table (CSV/Parquet) with one row per run.

6. **Validation tests**
   - Structural checks: identical prompts for identical inputs; stable formatting; no hidden randomness.
   - Behavioral checks: detectors trigger on known examples; logging completeness.

## Directory Structure

```
.
├── docs/
│   └── plan.md
├── config/
│   ├── models.json
│   └── prompts/
│       └── system_prompts.json
├── data/
│   ├── personas.json
│   └── questions.json
├── output/
│   ├── raw/
│   │   └── runs.jsonl
│   └── analysis/
│       └── runs.csv
├── scripts/
│   ├── run_experiment.py
│   ├── validate_inputs.py
│   └── analyze_outputs.py
└── tests/
    ├── test_prompt_integrity.py
    └── test_detectors.py
```
