## Plan — PCA-Integrated Neutrality Pipeline

## 1. Overview of Integrations

- **PCA-derived antisemitism dimensions**  
  - Integrate three dimensions from the 2022 survey: `conspiratorial`, `secondary`, and `new` antisemitism.
  - Encode these as qualitative levels (`low` / `medium` / `high`) in persona `dimension_profile` objects.
  - Ensure personas combine dimensions in realistic patterns, including baselines with mostly neutral scores.

- **Country context (V4 countries)**  
  - Treat `HU`, `PL`, `CZ`, and `SK` as separate contexts via a `country` field on personas.
  - Allow later grouping and comparison of responses by country for cross-national patterns.

- **Sociodemographic and attitudinal attributes**  
  - Add a `sociodem` block per persona with:
    - `age_group`, `gender`, `education`.
    - `religiosity`, `political_trust`, `migration_attitude`.
  - Use these attributes both in persona text blocks and in downstream analysis (e.g., RQ5, RQ6).

- **Research questions (RQ1–RQ7)**  
  - RQ1, RQ2, RQ5, RQ6 focus on how persona dimensions and sociodem attributes shape responses (user-driven variation).
  - RQ3 and RQ4 require carefully tagged prompts (direct vs. indirect, diagnostic questions, co-activation).
  - RQ7 requires repeated runs for the same (persona, question, model) triples to study consistency.

- **Cost and pilot considerations**  
  - Emphasize a **small pilot grid** (e.g., 5 personas × 5 questions × 2 models, 3 repeats) to test design and detectors.
  - Use a `--pilot` flag in `scripts/run_experiment.py` to restrict combinations and log to a dedicated pilot file.
  - Keep everything compatible with free OpenRouter models (current config uses Mistral-family, Qwen, etc.; ChatGPT can be added later when feasible).

---

## 2. Step-by-Step Execution Plan

1. **Schema extensions (backward compatible)**
   - Update `config/schemas/personas_schema.json` to allow optional fields:
     - `country` (enum: `HU`, `PL`, `CZ`, `SK`).
     - `dimension_profile` (object with `conspiratorial`, `secondary`, `new` set to `low` / `medium` / `high`).
     - `sociodem` (object with structured sociodem attributes).
   - Update `config/schemas/questions_schema.json` to allow optional fields:
     - `type` (`direct` / `indirect` / `mirroring`).
     - `diagnostic_for` (`conspiratorial` / `secondary` / `new` / `mixed` / `none`).
   - Keep existing structure valid so earlier minimal datasets still pass.

2. **Persona data expansion**
   - Expand `data/personas.json` to ~20–30 personas across `HU`, `PL`, `CZ`, `SK`.
   - For each persona:
     - Set `persona_id` to encode country and key traits (e.g., `HU_high_conspiratorial_old_low_edu`).
     - Provide `country`, `dimension_profile`, and `sociodem` blocks.
     - Keep existing Likert items required by the pipeline, but extend `likert_scores` to 10–15 items (including survey-inspired antisemitism items and neutral baselines).
   - Ensure coverage of combinations needed for RQ5 (dimension × sociodem interactions).

3. **Question data expansion and tagging**
   - Extend `data/questions.json` to ~20–30 questions.
   - For each question:
     - Maintain immutable `text` wording.
     - Assign `type` (`direct`, `indirect`, `mirroring`) to support RQ4.
     - Set `diagnostic_for` to target PCA dimensions or co-activation patterns (RQ3).
   - Include explicit antisemitism questions, indirect conspiratorial frames, and mirroring formulations.

4. **Prompt construction refinements**
   - Update `scripts/prompt_constructor.py`:
     - Incorporate `country` and `sociodem` into the persona block in a natural but stable template.
     - Preserve fixed Likert item ordering and existing hash-based integrity checks.
     - Keep system prompts forbidding the model from referencing persona metadata explicitly.

5. **Detector and framing extensions**
   - Update `scripts/detectors.py`:
     - Add keyword-based frame detectors for **moral**, **epistemic**, and **political** framing.
     - Extend antisemitic framing patterns (conspiracy and stereotype language) separate from general harmful content.
     - Return a richer `neutrality_analysis` structure, keeping older keys intact for backward compatibility.

6. **Analysis enhancements**
   - Update `scripts/analyze_outputs.py`:
     - Ensure persona metadata (country, dimension_profile, sociodem) is present in records via `run_experiment.py`.
     - Extend CSV/Parquet tables with persona-level columns.
     - Compute simple descriptive stats:
       - RQ1/RQ2: distributions of hedging, certainty, frames by PCA dimension levels.
       - RQ3/RQ4: counts of diagnostic items and co-activation patterns by question `type` and `diagnostic_for`.
       - RQ5/RQ6: comparisons of metrics across sociodem groups and models.
       - RQ7: variance and range across repeated runs for the same (persona, question, model).

