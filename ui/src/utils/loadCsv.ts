import { AnalysisRow } from '../types';

export async function loadCsvFromUrl(url: string): Promise<AnalysisRow[]> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch CSV: ${response.statusText}`);
  }
  const text = await response.text();
  return parseCsv(text);
}

export function loadCsvFromFile(file: File): Promise<AnalysisRow[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string;
        const rows = parseCsv(text);
        resolve(rows);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

function parseCsv(text: string): AnalysisRow[] {
  const lines = text.trim().split('\n');
  if (lines.length < 2) return [];

  const headers = parseCsvLine(lines[0]);
  const rows: AnalysisRow[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCsvLine(lines[i]);
    if (values.length !== headers.length) continue;

    const row: Partial<AnalysisRow> = {};
    for (let j = 0; j < headers.length; j++) {
      const header = headers[j];
      const value = values[j].trim();

      if (value === '') {
        (row as any)[header] = null;
        continue;
      }

      // Boolean fields
      if (header === 'has_error' || header.endsWith('_detected')) {
        (row as any)[header] = value === 'True' || value === 'true' || value === '1';
      }
      // Numeric fields
      else if (
        header.endsWith('_count') ||
        header.endsWith('_per_100_words') ||
        header === 'status_code' ||
        header === 'response_text_length' ||
        header.endsWith('_tokens')
      ) {
        const num = parseFloat(value);
        (row as any)[header] = isNaN(num) ? null : num;
      }
      // String fields
      else {
        (row as any)[header] = value;
      }
    }

    rows.push(row as AnalysisRow);
  }

  return rows;
}

function parseCsvLine(line: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    const nextChar = line[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        current += '"';
        i++; // Skip next quote
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }

  result.push(current);
  return result;
}

