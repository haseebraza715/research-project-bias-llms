## Research Project: Bias in LLMs

Pipeline for running controlled neutrality experiments on LLMs and analyzing responses to sensitive social questions.

---

## Top-Level Layout

- **config/**: Model registry, system prompts, and JSON schemas.
- **data/**: Input personas and questions for the experiment grid.
- **docs/**: Design and planning notes for the pipeline.
- **output/**: Raw model runs and derived analysis tables.
- **scripts/**: Core execution, prompt construction, validation, and analysis logic.
- **tests/**: Unit tests for prompt integrity and detector behavior.
- **requirements.txt**: Python dependencies for the non-UI pipeline.

---

## Quickstart (Trinity Pilot)

From the project root:

- **Install dependencies**  
  - `pip install -r requirements.txt`

- **Validate inputs**  
  - `python -m scripts.validate_inputs`

- **Run a small Trinity-only pilot**  
  - `python -m scripts.run_experiment --four-by-four --delay 1.0`  
    (4 personas × 4 questions × 1 model, written to `output/raw/trinity/four_by_four_runs.jsonl`)

- **Create compact JSON for inspection**  
  - `python -m scripts.compact_runs --input output/raw/trinity/four_by_four_runs.jsonl --output output/raw/trinity/four_by_four_compact.jsonl`  
  - `python -m scripts.jsonl_to_array --input output/raw/trinity/four_by_four_compact.jsonl --output output/json/trinity_compact/four_by_four.json`

---

## `config/`

- **config/models.json**  
  Registry of LLMs used in experiments, including:
  - `model_id`: Short internal name.
  - `model_family`: Prompt family key (e.g., `generic`, `mistral`, `llama`).
  - `provider`: API provider (e.g., `openrouter`).
  - `api_model_name`: Fully qualified API model identifier.

- **config/prompts/system_prompts.json**  
  System prompts keyed by `model_family`.  
  Enforces:
  - Neutral, non-roleplay instructions.
  - Explicit prohibition on referencing persona metadata.

- **config/schemas/personas_schema.json**  
  JSON Schema for `data/personas.json`:
  - Requires a `personas` array.
  - Each persona has `persona_id`, `likert_scores`, and optional:
    - `country` (`HU`, `PL`, `CZ`, `SK`),
    - `dimension_profile` (`conspiratorial`, `secondary`, `new` as `low` / `medium` / `high`),
    - `sociodem` (age_group, gender, education, religiosity, political_trust, migration_attitude).
  - `likert_scores` are integers 1–5 with no extra properties.

- **config/schemas/questions_schema.json**  
  JSON Schema for `data/questions.json`:
  - Requires a `questions` array.
  - Each question has `question_id` and fixed `text`.
  - Optional metadata:
    - `type`: `direct` / `indirect` / `mirroring`.
    - `diagnostic_for`: `conspiratorial` / `secondary` / `new` / `mixed` / `none`.
  - Enforces uniqueness and immutability of question wording.

- **config/schemas/system_prompts_schema.json**  
  JSON Schema for `prompts/system_prompts.json`:
  - Keys are lowercase model-family names.
  - Values are non-empty system prompt strings.

---

## `data/`

- **data/personas.json**  
  List of user personas for the experiment:
  - Each `persona_id` encodes country and key traits (e.g., `HU_high_conspiratorial_old_low_edu`).
  - `country`, `dimension_profile`, and `sociodem` capture V4 country, PCA-based antisemitism dimensions, and sociodemographic/attitudinal attributes.
  - `likert_scores` include the canonical 5 antisemitism items plus additional PCA-inspired items, all scored 1–5.

- **data/questions.json**  
  Canonical list of experiment questions:
  - `question_id` such as `Q1_definition`, `Q2_stereotypes`, etc.
  - `text` contains the full immutable question wording.
  - Each question is tagged with `type` (`direct`, `indirect`, `mirroring`) and `diagnostic_for` (target dimension or `mixed` / `none`).

---

## `docs/`

- **docs/plan.md**  
  Design plan for the pipeline, covering:
  - Inputs and schemas.
  - Prompt assembly and integrity checks.
  - Execution engine over personas × questions × models.
  - Neutrality testing layer and output products.
  - Validation and testing strategy.

---

## `output/`

- **output/raw/runs.jsonl**  
  Append-only ground-truth log of all experiment runs:
  - One JSON record per persona × question × model.
  - Stores prompts, responses, token usage, timestamps, and error flags.
  - May also include `neutrality_analysis` if analysis has been applied in-place.

- **output/analysis/runs.csv**  
  Flattened table derived from `runs.jsonl`:
  - One row per run with key identifiers (persona, question, model).
  - Detector outputs (e.g., persona leakage, harmful-content flags).
  - Soft-signal metrics (hedging, certainty, moral language, prescriptive verbs).
  - Token usage fields to support cost and length analysis.

- **output/raw/trinity/**  
  Trinity-only small-grid runs (1×1, 2×2, 3×3, 4×4) for cost-controlled pilots.

- **output/json/trinity_compact/**  
  Compact JSON array views of Trinity runs (persona_id, question_id, model_id, question_text, response_text only), suitable for JSON viewers and sharing.

---

## `scripts/`

- **scripts/run_experiment.py**  
  Main execution engine for running neutrality experiments:
  - Uses `ExperimentRunner` to iterate personas × questions × models.
  - Builds prompts via `PromptConstructor`.
  - Calls the OpenRouter chat completions API with retry/backoff.
  - Writes append-only JSONL records to `output/raw/runs.jsonl`.
  - CLI supports:
    - Custom config/data/output paths, API key, and delay.
    - `--single` test mode (written to `output/raw/single_runs.jsonl`).
    - Small grids: `--pilot`, `--one-by-one`, `--two-by-two`, `--three-by-three`, `--four-by-four`.  
      These currently use a Trinity-only selector for free-tier experiments.

- **scripts/prompt_constructor.py**  
  Canonical prompt construction and integrity checking:
  - Loads system prompts, personas, and questions.
  - Formats a stable persona block including:
    - Sociodemographic summary (country, age_group, gender, education).
    - PCA-based dimension profile (conspiratorial / secondary / new).
    - Likert items in fixed order.
  - Builds user messages as persona block + question text.
  - Computes SHA-256 hashes for system prompts, questions, and full prompts.
  - Exposes `PromptConstructor.construct_prompt(...)` plus helper hash utilities.

- **scripts/detectors.py**  
  Neutrality-testing detectors and soft-signal analyzers:
  - Pattern-based detectors for persona leakage, roleplay adoption, refusals, and harmful content.
  - Word-based metrics for hedging, certainty, moral language, and prescriptive verbs.
  - Additional framing detectors:
    - Antisemitic framing (conspiracy/coded language).
    - Moral, epistemic, and political frame markers.
  - `analyze_response(...)` returns a structured summary of all detector and frame outputs for one response.

- **scripts/analyze_outputs.py**  
  Post-processing and analysis of experiment logs:
  - Loads records from `output/raw/runs.jsonl`.
  - Applies `analyze_response` to attach `neutrality_analysis` to each run.
  - Writes updated JSONL (optional) and creates a flattened CSV or Parquet table in `output/analysis/`.
  - CSV/Parquet tables include persona metadata (country, dimension_profile, sociodem) and question metadata (type, diagnostic_for) alongside detector metrics.
  - CLI flags control input path, output JSONL path, table path, and output format, plus an optional `--print-summary` that prints simple RQ-style summaries (e.g., hedging/certainty by dimension, harmful-content rates by question type).

- **scripts/validate_inputs.py**  
  Input validation helpers:
  - Checks `data/personas.json` for required Likert items and valid enum values for country, dimension levels, and sociodem fields.
  - Checks `data/questions.json` for non-empty text, unique IDs, and valid `type` / `diagnostic_for` values.
  - Verifies that `config/prompts/system_prompts.json` is a non-empty mapping of model families to prompt strings.

- **scripts/compact_runs.py**  
  Utility to create compact JSONL views of runs:
  - Keeps only `persona_id`, `question_id`, `model_id`, `question_text`, and `response_text`.
  - Used to produce the `*_compact.jsonl` files under `output/raw/trinity/`.

- **scripts/jsonl_to_array.py**  
  Helper to convert JSONL streams into JSON array files for easier viewing:
  - Turns `*_compact.jsonl` into `*.json` arrays under `output/json/trinity_compact/`.

- **scripts/test_openrouter_trinity.ps1**  
  PowerShell script for testing the OpenRouter Trinity endpoint:
  - Sends a single test request to `arcee-ai/trinity-large-preview:free`.
  - Logs status code and raw body to a text file for debugging API issues.

---

## `tests/`

- **tests/test_prompt_integrity.py**  
  Tests around prompt construction and integrity (hash stability, fixed ordering, and formatting).

- **tests/test_detectors.py**  
  Tests for the neutrality detectors and soft-signal metrics in `scripts/detectors.py`.

---

## Dependencies

- **requirements.txt**  
  Non-UI Python dependencies (currently `requests` for API calls).  
  Install with:
  - `pip install -r requirements.txt`

