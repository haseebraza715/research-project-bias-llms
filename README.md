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
  - Each persona has `persona_id` and `likert_scores`.
  - `likert_scores` are integers 1–5 with no extra properties.

- **config/schemas/questions_schema.json**  
  JSON Schema for `data/questions.json`:
  - Requires a `questions` array.
  - Each question has `question_id` and fixed `text`.
  - Enforces uniqueness and immutability of question wording.

- **config/schemas/system_prompts_schema.json**  
  JSON Schema for `prompts/system_prompts.json`:
  - Keys are lowercase model-family names.
  - Values are non-empty system prompt strings.

---

## `data/`

- **data/personas.json**  
  List of user personas for the experiment:
  - Each `persona_id` encodes concern level (e.g., `P1_low_concern`).
  - `likert_scores` map fixed antisemitism-related statements to 1–5 scores.

- **data/questions.json**  
  Canonical list of experiment questions:
  - `question_id` such as `Q1_definition`, `Q2_stereotypes`, etc.
  - `text` contains the full immutable question wording.

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

---

## `scripts/`

- **scripts/run_experiment.py**  
  Main execution engine for running neutrality experiments:
  - Uses `ExperimentRunner` to iterate personas × questions × models.
  - Builds prompts via `PromptConstructor`.
  - Calls the OpenRouter chat completions API with retry/backoff.
  - Writes append-only JSONL records to `output/raw/runs.jsonl`.
  - CLI supports custom config/data/output paths, API key, delay, and a `--single` test mode.

- **scripts/prompt_constructor.py**  
  Canonical prompt construction and integrity checking:
  - Loads system prompts, personas, and questions.
  - Formats persona Likert scores in a fixed, ordered metadata block.
  - Builds user messages as persona block + question.
  - Computes SHA-256 hashes for system prompts, questions, and full prompts.
  - Exposes `PromptConstructor.construct_prompt(...)` plus helper hash utilities.

- **scripts/detectors.py**  
  Neutrality-testing detectors and soft-signal analyzers:
  - Pattern-based detectors for persona leakage, roleplay adoption, refusals, and harmful content.
  - Word-based metrics for hedging, certainty, moral language, and prescriptive verbs.
  - `analyze_response(...)` returns a structured summary of all detector outputs for one response.

- **scripts/analyze_outputs.py**  
  Post-processing and analysis of experiment logs:
  - Loads records from `output/raw/runs.jsonl`.
  - Applies `analyze_response` to attach `neutrality_analysis` to each run.
  - Writes updated JSONL (optional) and creates a flattened CSV or Parquet table in `output/analysis/`.
  - CLI flags control input path, output JSONL path, table path, and output format.

- **scripts/validate_inputs.py**  
  Reserved for input validation helpers (currently empty; no runtime logic implemented yet).

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

