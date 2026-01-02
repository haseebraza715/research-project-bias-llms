import React, { useState, useMemo } from 'react';
import { RawRunRecord, FilterState } from '../types';
import { filterRawRecords } from '../utils/filtering';

interface RawViewerProps {
  records: RawRunRecord[];
  filters: FilterState;
  skipped: number;
}

const MAX_DISPLAY = 2000;

export const RawViewer: React.FC<RawViewerProps> = ({
  records,
  filters,
  skipped,
}) => {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [hideLongFields, setHideLongFields] = useState(false);

  const filtered = useMemo(
    () => {
      if (!records || records.length === 0) return [];
      return filterRawRecords(records, filters);
    },
    [records, filters]
  );

  const displayRecords = filtered?.slice(0, MAX_DISPLAY) || [];
  const hasMore = (filtered?.length || 0) > MAX_DISPLAY;

  const selectedRecord =
    selectedIndex !== null ? displayRecords[selectedIndex] : null;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="raw-viewer">
      <div className="raw-list">
        {skipped > 0 && (
          <div className="raw-list-info">
            Skipped {skipped} invalid line(s)
          </div>
        )}
        {hasMore && (
          <div className="raw-list-info">
            Showing first {MAX_DISPLAY} of {filtered.length} records
          </div>
        )}
        {displayRecords.map((record, index) => (
          <div
            key={index}
            className={`raw-list-item ${selectedIndex === index ? 'selected' : ''}`}
            onClick={() => setSelectedIndex(index)}
          >
            <div className="raw-list-item-header">
              {record.persona_id} / {record.question_id}
            </div>
            <div className="raw-list-item-meta">
              <span>{record.model_id}</span>
              {record.has_error && <span className="error-badge">ERROR</span>}
              {!hideLongFields && (
                <>
                  {record.prompt_hash && (
                    <span>{record.prompt_hash.substring(0, 8)}...</span>
                  )}
                  {record.response_text && (
                    <span>{record.response_text.length} chars</span>
                  )}
                </>
              )}
            </div>
          </div>
        ))}
        <div className="raw-list-toggle">
          <label>
            <input
              type="checkbox"
              checked={hideLongFields}
              onChange={(e) => setHideLongFields(e.target.checked)}
            />
            Hide long fields in list
          </label>
        </div>
      </div>

      <div className="raw-detail">
        {selectedRecord ? (
          <>
            <div className="raw-detail-section">
              <div className="raw-detail-section-title">Basic Info</div>
              <div className="raw-detail-content">
                <div>Timestamp: {selectedRecord.timestamp}</div>
                <div>Persona ID: {selectedRecord.persona_id}</div>
                <div>Question ID: {selectedRecord.question_id}</div>
                <div>Model ID: {selectedRecord.model_id}</div>
                <div>Model Family: {selectedRecord.model_family}</div>
                <div>API Model: {selectedRecord.api_model_name}</div>
                <div>Has Error: {selectedRecord.has_error ? 'Yes' : 'No'}</div>
                <div>Status Code: {selectedRecord.status_code}</div>
              </div>
            </div>

            <div className="raw-detail-section">
              <div className="raw-detail-section-title">Prompt Hash</div>
              <div className="raw-detail-content">{selectedRecord.prompt_hash || '(empty)'}</div>
            </div>

            <div className="raw-detail-section">
              <div className="raw-detail-section-title">System Prompt</div>
              <div className="raw-detail-content">{selectedRecord.system_prompt || '(empty)'}</div>
              {selectedRecord.system_prompt && (
                <div className="raw-detail-buttons">
                  <button
                    className="button"
                    onClick={() => copyToClipboard(selectedRecord.system_prompt)}
                  >
                    Copy prompt
                  </button>
                </div>
              )}
            </div>

            <div className="raw-detail-section">
              <div className="raw-detail-section-title">User Message</div>
              <div className="raw-detail-content">{selectedRecord.user_message || '(empty)'}</div>
            </div>

            <div className="raw-detail-section">
              <div className="raw-detail-section-title">Full Prompt</div>
              <div className="raw-detail-content">{selectedRecord.full_prompt || '(empty)'}</div>
            </div>

            <div className="raw-detail-section">
              <div className="raw-detail-section-title">Response Text</div>
              <div className="raw-detail-content">{selectedRecord.response_text || '(empty)'}</div>
              {selectedRecord.response_text && (
                <div className="raw-detail-buttons">
                  <button
                    className="button"
                    onClick={() => copyToClipboard(selectedRecord.response_text)}
                  >
                    Copy response
                  </button>
                </div>
              )}
            </div>

            <div className="raw-detail-section">
              <div className="raw-detail-section-title">API Response</div>
              <div className="raw-detail-json">
                {JSON.stringify(selectedRecord.api_response, null, 2)}
              </div>
            </div>

            <div className="raw-detail-section">
              <div className="raw-detail-section-title">Integrity Checks</div>
              <div className="raw-detail-json">
                {JSON.stringify(selectedRecord.integrity_checks, null, 2)}
              </div>
            </div>

            <div className="raw-detail-section">
              <div className="raw-detail-section-title">Neutrality Analysis</div>
              <div className="raw-detail-json">
                {JSON.stringify(selectedRecord.neutrality_analysis, null, 2)}
              </div>
            </div>
          </>
        ) : (
          <div className="loading">Select a record to view details</div>
        )}
      </div>
    </div>
  );
};

