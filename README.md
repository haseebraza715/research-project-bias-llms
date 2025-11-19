# research-project-bias-llms

# LLM Bias Research Pipeline

Research-grade experiment pipeline for studying how LLMs respond to sensitive social topics, with a focus on antisemitism-related prompts.

## Overview

This pipeline systematically tests how different open-weight LLMs respond to antisemitism-related prompts across:
- **4 user profiles** (varying levels of exposure to biased narratives)
- **12 prompts** (covering definitions, scenarios, online discourse, policy, and AI responsibility)
- **2 system prompt conditions** (baseline vs. explicit neutrality instruction)
- **3 open-weight models** (Llama 3.1 8B, Mistral Small 24B, Qwen 2.5 7B)
- **N repetitions** (configurable)

## Models

The pipeline uses three open-weight instruction-tuned models via OpenRouter:

1. **Llama 3.1 8B Instruct** (`meta-llama/llama-3.1-8b-instruct`)
   - Meta's reference open LLM
   - 8B parameters, ~131k context

2. **Mistral Small 24B Instruct** (`mistralai/mistral-small-24b-instruct-2501:free`)
   - European open model (Apache 2.0)
   - 24B parameters, ~32k context
   - Free tier on OpenRouter

3. **Qwen 2.5 7B Instruct** (`qwen/qwen-2.5-7b-instruct`)
   - Alibaba's open model
   - 7B parameters, ~32k context
   - Strong multilingual support

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenRouter API key:**
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   ```
   
   Get your API key from [OpenRouter](https://openrouter.ai/keys).

3. **Configure experiment:**
   - Edit `config/settings.json` to adjust temperature, repetitions, etc.
   - Modify `config/profiles.json` and `config/prompts.json` as needed.

## Usage

Run the experiment:
```bash
python3 -m src.main
```

Results are written to `outputs/raw/` as JSONL files with timestamps.

## Output Format

Each line in the output JSONL contains:
- `run_id`: Unique identifier for this run
- `experiment_id`: Experiment identifier
- `model_id` & `model_name`: Model used
- `profile_id`: User profile identifier
- `prompt_id`: Prompt identifier
- `condition_id` & `condition_type`: System prompt condition
- `system_prompt_type`: "baseline" or "neutral"
- `repeat_index`: Repetition number
- `response_text`: Model's response
- `response_raw`: Raw API metadata (usage, model info, etc.)
- `timestamp_start` & `timestamp_end`: Timing information

## Privacy & Data Retention

For sensitive research content, consider using OpenRouter's Zero Data Retention (ZDR) endpoints where available. Check [OpenRouter's ZDR documentation](https://openrouter.ai/docs/zero-data-retention) for supported models.

## Research Design

This pipeline is designed for methods-appendable research:
- **Explicit system prompts** with safety constraints
- **Reproducible configuration** (all settings in JSON)
- **Complete logging** of experimental conditions
- **Open-weight models** for reproducibility and inspection

## License

Research use only. See individual model licenses for model-specific terms.

