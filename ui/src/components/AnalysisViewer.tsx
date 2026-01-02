import React, { useState, useMemo } from 'react';
import { AnalysisRow, FilterState } from '../types';
import { filterAnalysisRows } from '../utils/filtering';
import { exportCsv } from '../utils/csvExport';

interface AnalysisViewerProps {
  rows: AnalysisRow[];
  filters: FilterState;
}

const MAX_DISPLAY = 2000;

export const AnalysisViewer: React.FC<AnalysisViewerProps> = ({
  rows,
  filters,
}) => {
  const [selectedRow, setSelectedRow] = useState<AnalysisRow | null>(null);

  const filtered = useMemo(
    () => {
      if (!rows || rows.length === 0) return [];
      return filterAnalysisRows(rows, filters);
    },
    [rows, filters]
  );

  const displayRows = filtered?.slice(0, MAX_DISPLAY) || [];
  const hasMore = (filtered?.length || 0) > MAX_DISPLAY;

  // Summary calculations
  const uniquePersonas = useMemo(
    () => (filtered && filtered.length > 0) ? new Set(filtered.map((r) => r.persona_id)).size : 0,
    [filtered]
  );
  const uniqueQuestions = useMemo(
    () => (filtered && filtered.length > 0) ? new Set(filtered.map((r) => r.question_id)).size : 0,
    [filtered]
  );
  const uniqueModels = useMemo(
    () => (filtered && filtered.length > 0) ? new Set(filtered.map((r) => r.model_id)).size : 0,
    [filtered]
  );
  const errorCount = useMemo(
    () => (filtered && filtered.length > 0) ? filtered.filter((r) => r.has_error).length : 0,
    [filtered]
  );
  const avgTotalTokens = useMemo(() => {
    if (!filtered || filtered.length === 0) return null;
    const tokens = filtered
      .map((r) => r.total_tokens)
      .filter((t): t is number => t !== null);
    if (tokens.length === 0) return null;
    return Math.round(tokens.reduce((a, b) => a + b, 0) / tokens.length);
  }, [filtered]);
  const avgResponseLength = useMemo(() => {
    if (!filtered || filtered.length === 0) return null;
    const lengths = filtered
      .map((r) => r.response_text_length)
      .filter((l): l is number => l !== null);
    if (lengths.length === 0) return null;
    return Math.round(lengths.reduce((a, b) => a + b, 0) / lengths.length);
  }, [filtered]);

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'boolean') return value ? '✓' : '✗';
    if (typeof value === 'number') {
      if (Number.isInteger(value)) return value.toString();
      return value.toFixed(2);
    }
    return String(value);
  };

  return (
    <div className="analysis-viewer">
      <div className="summary-strip">
        <div className="summary-item">
          <span className="summary-label">Total loaded:</span>
          <span>{rows.length}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">After filter:</span>
          <span>{filtered.length}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Unique personas:</span>
          <span>{uniquePersonas}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Unique questions:</span>
          <span>{uniqueQuestions}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Unique models:</span>
          <span>{uniqueModels}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Errors:</span>
          <span>{errorCount}</span>
        </div>
        {avgTotalTokens !== null && (
          <div className="summary-item">
            <span className="summary-label">Avg tokens:</span>
            <span>{avgTotalTokens}</span>
          </div>
        )}
        {avgResponseLength !== null && (
          <div className="summary-item">
            <span className="summary-label">Avg response length:</span>
            <span>{avgResponseLength}</span>
          </div>
        )}
        <div className="summary-item export-button">
          <button
            className="button"
            onClick={() => exportCsv(filtered)}
          >
            Download filtered CSV
          </button>
        </div>
      </div>

      <div className="analysis-table-container">
        {hasMore && (
          <div className="analysis-table-info">
            Showing first {MAX_DISPLAY} of {filtered.length} rows
          </div>
        )}
        <table className="analysis-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Persona</th>
              <th>Question</th>
              <th>Model</th>
              <th>Error</th>
              <th>Length</th>
              <th>Leakage</th>
              <th>Roleplay</th>
              <th>Refusal</th>
              <th>Harmful</th>
              <th>Hedging</th>
              <th>Certainty</th>
              <th>Moral</th>
              <th>Prescriptive</th>
              <th>Tokens</th>
            </tr>
          </thead>
          <tbody>
            {displayRows.map((row, index) => (
              <tr
                key={index}
                className={selectedRow === row ? 'selected' : ''}
                onClick={() => setSelectedRow(row)}
              >
                <td>{new Date(row.timestamp).toLocaleString()}</td>
                <td>{row.persona_id}</td>
                <td>{row.question_id}</td>
                <td>{row.model_id}</td>
                <td className={row.has_error ? 'boolean-true' : 'boolean-false'}>
                  {formatValue(row.has_error)}
                </td>
                <td className="number">{formatValue(row.response_text_length)}</td>
                <td className={row.persona_leakage_detected ? 'boolean-true' : 'boolean-false'}>
                  {formatValue(row.persona_leakage_detected)}
                </td>
                <td className={row.roleplay_adoption_detected ? 'boolean-true' : 'boolean-false'}>
                  {formatValue(row.roleplay_adoption_detected)}
                </td>
                <td className={row.refusal_flag_detected ? 'boolean-true' : 'boolean-false'}>
                  {formatValue(row.refusal_flag_detected)}
                </td>
                <td className={row.harmful_content_flag_detected ? 'boolean-true' : 'boolean-false'}>
                  {formatValue(row.harmful_content_flag_detected)}
                </td>
                <td className="number">{formatValue(row.hedging_per_100_words)}</td>
                <td className="number">{formatValue(row.certainty_per_100_words)}</td>
                <td className="number">{formatValue(row.moral_language_per_100_words)}</td>
                <td className="number">{formatValue(row.prescriptive_verbs_per_100_words)}</td>
                <td className="number">{formatValue(row.total_tokens)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedRow && (
        <DetailDrawer row={selectedRow} onClose={() => setSelectedRow(null)} />
      )}
    </div>
  );
};

interface DetailDrawerProps {
  row: AnalysisRow;
  onClose: () => void;
}

const DetailDrawer: React.FC<DetailDrawerProps> = ({ row, onClose }) => {
  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'boolean') return value ? 'True' : 'False';
    if (typeof value === 'number') {
      if (Number.isInteger(value)) return value.toString();
      return value.toFixed(2);
    }
    return String(value);
  };

  const getValueClass = (value: any): string => {
    if (typeof value === 'boolean') {
      return value ? 'boolean-true' : 'boolean-false';
    }
    if (typeof value === 'number') {
      return 'number';
    }
    return '';
  };

  return (
    <div className="detail-drawer">
      <div className="detail-drawer-header">
        <div className="detail-drawer-title">Row Details</div>
        <button className="detail-drawer-close" onClick={onClose}>
          ×
        </button>
      </div>
      <div className="detail-drawer-content">
        <div className="detail-kv-list">
          <div className="detail-kv-key">timestamp</div>
          <div className="detail-kv-value">{row.timestamp}</div>

          <div className="detail-kv-key">persona_id</div>
          <div className="detail-kv-value">{row.persona_id}</div>

          <div className="detail-kv-key">question_id</div>
          <div className="detail-kv-value">{row.question_id}</div>

          <div className="detail-kv-key">model_id</div>
          <div className="detail-kv-value">{row.model_id}</div>

          <div className="detail-kv-key">model_family</div>
          <div className="detail-kv-value">{row.model_family}</div>

          <div className="detail-kv-key">api_model_name</div>
          <div className="detail-kv-value">{row.api_model_name}</div>

          <div className="detail-kv-key">has_error</div>
          <div className={`detail-kv-value ${getValueClass(row.has_error)}`}>
            {formatValue(row.has_error)}
          </div>

          <div className="detail-kv-key">status_code</div>
          <div className={`detail-kv-value ${getValueClass(row.status_code)}`}>
            {formatValue(row.status_code)}
          </div>

          <div className="detail-kv-key">response_text_length</div>
          <div className={`detail-kv-value ${getValueClass(row.response_text_length)}`}>
            {formatValue(row.response_text_length)}
          </div>

          <div className="detail-kv-key">persona_leakage_detected</div>
          <div className={`detail-kv-value ${getValueClass(row.persona_leakage_detected)}`}>
            {formatValue(row.persona_leakage_detected)}
          </div>

          <div className="detail-kv-key">persona_leakage_count</div>
          <div className={`detail-kv-value ${getValueClass(row.persona_leakage_count)}`}>
            {formatValue(row.persona_leakage_count)}
          </div>

          <div className="detail-kv-key">roleplay_adoption_detected</div>
          <div className={`detail-kv-value ${getValueClass(row.roleplay_adoption_detected)}`}>
            {formatValue(row.roleplay_adoption_detected)}
          </div>

          <div className="detail-kv-key">roleplay_adoption_count</div>
          <div className={`detail-kv-value ${getValueClass(row.roleplay_adoption_count)}`}>
            {formatValue(row.roleplay_adoption_count)}
          </div>

          <div className="detail-kv-key">refusal_flag_detected</div>
          <div className={`detail-kv-value ${getValueClass(row.refusal_flag_detected)}`}>
            {formatValue(row.refusal_flag_detected)}
          </div>

          <div className="detail-kv-key">refusal_flag_count</div>
          <div className={`detail-kv-value ${getValueClass(row.refusal_flag_count)}`}>
            {formatValue(row.refusal_flag_count)}
          </div>

          <div className="detail-kv-key">harmful_content_flag_detected</div>
          <div className={`detail-kv-value ${getValueClass(row.harmful_content_flag_detected)}`}>
            {formatValue(row.harmful_content_flag_detected)}
          </div>

          <div className="detail-kv-key">harmful_content_flag_count</div>
          <div className={`detail-kv-value ${getValueClass(row.harmful_content_flag_count)}`}>
            {formatValue(row.harmful_content_flag_count)}
          </div>

          <div className="detail-kv-key">hedging_count</div>
          <div className={`detail-kv-value ${getValueClass(row.hedging_count)}`}>
            {formatValue(row.hedging_count)}
          </div>

          <div className="detail-kv-key">hedging_per_100_words</div>
          <div className={`detail-kv-value ${getValueClass(row.hedging_per_100_words)}`}>
            {formatValue(row.hedging_per_100_words)}
          </div>

          <div className="detail-kv-key">certainty_count</div>
          <div className={`detail-kv-value ${getValueClass(row.certainty_count)}`}>
            {formatValue(row.certainty_count)}
          </div>

          <div className="detail-kv-key">certainty_per_100_words</div>
          <div className={`detail-kv-value ${getValueClass(row.certainty_per_100_words)}`}>
            {formatValue(row.certainty_per_100_words)}
          </div>

          <div className="detail-kv-key">moral_language_count</div>
          <div className={`detail-kv-value ${getValueClass(row.moral_language_count)}`}>
            {formatValue(row.moral_language_count)}
          </div>

          <div className="detail-kv-key">moral_language_per_100_words</div>
          <div className={`detail-kv-value ${getValueClass(row.moral_language_per_100_words)}`}>
            {formatValue(row.moral_language_per_100_words)}
          </div>

          <div className="detail-kv-key">prescriptive_verbs_count</div>
          <div className={`detail-kv-value ${getValueClass(row.prescriptive_verbs_count)}`}>
            {formatValue(row.prescriptive_verbs_count)}
          </div>

          <div className="detail-kv-key">prescriptive_verbs_per_100_words</div>
          <div className={`detail-kv-value ${getValueClass(row.prescriptive_verbs_per_100_words)}`}>
            {formatValue(row.prescriptive_verbs_per_100_words)}
          </div>

          <div className="detail-kv-key">prompt_tokens</div>
          <div className={`detail-kv-value ${getValueClass(row.prompt_tokens)}`}>
            {formatValue(row.prompt_tokens)}
          </div>

          <div className="detail-kv-key">completion_tokens</div>
          <div className={`detail-kv-value ${getValueClass(row.completion_tokens)}`}>
            {formatValue(row.completion_tokens)}
          </div>

          <div className="detail-kv-key">total_tokens</div>
          <div className={`detail-kv-value ${getValueClass(row.total_tokens)}`}>
            {formatValue(row.total_tokens)}
          </div>
        </div>
      </div>
    </div>
  );
};

