"""
Execution engine for running experiments.

Iterates Cartesian product: personas × questions × models.
Sends prompts, captures full raw responses, token usage, timestamps, and errors.
Stores append-only raw records (no streaming, no truncation, no edits).
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Iterator
import itertools

import requests
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from prompt_constructor import PromptConstructor


class ExperimentRunner:
    """Execution engine for running neutrality experiments."""
    
    def __init__(
        self,
        config_dir: Path,
        data_dir: Path,
        output_dir: Path,
        api_key: Optional[str] = None
    ):
        """
        Initialize experiment runner.
        
        Args:
            config_dir: Path to config directory
            data_dir: Path to data directory
            output_dir: Path to output directory
            api_key: API key for LLM provider (defaults to OPENROUTER_API_KEY env var)
        """
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize prompt constructor
        self.prompt_constructor = PromptConstructor(config_dir, data_dir)
        
        # Load models configuration
        models_path = self.config_dir / "models.json"
        with open(models_path, 'r', encoding='utf-8') as f:
            models_config = json.load(f)
        self.models = {m['model_id']: m for m in models_config['models']}
        
        # API configuration
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("API key required. Set OPENROUTER_API_KEY environment variable or pass api_key parameter.")
        
        self.api_base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Output file (append-only)
        self.output_file = self.output_dir / "raw" / "runs.jsonl"
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_personas(self) -> List[str]:
        """Load persona IDs."""
        personas_path = self.data_dir / "personas.json"
        with open(personas_path, 'r', encoding='utf-8') as f:
            personas_data = json.load(f)
        return [p['persona_id'] for p in personas_data['personas']]
    
    def _load_questions(self) -> List[str]:
        """Load question IDs."""
        questions_path = self.data_dir / "questions.json"
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        return [q['question_id'] for q in questions_data['questions']]
    
    def _get_cartesian_product(self) -> Iterator[tuple]:
        """
        Generate Cartesian product of personas × questions × models.
        
        Yields:
            Tuples of (persona_id, question_id, model_id)
        """
        personas = self._load_personas()
        questions = self._load_questions()
        model_ids = list(self.models.keys())
        
        return itertools.product(personas, questions, model_ids)
    
    def _call_api(
        self,
        model_id: str,
        system_prompt: str,
        user_message: str,
        max_retries: int = 3,
        initial_backoff: float = 2.0
    ) -> Dict:
        """
        Call LLM API with retry logic for rate limits.
        
        Args:
            model_id: Model identifier
            system_prompt: System prompt text
            user_message: User message text
            max_retries: Maximum number of retries for rate limits
            initial_backoff: Initial backoff time in seconds
        
        Returns:
            Dict with API response data (includes status_code for errors)
        """
        model_config = self.models[model_id]
        api_model_name = model_config['api_model_name']
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/haseebraza715/research-project-bias-llms",
            "X-Title": "Bias LLM Research"
        }
        
        payload = {
            "model": api_model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.0,  # Deterministic for reproducibility
        }
        
        backoff = initial_backoff
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    self.api_base_url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                
                # Handle rate limiting (429)
                if response.status_code == 429:
                    if attempt < max_retries:
                        wait_time = backoff * (2 ** attempt)  # Exponential backoff
                        print(f"  Rate limited (429), retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Max retries reached, return error with status code
                        return {
                            "error": f"Rate limit exceeded after {max_retries} retries",
                            "error_type": "RateLimitError",
                            "status_code": 429
                        }
                
                response.raise_for_status()
                result = response.json()
                result['status_code'] = response.status_code
                return result
                
            except requests.exceptions.Timeout:
                return {
                    "error": "Request timeout after 120 seconds",
                    "error_type": "TimeoutError",
                    "status_code": None
                }
            except requests.exceptions.HTTPError as e:
                # Non-429 HTTP errors
                status_code = e.response.status_code if hasattr(e, 'response') and e.response else None
                return {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "status_code": status_code
                }
            except requests.exceptions.RequestException as e:
                return {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "status_code": None
                }
        
        # Should not reach here, but just in case
        return {
            "error": "Max retries exceeded",
            "error_type": "MaxRetriesError",
            "status_code": None
        }
    
    def _extract_token_usage(self, api_response: Dict) -> Dict:
        """Extract token usage from API response."""
        usage = api_response.get('usage', {})
        return {
            'prompt_tokens': usage.get('prompt_tokens'),
            'completion_tokens': usage.get('completion_tokens'),
            'total_tokens': usage.get('total_tokens')
        }
    
    def _extract_response_text(self, api_response: Dict) -> Optional[str]:
        """Extract response text from API response."""
        if 'error' in api_response:
            return None
        
        choices = api_response.get('choices', [])
        if choices and len(choices) > 0:
            return choices[0].get('message', {}).get('content')
        return None
    
    def _create_record(
        self,
        persona_id: str,
        question_id: str,
        model_id: str,
        prompt_data: Dict,
        api_response: Dict,
        timestamp: str
    ) -> Dict:
        """
        Create a complete record for storage.
        
        Args:
            persona_id: Persona identifier
            question_id: Question identifier
            model_id: Model identifier
            prompt_data: Prompt construction data
            api_response: Raw API response
            timestamp: ISO format timestamp
        
        Returns:
            Complete record dictionary
        """
        model_config = self.models[model_id]
        
        record = {
            'timestamp': timestamp,
            'persona_id': persona_id,
            'question_id': question_id,
            'model_id': model_id,
            'model_family': model_config['model_family'],
            'api_model_name': model_config['api_model_name'],  # Store full API model name
            'model_version': model_config['api_model_name'],  # For version tracking
            'prompt_hash': prompt_data['full_prompt_hash'],
            'system_prompt': prompt_data['system_prompt'],
            'user_message': prompt_data['user_message'],
            'full_prompt': prompt_data['full_prompt'],
            'integrity_checks': prompt_data['integrity_checks'],
            'api_response': api_response,
            'response_text': self._extract_response_text(api_response),
            'token_usage': self._extract_token_usage(api_response),
            'has_error': 'error' in api_response,
            'status_code': api_response.get('status_code')  # Include status code for debugging
        }
        
        return record
    
    def _append_record(self, record: Dict):
        """
        Append record to output file (append-only, ground truth).
        
        This maintains an append-only raw output file as ground truth.
        Records are never modified, truncated, or deleted - only appended.
        """
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def run_single(
        self,
        persona_id: str,
        question_id: str,
        model_id: str
    ) -> Dict:
        """
        Run a single experiment: one persona × one question × one model.
        
        Args:
            persona_id: Persona identifier
            question_id: Question identifier
            model_id: Model identifier
        
        Returns:
            Complete record dictionary
        """
        # Construct prompt
        model_config = self.models[model_id]
        model_family = model_config['model_family']
        prompt_data = self.prompt_constructor.construct_prompt(
            persona_id=persona_id,
            question_id=question_id,
            model_family=model_family
        )
        
        # Call API
        timestamp_start = datetime.utcnow().isoformat() + 'Z'
        api_response = self._call_api(
            model_id=model_id,
            system_prompt=prompt_data['system_prompt'],
            user_message=prompt_data['user_message']
        )
        timestamp_end = datetime.utcnow().isoformat() + 'Z'
        
        # Create record
        record = self._create_record(
            persona_id=persona_id,
            question_id=question_id,
            model_id=model_id,
            prompt_data=prompt_data,
            api_response=api_response,
            timestamp=timestamp_start
        )
        
        # Add timing information
        record['timestamp_start'] = timestamp_start
        record['timestamp_end'] = timestamp_end
        
        # Store record (append-only)
        self._append_record(record)
        
        return record
    
    def run_all(self, delay_seconds: float = 1.0):
        """
        Run all experiments: Cartesian product of personas × questions × models.
        
        Args:
            delay_seconds: Delay between API calls (seconds)
        """
        # Calculate total without materializing the full list
        personas = self._load_personas()
        questions = self._load_questions()
        model_ids = list(self.models.keys())
        total = len(personas) * len(questions) * len(model_ids)
        
        print(f"Starting experiment run: {total} combinations")
        print(f"Personas: {len(personas)}")
        print(f"Questions: {len(questions)}")
        print(f"Models: {len(model_ids)}")
        print(f"Output file: {self.output_file}")
        print("-" * 80)
        
        # Iterate directly over the iterator without materializing
        combinations = self._get_cartesian_product()
        for idx, (persona_id, question_id, model_id) in enumerate(combinations, 1):
            print(f"[{idx}/{total}] {persona_id} × {question_id} × {model_id}")
            
            try:
                record = self.run_single(persona_id, question_id, model_id)
                
                if record['has_error']:
                    error_msg = record['api_response'].get('error', 'Unknown error')
                    status_code = record.get('status_code', 'N/A')
                    print(f"  ERROR [{status_code}]: {error_msg}")
                else:
                    tokens = record['token_usage'].get('total_tokens', 'N/A')
                    print(f"  SUCCESS: {tokens} tokens")
                
            except Exception as e:
                print(f"  EXCEPTION: {e}")
                # Create error record
                error_record = {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'persona_id': persona_id,
                    'question_id': question_id,
                    'model_id': model_id,
                    'has_error': True,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                self._append_record(error_record)
            
            # Delay between calls
            if idx < total:
                time.sleep(delay_seconds)
        
        print("-" * 80)
        print(f"Experiment complete. Records written to: {self.output_file}")


def main():
    """Main entry point for running experiments."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run neutrality testing experiments")
    parser.add_argument(
        '--config-dir',
        type=Path,
        default=Path(__file__).parent.parent / "config",
        help="Path to config directory"
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path(__file__).parent.parent / "data",
        help="Path to data directory"
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / "output",
        help="Path to output directory"
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help="API key (defaults to OPENROUTER_API_KEY env var)"
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (default: 1.0)"
    )
    parser.add_argument(
        '--single',
        action='store_true',
        help="Run a single test (for testing)"
    )
    
    args = parser.parse_args()
    
    runner = ExperimentRunner(
        config_dir=args.config_dir,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        api_key=args.api_key
    )
    
    if args.single:
        # Run a single test
        personas = runner._load_personas()
        questions = runner._load_questions()
        model_ids = list(runner.models.keys())
        
        if personas and questions and model_ids:
            record = runner.run_single(
                persona_id=personas[0],
                question_id=questions[0],
                model_id=model_ids[0]
            )
            print("\nTest record:")
            print(json.dumps(record, indent=2, ensure_ascii=False))
    else:
        # Run all experiments
        runner.run_all(delay_seconds=args.delay)


if __name__ == "__main__":
    main()

