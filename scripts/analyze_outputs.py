"""
Analyze experiment outputs and apply neutrality testing layer.

Reads raw JSONL records, applies detectors and soft signal analysis,
and optionally generates flattened analysis table.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import csv

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from detectors import analyze_response


def load_jsonl_records(filepath: Path) -> List[Dict]:
    """
    Load records from JSONL file.
    
    Args:
        filepath: Path to JSONL file
    
    Returns:
        List of record dictionaries
    """
    records = []
    if not filepath.exists():
        return records
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON line: {e}")
                    continue
    
    return records


def analyze_record(record: Dict) -> Dict:
    """
    Apply neutrality testing to a single record.
    
    Args:
        record: Raw experiment record
    
    Returns:
        Record with neutrality analysis added
    """
    # Extract response text
    response_text = record.get('response_text')
    
    # Apply neutrality analysis
    analysis = analyze_response(response_text)
    
    # Add analysis to record
    record['neutrality_analysis'] = analysis
    
    return record


def analyze_all_records(input_file: Path, output_file: Optional[Path] = None) -> List[Dict]:
    """
    Analyze all records from input file.
    
    Args:
        input_file: Path to input JSONL file
        output_file: Optional path to write analyzed records (JSONL)
    
    Returns:
        List of analyzed records
    """
    print(f"Loading records from: {input_file}")
    records = load_jsonl_records(input_file)
    print(f"Loaded {len(records)} records")
    
    analyzed_records = []
    for idx, record in enumerate(records, 1):
        if idx % 10 == 0:
            print(f"Analyzing record {idx}/{len(records)}...")
        
        analyzed = analyze_record(record)
        analyzed_records.append(analyzed)
    
    # Write analyzed records if output file specified
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in analyzed_records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"Analyzed records written to: {output_file}")
    
    return analyzed_records


def create_analysis_table(records: List[Dict], output_file: Path, format: str = 'csv'):
    """
    Create flattened analysis table with one row per run.
    
    Args:
        records: List of analyzed records
        output_file: Path to output file
        format: Output format ('csv' or 'parquet')
    """
    if not records:
        print("No records to write")
        return
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if format.lower() == 'parquet':
        create_parquet_table(records, output_file)
    else:
        create_csv_table(records, output_file)


def create_csv_table(records: List[Dict], output_file: Path):
    """
    Create flattened CSV analysis table with one row per run.
    
    Args:
        records: List of analyzed records
        output_file: Path to output CSV file
    """
    
    # Define CSV columns
    fieldnames = [
        'timestamp',
        'persona_id',
        'question_id',
        'model_id',
        'model_family',
        'api_model_name',
        'has_error',
        'status_code',
        'response_text_length',
        # Detectors
        'persona_leakage_detected',
        'persona_leakage_count',
        'roleplay_adoption_detected',
        'roleplay_adoption_count',
        'refusal_flag_detected',
        'refusal_flag_count',
        'harmful_content_flag_detected',
        'harmful_content_flag_count',
        # Soft signals
        'hedging_count',
        'hedging_per_100_words',
        'certainty_count',
        'certainty_per_100_words',
        'moral_language_count',
        'moral_language_per_100_words',
        'prescriptive_verbs_count',
        'prescriptive_verbs_per_100_words',
        # Token usage
        'prompt_tokens',
        'completion_tokens',
        'total_tokens',
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in records:
            analysis = record.get('neutrality_analysis', {})
            token_usage = record.get('token_usage', {})
            response_text = record.get('response_text', '')
            
            row = {
                'timestamp': record.get('timestamp', ''),
                'persona_id': record.get('persona_id', ''),
                'question_id': record.get('question_id', ''),
                'model_id': record.get('model_id', ''),
                'model_family': record.get('model_family', ''),
                'api_model_name': record.get('api_model_name', ''),
                'has_error': record.get('has_error', False),
                'status_code': record.get('status_code', ''),
                'response_text_length': len(response_text) if response_text else 0,
                # Detectors
                'persona_leakage_detected': analysis.get('persona_leakage', {}).get('detected', False),
                'persona_leakage_count': analysis.get('persona_leakage', {}).get('match_count', 0),
                'roleplay_adoption_detected': analysis.get('roleplay_adoption', {}).get('detected', False),
                'roleplay_adoption_count': analysis.get('roleplay_adoption', {}).get('match_count', 0),
                'refusal_flag_detected': analysis.get('refusal_flag', {}).get('detected', False),
                'refusal_flag_count': analysis.get('refusal_flag', {}).get('match_count', 0),
                'harmful_content_flag_detected': analysis.get('harmful_content_flag', {}).get('detected', False),
                'harmful_content_flag_count': analysis.get('harmful_content_flag', {}).get('match_count', 0),
                # Soft signals
                'hedging_count': analysis.get('hedging', {}).get('count', 0),
                'hedging_per_100_words': analysis.get('hedging', {}).get('per_100_words', 0.0),
                'certainty_count': analysis.get('certainty', {}).get('count', 0),
                'certainty_per_100_words': analysis.get('certainty', {}).get('per_100_words', 0.0),
                'moral_language_count': analysis.get('moral_language', {}).get('count', 0),
                'moral_language_per_100_words': analysis.get('moral_language', {}).get('per_100_words', 0.0),
                'prescriptive_verbs_count': analysis.get('prescriptive_verbs', {}).get('count', 0),
                'prescriptive_verbs_per_100_words': analysis.get('prescriptive_verbs', {}).get('per_100_words', 0.0),
                # Token usage
                'prompt_tokens': token_usage.get('prompt_tokens', ''),
                'completion_tokens': token_usage.get('completion_tokens', ''),
                'total_tokens': token_usage.get('total_tokens', ''),
            }
            writer.writerow(row)
    
    print(f"CSV analysis table written to: {output_file}")


def create_parquet_table(records: List[Dict], output_file: Path):
    """
    Create flattened Parquet analysis table with one row per run.
    
    Args:
        records: List of analyzed records
        output_file: Path to output Parquet file
    """
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas and pyarrow required for Parquet output.")
        print("Install with: pip install pandas pyarrow")
        return
    
    # Build rows
    rows = []
    for record in records:
        analysis = record.get('neutrality_analysis', {})
        token_usage = record.get('token_usage', {})
        response_text = record.get('response_text', '')
        
        row = {
            'timestamp': record.get('timestamp', ''),
            'persona_id': record.get('persona_id', ''),
            'question_id': record.get('question_id', ''),
            'model_id': record.get('model_id', ''),
            'model_family': record.get('model_family', ''),
            'api_model_name': record.get('api_model_name', ''),
            'has_error': record.get('has_error', False),
            'status_code': record.get('status_code', ''),
            'response_text_length': len(response_text) if response_text else 0,
            # Detectors
            'persona_leakage_detected': analysis.get('persona_leakage', {}).get('detected', False),
            'persona_leakage_count': analysis.get('persona_leakage', {}).get('match_count', 0),
            'roleplay_adoption_detected': analysis.get('roleplay_adoption', {}).get('detected', False),
            'roleplay_adoption_count': analysis.get('roleplay_adoption', {}).get('match_count', 0),
            'refusal_flag_detected': analysis.get('refusal_flag', {}).get('detected', False),
            'refusal_flag_count': analysis.get('refusal_flag', {}).get('match_count', 0),
            'harmful_content_flag_detected': analysis.get('harmful_content_flag', {}).get('detected', False),
            'harmful_content_flag_count': analysis.get('harmful_content_flag', {}).get('match_count', 0),
            # Soft signals
            'hedging_count': analysis.get('hedging', {}).get('count', 0),
            'hedging_per_100_words': analysis.get('hedging', {}).get('per_100_words', 0.0),
            'certainty_count': analysis.get('certainty', {}).get('count', 0),
            'certainty_per_100_words': analysis.get('certainty', {}).get('per_100_words', 0.0),
            'moral_language_count': analysis.get('moral_language', {}).get('count', 0),
            'moral_language_per_100_words': analysis.get('moral_language', {}).get('per_100_words', 0.0),
            'prescriptive_verbs_count': analysis.get('prescriptive_verbs', {}).get('count', 0),
            'prescriptive_verbs_per_100_words': analysis.get('prescriptive_verbs', {}).get('per_100_words', 0.0),
            # Token usage
            'prompt_tokens': token_usage.get('prompt_tokens') or 0,
            'completion_tokens': token_usage.get('completion_tokens') or 0,
            'total_tokens': token_usage.get('total_tokens') or 0,
        }
        rows.append(row)
    
    # Create DataFrame and write Parquet
    df = pd.DataFrame(rows)
    df.to_parquet(output_file, index=False, engine='pyarrow')
    
    print(f"Parquet analysis table written to: {output_file}")


def main():
    """Main entry point for analyzing outputs."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze experiment outputs with neutrality testing")
    parser.add_argument(
        '--input',
        type=Path,
        default=Path(__file__).parent.parent / "output" / "raw" / "runs.jsonl",
        help="Path to input JSONL file"
    )
    parser.add_argument(
        '--output-jsonl',
        type=Path,
        default=None,
        help="Path to output analyzed JSONL file (optional)"
    )
    parser.add_argument(
        '--output-table',
        type=Path,
        default=Path(__file__).parent.parent / "output" / "analysis" / "runs.csv",
        help="Path to output analysis table (CSV or Parquet)"
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'parquet'],
        default='csv',
        help="Output format for analysis table (default: csv)"
    )
    parser.add_argument(
        '--table-only',
        action='store_true',
        help="Only generate analysis table, skip JSONL output"
    )
    
    args = parser.parse_args()
    
    # Analyze records
    analyzed_records = analyze_all_records(
        input_file=args.input,
        output_file=None if args.table_only else (args.output_jsonl or args.input)
    )
    
    # Generate analysis table
    if analyzed_records:
        create_analysis_table(analyzed_records, args.output_table, format=args.format)
    else:
        print("No records found to analyze")


if __name__ == "__main__":
    main()