7. **Pilot mode for experiments**
   - Update `scripts/run_experiment.py`:
     - Add a `--pilot` flag to run a restricted grid (e.g., 5 personas × 5 questions × 2 models, 3 repeats).
     - Write pilot runs to `output/raw/pilot_runs.jsonl` (append-only, same record structure).
     - Allow selection of representative personas and questions that span PCA dimensions and sociodem space.

8. **Validation and testing**
   - Implement `scripts/validate_inputs.py`:
     - Load schemas and data, verify structural validity and allowed enum values.
     - Check for missing Likert items, inconsistent dimension labels, and question tags.
   - Extend tests in `tests/` where needed (e.g., detector behavior, stability of persona formatting).
   - Run `python -m scripts.validate_inputs` and `pytest` before and after pilot configuration changes.

---

## 3. Pilot Testing Approach

- **Pilot grid design**
  - Select ~5 personas spanning:
    - Different countries (at least 3 of `HU`, `PL`, `CZ`, `SK`).
    - Different dimension profiles (e.g., high vs. low conspiratorial; contrasting secondary/new levels).
    - Contrasting sociodem traits (age groups, education, migration attitudes).
  - Select ~5 questions:
    - Mix of direct, indirect, and mirroring types.
    - Cover each PCA dimension at least once; include one co-activation item.
  - Use 2 representative models from `config/models.json` (e.g., one Mistral-family, one Qwen-family) for the pilot.

- **Execution**
  - Run:
    - `python -m scripts.validate_inputs`
    - `python -m scripts.run_experiment --pilot --delay 1.0`
    - `python -m scripts.analyze_outputs --input output/raw/pilot_runs.jsonl --output-table output/analysis/pilot_runs.csv`
  - Inspect a small sample of raw records and analysis rows for:
    - Correct persona text blocks (country + sociodem + Likert items).
    - Reasonable detector and frame outputs.
    - Acceptable refusal rates and token usage (cost and time checks).

- **Manual checks**
  - Spot-check responses for:
    - Expected shifts with high vs. low dimension profiles (RQ1, RQ5).
    - Presence of moral, epistemic, or political framing in line with persona cues (RQ2).
    - Differences between direct vs. indirect/mirroring questions (RQ3, RQ4).
    - Stability across repeated runs for the same configuration (RQ7).

---

## 4. How Changes Support Each RQ

- **RQ1 — PCA dimensions vs. baseline (user-driven)**  
  - Persona `dimension_profile` encodes conspiratorial/secondary/new antisemitism levels.
  - Analysis groups responses by these levels (e.g., high vs. low) and compares hedging, certainty, and harmful-content flags.

- **RQ2 — Dimensions activating moral/epistemic/political frames (user-driven)**  
  - Frame detectors in `scripts/detectors.py` tag responses with moral, epistemic, and political markers.
  - Analysis inspects frame frequencies by dimension levels to see which dimensions drive which framing styles.

- **RQ3 — Diagnostic questions and co-activations (prompt-driven)**  
  - `questions.json` adds `type` and `diagnostic_for` fields to label diagnostic and co-activation prompts.
  - Analysis aggregates detector outputs and frames by these labels to identify which prompts most cleanly separate or co-activate dimensions.

- **RQ4 — Indirect vs. direct questions and mirroring (prompt-driven)**  
  - Question `type` (`direct`, `indirect`, `mirroring`) allows direct comparison of framing and harmful-content flags across question styles.
  - Repeated questions within the same dimension profile support detecting mirroring or soft alignment in indirect/mirroring forms.

- **RQ5 — Dimensions × sociodem/attitudinal attributes (user-driven)**  
  - Persona `sociodem` attributes enable cross-tabulation of dimensions with age, gender, education, religiosity, trust, and migration attitudes.
  - Analysis compares metrics (e.g., harmful-content flags, hedging) across these intersections.

- **RQ6 — LLM type influence on RQ5 (data-driven)**  
  - Model identifiers and families in `config/models.json` are preserved in all records.
  - Analysis compares RQ5-style metrics across model families (e.g., Mistral vs. Qwen; ChatGPT can be added later) for the same persona-question combinations.

- **RQ7 — Response consistency across repeats**  
  - `run_experiment.py`’s pilot mode includes repeated runs for fixed (persona, question, model).
  - Analysis computes basic variability measures (e.g., distribution of frames, hedging, harmful-content flags) across repeats to identify factors reducing consistency.

