import { RawRunRecord } from '../types';

export interface LoadJsonlResult {
  records: RawRunRecord[];
  skipped: number;
}

export async function loadJsonlFromUrl(url: string): Promise<LoadJsonlResult> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch JSONL: ${response.statusText}`);
  }
  const text = await response.text();
  return parseJsonl(text);
}

export function loadJsonlFromFile(file: File): Promise<LoadJsonlResult> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string;
        const result = parseJsonl(text);
        resolve(result);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

function parseJsonl(text: string): LoadJsonlResult {
  const lines = text.trim().split('\n');
  const records: RawRunRecord[] = [];
  let skipped = 0;

  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const record = JSON.parse(line) as RawRunRecord;
      records.push(record);
    } catch (error) {
      skipped++;
    }
  }

  return { records, skipped };
}

