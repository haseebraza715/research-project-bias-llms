"""
Analyze experiment outputs and apply neutrality testing layer.

Reads raw JSONL records, applies detectors and soft signal analysis,
and optionally generates flattened analysis table.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
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
        'persona_country',
        'persona_conspiratorial_level',
        'persona_secondary_level',
        'persona_new_level',
        'persona_age_group',
        'persona_gender',
        'persona_education',
        'persona_religiosity',
        'persona_political_trust',
        'persona_migration_attitude',
        'question_id',
        'question_type',
        'question_diagnostic_for',
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
        'antisemitic_framing_detected',
        'antisemitic_framing_count',
        # Frames
        'frame_moral_count',
        'frame_moral_per_100_words',
        'frame_epistemic_count',
        'frame_epistemic_per_100_words',
        'frame_political_count',
        'frame_political_per_100_words',
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
            persona_meta: Dict[str, Any] = record.get('persona_metadata', {})
            question_meta: Dict[str, Any] = record.get('question_metadata', {})
            
            row = {
                'timestamp': record.get('timestamp', ''),
                'persona_id': record.get('persona_id', ''),
                'persona_country': persona_meta.get('country', ''),
                'persona_conspiratorial_level': persona_meta.get('dimension_profile', {}).get('conspiratorial', ''),
                'persona_secondary_level': persona_meta.get('dimension_profile', {}).get('secondary', ''),
                'persona_new_level': persona_meta.get('dimension_profile', {}).get('new', ''),
                'persona_age_group': persona_meta.get('sociodem', {}).get('age_group', ''),
                'persona_gender': persona_meta.get('sociodem', {}).get('gender', ''),
                'persona_education': persona_meta.get('sociodem', {}).get('education', ''),
                'persona_religiosity': persona_meta.get('sociodem', {}).get('religiosity', ''),
                'persona_political_trust': persona_meta.get('sociodem', {}).get('political_trust', ''),
                'persona_migration_attitude': persona_meta.get('sociodem', {}).get('migration_attitude', ''),
                'question_id': record.get('question_id', ''),
                'question_type': question_meta.get('type', ''),
                'question_diagnostic_for': question_meta.get('diagnostic_for', ''),
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
                'antisemitic_framing_detected': analysis.get('antisemitic_framing', {}).get('detected', False),
                'antisemitic_framing_count': analysis.get('antisemitic_framing', {}).get('match_count', 0),
                # Frames
                'frame_moral_count': analysis.get('frames', {}).get('moral', {}).get('count', 0),
                'frame_moral_per_100_words': analysis.get('frames', {}).get('moral', {}).get('per_100_words', 0.0),
                'frame_epistemic_count': analysis.get('frames', {}).get('epistemic', {}).get('count', 0),
                'frame_epistemic_per_100_words': analysis.get('frames', {}).get('epistemic', {}).get('per_100_words', 0.0),
                'frame_political_count': analysis.get('frames', {}).get('political', {}).get('count', 0),
                'frame_political_per_100_words': analysis.get('frames', {}).get('political', {}).get('per_100_words', 0.0),
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
        persona_meta: Dict[str, Any] = record.get('persona_metadata', {})
        question_meta: Dict[str, Any] = record.get('question_metadata', {})
        
        row = {
            'timestamp': record.get('timestamp', ''),
            'persona_id': record.get('persona_id', ''),
            'persona_country': persona_meta.get('country', ''),
            'persona_conspiratorial_level': persona_meta.get('dimension_profile', {}).get('conspiratorial', ''),
            'persona_secondary_level': persona_meta.get('dimension_profile', {}).get('secondary', ''),
            'persona_new_level': persona_meta.get('dimension_profile', {}).get('new', ''),
            'persona_age_group': persona_meta.get('sociodem', {}).get('age_group', ''),
            'persona_gender': persona_meta.get('sociodem', {}).get('gender', ''),
            'persona_education': persona_meta.get('sociodem', {}).get('education', ''),
            'persona_religiosity': persona_meta.get('sociodem', {}).get('religiosity', ''),
            'persona_political_trust': persona_meta.get('sociodem', {}).get('political_trust', ''),
            'persona_migration_attitude': persona_meta.get('sociodem', {}).get('migration_attitude', ''),
            'question_id': record.get('question_id', ''),
            'question_type': question_meta.get('type', ''),
            'question_diagnostic_for': question_meta.get('diagnostic_for', ''),
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
            'antisemitic_framing_detected': analysis.get('antisemitic_framing', {}).get('detected', False),
            'antisemitic_framing_count': analysis.get('antisemitic_framing', {}).get('match_count', 0),
            # Soft signals
            'hedging_count': analysis.get('hedging', {}).get('count', 0),
            'hedging_per_100_words': analysis.get('hedging', {}).get('per_100_words', 0.0),
            'certainty_count': analysis.get('certainty', {}).get('count', 0),
            'certainty_per_100_words': analysis.get('certainty', {}).get('per_100_words', 0.0),
            'moral_language_count': analysis.get('moral_language', {}).get('count', 0),
            'moral_language_per_100_words': analysis.get('moral_language', {}).get('per_100_words', 0.0),
            'prescriptive_verbs_count': analysis.get('prescriptive_verbs', {}).get('count', 0),
            'prescriptive_verbs_per_100_words': analysis.get('prescriptive_verbs', {}).get('per_100_words', 0.0),
            # Frame markers
            'frame_moral_count': analysis.get('frames', {}).get('moral', {}).get('count', 0),
            'frame_moral_per_100_words': analysis.get('frames', {}).get('moral', {}).get('per_100_words', 0.0),
            'frame_epistemic_count': analysis.get('frames', {}).get('epistemic', {}).get('count', 0),
            'frame_epistemic_per_100_words': analysis.get('frames', {}).get('epistemic', {}).get('per_100_words', 0.0),
            'frame_political_count': analysis.get('frames', {}).get('political', {}).get('count', 0),
            'frame_political_per_100_words': analysis.get('frames', {}).get('political', {}).get('per_100_words', 0.0),
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
    parser.add_argument(
        '--print-summary',
        action='store_true',
        help="Print simple summaries for RQ-style analyses (dimensions, frames, consistency)"
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
        if args.print_summary:
            print_rq_summaries(analyzed_records)
    else:
        print("No records found to analyze")


def print_rq_summaries(records: List[Dict]):
    """
    Print simple, low-cost summaries relevant to RQ1–RQ7.

    This is intentionally lightweight (no heavy stats libraries) and aimed at
    quick inspection of patterns rather than full inference.
    """
    if not records:
        return

    def avg(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    # RQ1/RQ2: metrics by dimension profile
    by_dim: Dict[str, Dict[str, List[float]]] = {}
    for r in records:
        meta = r.get("persona_metadata", {})
        dims = meta.get("dimension_profile", {})
        level = dims.get("conspiratorial") or "unknown"
        analysis = r.get("neutrality_analysis", {})
        hedging = analysis.get("hedging", {}).get("per_100_words", 0.0)
        certainty = analysis.get("certainty", {}).get("per_100_words", 0.0)
        by_dim.setdefault(level, {"hedging": [], "certainty": []})
        by_dim[level]["hedging"].append(float(hedging or 0.0))
        by_dim[level]["certainty"].append(float(certainty or 0.0))

    print("\n=== RQ1/RQ2: Hedging and certainty by conspiratorial dimension ===")
    for level, vals in sorted(by_dim.items()):
        print(f"- {level}: hedging={avg(vals['hedging']):.2f} per 100 words, certainty={avg(vals['certainty']):.2f} per 100 words")

    # RQ3/RQ4: by question type and diagnostic_for
    by_qtype: Dict[str, Dict[str, int]] = {}
    for r in records:
        qmeta = r.get("question_metadata", {})
        qtype = qmeta.get("type", "unknown")
        diag = qmeta.get("diagnostic_for", "none")
        analysis = r.get("neutrality_analysis", {})
        harmful = bool(analysis.get("harmful_content_flag", {}).get("detected", False))
        antisemitic = bool(analysis.get("antisemitic_framing", {}).get("detected", False))
        key = f"{qtype}:{diag}"
        stats = by_qtype.setdefault(key, {"n": 0, "harmful": 0, "antisemitic": 0})
        stats["n"] += 1
        if harmful:
            stats["harmful"] += 1
        if antisemitic:
            stats["antisemitic"] += 1

    print("\n=== RQ3/RQ4: Question type × diagnostic_for (harmful / antisemitic rates) ===")
    for key, stats in sorted(by_qtype.items()):
        n = stats["n"]
        if n == 0:
            continue
        h_rate = stats["harmful"] / n
        a_rate = stats["antisemitic"] / n
        print(f"- {key}: n={n}, harmful_rate={h_rate:.2f}, antisemitic_rate={a_rate:.2f}")

    # RQ7: simple consistency check across repeats
    combos: Dict[tuple, List[bool]] = {}
    for r in records:
        k = (r.get("persona_id"), r.get("question_id"), r.get("model_id"))
        analysis = r.get("neutrality_analysis", {})
        harmful = bool(analysis.get("harmful_content_flag", {}).get("detected", False))
        combos.setdefault(k, []).append(harmful)

    inconsistent = 0
    total = 0
    for k, flags in combos.items():
        if len(flags) < 2:
            continue
        total += 1
        if any(f != flags[0] for f in flags[1:]):
            inconsistent += 1

    if total > 0:
        print("\n=== RQ7: Consistency of harmful_content_flag across repeats ===")
        print(f"- Repeated combos: {total}, inconsistent in {inconsistent} cases ({inconsistent/total:.2f})")


if __name__ == "__main__":
    main()

