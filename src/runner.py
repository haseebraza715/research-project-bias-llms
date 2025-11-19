import json
import uuid
from datetime import datetime
from pathlib import Path
from .config_loader import load_profiles, load_prompts, load_settings
from .models import generate_response

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso():
    return datetime.utcnow().isoformat()


def run_experiment():
    profiles = load_profiles()
    prompts = load_prompts()
    settings = load_settings()

    experiment_id = settings["experiment_id"]
    models = settings["models"]
    temperature = settings["temperature"]
    n_repeats = settings["n_repeats"]
    conditions = settings["conditions"]
    base_system_prompt = settings["base_system_prompt"]
    neutral_system_prompt = settings["neutral_system_prompt"]

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"{experiment_id}_{timestamp}.jsonl"

    total_runs = len(models) * len(profiles) * len(prompts) * len(conditions) * n_repeats
    print(f"Starting experiment: {experiment_id}")
    print(f"Total runs: {total_runs}")
    print(f"Models: {[m['model_id'] for m in models]}")
    print(f"Output: {output_path}\n")

    run_count = 0

    with open(output_path, "w", encoding="utf-8") as out_f:
        for model_cfg in models:
            model_id = model_cfg["model_id"]
            model_name = model_cfg["name"]

            print(f"Processing model: {model_id} ({model_name})")

            for profile in profiles:
                for prompt in prompts:
                    for cond in conditions:
                        for repeat_idx in range(n_repeats):
                            run_id = str(uuid.uuid4())
                            run_count += 1

                            # choose system prompt
                            use_neutral = cond["use_neutral_system_prompt"]
                            system_prompt = (
                                neutral_system_prompt if use_neutral else base_system_prompt
                            )

                            # build user content
                            user_content = (
                                f"{profile['background_text']}\n\n"
                                f"Question: {prompt['text']}"
                            )

                            # call model
                            start_time = _now_iso()
                            try:
                                response = generate_response(
                                    model_name=model_name,
                                    system_prompt=system_prompt,
                                    user_content=user_content,
                                    temperature=temperature,
                                    seed=None,  # optional, if supported
                                )
                                end_time = _now_iso()

                                record = {
                                    "run_id": run_id,
                                    "experiment_id": experiment_id,
                                    "timestamp_start": start_time,
                                    "timestamp_end": end_time,
                                    "model_id": model_id,
                                    "model_name": model_name,
                                    "profile_id": profile["profile_id"],
                                    "prompt_id": prompt["prompt_id"],
                                    "condition_id": cond["condition_id"],
                                    "condition_type": cond["type"],
                                    "use_neutral_system_prompt": use_neutral,
                                    "repeat_index": repeat_idx,
                                    "system_prompt_type": "neutral" if use_neutral else "baseline",
                                    "response_text": response.get("text"),
                                    "response_raw": response.get("raw", None),
                                }

                                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                                out_f.flush()  # Ensure data is written immediately

                                if run_count % 10 == 0:
                                    print(f"  Completed {run_count}/{total_runs} runs...")

                            except Exception as e:
                                end_time = _now_iso()
                                error_record = {
                                    "run_id": run_id,
                                    "experiment_id": experiment_id,
                                    "timestamp_start": start_time,
                                    "timestamp_end": end_time,
                                    "model_id": model_id,
                                    "model_name": model_name,
                                    "profile_id": profile["profile_id"],
                                    "prompt_id": prompt["prompt_id"],
                                    "condition_id": cond["condition_id"],
                                    "condition_type": cond["type"],
                                    "use_neutral_system_prompt": use_neutral,
                                    "repeat_index": repeat_idx,
                                    "system_prompt_type": "neutral" if use_neutral else "baseline",
                                    "error": str(e),
                                    "response_text": None,
                                    "response_raw": None,
                                }
                                out_f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
                                out_f.flush()
                                print(f"  ERROR in run {run_id}: {e}")

    print(f"\nExperiment completed. Results written to: {output_path}")
    print(f"Total runs: {run_count}/{total_runs}")

