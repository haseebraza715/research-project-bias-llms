import { RawRunRecord, AnalysisRow, FilterState, SortOption } from '../types';

export function filterRawRecords(
  records: RawRunRecord[],
  filters: FilterState
): RawRunRecord[] {
  if (!records || records.length === 0) return [];
  let filtered = [...records];

  // Apply filters
  if (filters.persona_id) {
    filtered = filtered.filter((r) => r.persona_id === filters.persona_id);
  }
  if (filters.question_id) {
    filtered = filtered.filter((r) => r.question_id === filters.question_id);
  }
  if (filters.model_id) {
    filtered = filtered.filter((r) => r.model_id === filters.model_id);
  }
  if (filters.model_family) {
    filtered = filtered.filter((r) => r.model_family === filters.model_family);
  }
  if (filters.api_model_name) {
    filtered = filtered.filter((r) => r.api_model_name === filters.api_model_name);
  }
  if (filters.errorsOnly) {
    filtered = filtered.filter((r) => r.has_error === true);
  }
  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filtered = filtered.filter((r) => {
      return (
        r.prompt_hash?.toLowerCase().includes(searchLower) ||
        r.persona_id?.toLowerCase().includes(searchLower) ||
        r.question_id?.toLowerCase().includes(searchLower) ||
        r.model_id?.toLowerCase().includes(searchLower) ||
        r.response_text?.toLowerCase().includes(searchLower) ||
        (r.api_response?.error &&
          (typeof r.api_response.error === 'string'
            ? r.api_response.error.toLowerCase().includes(searchLower)
            : r.api_response.error.message?.toLowerCase().includes(searchLower)))
      );
    });
  }

  // Apply sorting
  filtered = sortRawRecords(filtered, filters.sort);

  return filtered;
}

export function filterAnalysisRows(
  rows: AnalysisRow[],
  filters: FilterState
): AnalysisRow[] {
  if (!rows || rows.length === 0) return [];
  let filtered = [...rows];

  // Apply filters
  if (filters.persona_id) {
    filtered = filtered.filter((r) => r.persona_id === filters.persona_id);
  }
  if (filters.question_id) {
    filtered = filtered.filter((r) => r.question_id === filters.question_id);
  }
  if (filters.model_id) {
    filtered = filtered.filter((r) => r.model_id === filters.model_id);
  }
  if (filters.model_family) {
    filtered = filtered.filter((r) => r.model_family === filters.model_family);
  }
  if (filters.api_model_name) {
    filtered = filtered.filter((r) => r.api_model_name === filters.api_model_name);
  }
  if (filters.errorsOnly) {
    filtered = filtered.filter((r) => r.has_error === true);
  }
  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filtered = filtered.filter((r) => {
      return (
        r.persona_id?.toLowerCase().includes(searchLower) ||
        r.question_id?.toLowerCase().includes(searchLower) ||
        r.model_id?.toLowerCase().includes(searchLower) ||
        r.api_model_name?.toLowerCase().includes(searchLower)
      );
    });
  }

  // Apply sorting
  filtered = sortAnalysisRows(filtered, filters.sort);

  return filtered;
}

function sortRawRecords(records: RawRunRecord[], sort: SortOption): RawRunRecord[] {
  const sorted = [...records];
  sorted.sort((a, b) => {
    switch (sort) {
      case 'timestamp_desc':
        return b.timestamp.localeCompare(a.timestamp);
      case 'timestamp_asc':
        return a.timestamp.localeCompare(b.timestamp);
      case 'persona_id':
        return a.persona_id.localeCompare(b.persona_id);
      case 'question_id':
        return a.question_id.localeCompare(b.question_id);
      case 'model_id':
        return a.model_id.localeCompare(b.model_id);
      default:
        return 0;
    }
  });
  return sorted;
}

function sortAnalysisRows(rows: AnalysisRow[], sort: SortOption): AnalysisRow[] {
  const sorted = [...rows];
  sorted.sort((a, b) => {
    switch (sort) {
      case 'timestamp_desc':
        return b.timestamp.localeCompare(a.timestamp);
      case 'timestamp_asc':
        return a.timestamp.localeCompare(b.timestamp);
      case 'persona_id':
        return a.persona_id.localeCompare(b.persona_id);
      case 'question_id':
        return a.question_id.localeCompare(b.question_id);
      case 'model_id':
        return a.model_id.localeCompare(b.model_id);
      default:
        return 0;
    }
  });
  return sorted;
}

export function getUniqueValues<T extends Record<string, any>>(
  items: T[],
  key: keyof T
): string[] {
  const values = new Set<string>();
  for (const item of items) {
    const value = item[key];
    if (value != null && typeof value === 'string') {
      values.add(value);
    }
  }
  return Array.from(values).sort();
}

