import { AnalysisRow } from '../types';

export function exportCsv(rows: AnalysisRow[], filename: string = 'filtered_runs.csv'): void {
  if (rows.length === 0) {
    alert('No data to export');
    return;
  }

  const headers = [
    'timestamp',
    'persona_id',
    'question_id',
    'model_id',
    'model_family',
    'api_model_name',
    'has_error',
    'status_code',
    'response_text_length',
    'persona_leakage_detected',
    'persona_leakage_count',
    'roleplay_adoption_detected',
    'roleplay_adoption_count',
    'refusal_flag_detected',
    'refusal_flag_count',
    'harmful_content_flag_detected',
    'harmful_content_flag_count',
    'hedging_count',
    'hedging_per_100_words',
    'certainty_count',
    'certainty_per_100_words',
    'moral_language_count',
    'moral_language_per_100_words',
    'prescriptive_verbs_count',
    'prescriptive_verbs_per_100_words',
    'prompt_tokens',
    'completion_tokens',
    'total_tokens',
  ];

  const escapeCsvValue = (value: any): string => {
    if (value === null || value === undefined) {
      return '';
    }
    const str = String(value);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const lines = [headers.join(',')];

  for (const row of rows) {
    const values = headers.map((header) => {
      const value = (row as any)[header];
      if (typeof value === 'boolean') {
        return value ? 'True' : 'False';
      }
      return escapeCsvValue(value);
    });
    lines.push(values.join(','));
  }

  const csv = lines.join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

