# research-project-bias-llms

Research pipeline for studying LLM responses to sensitive social topics.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

## Usage

```bash
python3 -m src.main
```

Results are written to `outputs/raw/` as JSONL files.
