import React from 'react';
import { FilterState, RawRunRecord, AnalysisRow } from '../types';
import { getUniqueValues } from '../utils/filtering';

interface FilterBarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  rawRecords?: RawRunRecord[];
  analysisRows?: AnalysisRow[];
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onFiltersChange,
  rawRecords,
  analysisRows,
}) => {
  const isRawMode = !!rawRecords;
  const data = rawRecords || analysisRows || [];

  const personaIds = getUniqueValues(data as (RawRunRecord | AnalysisRow)[], 'persona_id');
  const questionIds = getUniqueValues(data as (RawRunRecord | AnalysisRow)[], 'question_id');
  const modelIds = getUniqueValues(data as (RawRunRecord | AnalysisRow)[], 'model_id');
  const modelFamilies = getUniqueValues(data as (RawRunRecord | AnalysisRow)[], 'model_family');
  const apiModelNames = getUniqueValues(data as (RawRunRecord | AnalysisRow)[], 'api_model_name');

  const updateFilter = <K extends keyof FilterState>(
    key: K,
    value: FilterState[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  return (
    <div className="filter-bar">
      <div className="filter-group">
        <label>Persona:</label>
        <select
          value={filters.persona_id}
          onChange={(e) => updateFilter('persona_id', e.target.value)}
        >
          <option value="">All</option>
          {personaIds.map((id) => (
            <option key={id} value={id}>
              {id}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Question:</label>
        <select
          value={filters.question_id}
          onChange={(e) => updateFilter('question_id', e.target.value)}
        >
          <option value="">All</option>
          {questionIds.map((id) => (
            <option key={id} value={id}>
              {id}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Model:</label>
        <select
          value={filters.model_id}
          onChange={(e) => updateFilter('model_id', e.target.value)}
        >
          <option value="">All</option>
          {modelIds.map((id) => (
            <option key={id} value={id}>
              {id}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Family:</label>
        <select
          value={filters.model_family}
          onChange={(e) => updateFilter('model_family', e.target.value)}
        >
          <option value="">All</option>
          {modelFamilies.map((family) => (
            <option key={family} value={family}>
              {family}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>API Model:</label>
        <select
          value={filters.api_model_name}
          onChange={(e) => updateFilter('api_model_name', e.target.value)}
        >
          <option value="">All</option>
          {apiModelNames.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>
          <input
            type="checkbox"
            checked={filters.errorsOnly}
            onChange={(e) => updateFilter('errorsOnly', e.target.checked)}
          />
          Errors only
        </label>
      </div>

      <div className="filter-group">
        <label>Search:</label>
        <input
          type="text"
          value={filters.search}
          onChange={(e) => updateFilter('search', e.target.value)}
          placeholder={isRawMode ? 'Search in records...' : 'Search in rows...'}
        />
      </div>

      <div className="filter-group">
        <label>Sort:</label>
        <select
          value={filters.sort}
          onChange={(e) => updateFilter('sort', e.target.value as FilterState['sort'])}
        >
          <option value="timestamp_desc">Timestamp (desc)</option>
          <option value="timestamp_asc">Timestamp (asc)</option>
          <option value="persona_id">Persona ID</option>
          <option value="question_id">Question ID</option>
          <option value="model_id">Model ID</option>
        </select>
      </div>
    </div>
  );
};

