import React, { useState, useEffect } from 'react';
import { RawRunRecord, AnalysisRow, FilterState } from './types';
import { loadJsonlFromUrl, loadJsonlFromFile } from './utils/loadJsonl';
import { loadCsvFromUrl, loadCsvFromFile } from './utils/loadCsv';
import { FilterBar } from './components/FilterBar';
import { RawViewer } from './components/RawViewer';
import { AnalysisViewer } from './components/AnalysisViewer';
import { useTheme } from './hooks/useTheme';
import './styles.css';

type Tab = 'raw' | 'analysis';

const initialFilters: FilterState = {
  persona_id: '',
  question_id: '',
  model_id: '',
  model_family: '',
  api_model_name: '',
  errorsOnly: false,
  search: '',
  sort: 'timestamp_desc',
};

function App() {
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState<Tab>('raw');
  const [rawRecords, setRawRecords] = useState<RawRunRecord[]>([]);
  const [analysisRows, setAnalysisRows] = useState<AnalysisRow[]>([]);
  const [rawSkipped, setRawSkipped] = useState(0);
  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [loading, setLoading] = useState({ raw: false, analysis: false });
  const [error, setError] = useState({ raw: '', analysis: '' });
  const [rawFileInput, setRawFileInput] = useState<HTMLInputElement | null>(null);
  const [analysisFileInput, setAnalysisFileInput] = useState<HTMLInputElement | null>(null);

  // Load raw JSONL
  useEffect(() => {
    if (activeTab === 'raw' && rawRecords.length === 0 && !loading.raw) {
      loadRawData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  // Load analysis CSV
  useEffect(() => {
    if (activeTab === 'analysis' && analysisRows.length === 0 && !loading.analysis) {
      loadAnalysisData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const loadRawData = async () => {
    setLoading((prev) => ({ ...prev, raw: true }));
    setError((prev) => ({ ...prev, raw: '' }));
    try {
      const result = await loadJsonlFromUrl('/output/raw/runs.jsonl');
      setRawRecords(result.records);
      setRawSkipped(result.skipped);
    } catch (err) {
      setError((prev) => ({
        ...prev,
        raw: 'Failed to load from URL. Please upload a file.',
      }));
    } finally {
      setLoading((prev) => ({ ...prev, raw: false }));
    }
  };

  const loadAnalysisData = async () => {
    setLoading((prev) => ({ ...prev, analysis: true }));
    setError((prev) => ({ ...prev, analysis: '' }));
    try {
      const rows = await loadCsvFromUrl('/output/analysis/runs.csv');
      setAnalysisRows(rows);
    } catch (err) {
      setError((prev) => ({
        ...prev,
        analysis: 'Failed to load from URL. Please upload a file.',
      }));
    } finally {
      setLoading((prev) => ({ ...prev, analysis: false }));
    }
  };

  const handleRawFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading((prev) => ({ ...prev, raw: true }));
    setError((prev) => ({ ...prev, raw: '' }));
    try {
      const result = await loadJsonlFromFile(file);
      setRawRecords(result.records);
      setRawSkipped(result.skipped);
    } catch (err) {
      setError((prev) => ({
        ...prev,
        raw: err instanceof Error ? err.message : 'Failed to load file',
      }));
    } finally {
      setLoading((prev) => ({ ...prev, raw: false }));
      if (rawFileInput) rawFileInput.value = '';
    }
  };

  const handleAnalysisFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading((prev) => ({ ...prev, analysis: true }));
    setError((prev) => ({ ...prev, analysis: '' }));
    try {
      const rows = await loadCsvFromFile(file);
      setAnalysisRows(rows);
    } catch (err) {
      setError((prev) => ({
        ...prev,
        analysis: err instanceof Error ? err.message : 'Failed to load file',
      }));
    } finally {
      setLoading((prev) => ({ ...prev, analysis: false }));
      if (analysisFileInput) analysisFileInput.value = '';
    }
  };

  const renderContent = () => {
    try {
      if (activeTab === 'raw') {
        if (loading.raw) {
          return <div className="loading">Loading raw data...</div>;
        }
        if (error.raw && rawRecords.length === 0) {
          return (
            <div>
              <div className="error">{error.raw}</div>
              <div className="file-upload-area" onClick={() => rawFileInput?.click()}>
                <input
                  ref={(el) => setRawFileInput(el)}
                  type="file"
                  accept=".jsonl,.json"
                  onChange={handleRawFileUpload}
                />
                <div className="file-upload-text">Click to upload JSONL file</div>
              </div>
            </div>
          );
        }
        if (!loading.raw && rawRecords.length === 0 && !error.raw) {
          return <div className="loading">No data loaded. Files should be in public/output/</div>;
        }
        return (
          <>
            <FilterBar
              filters={filters}
              onFiltersChange={setFilters}
              rawRecords={rawRecords}
            />
            <RawViewer
              records={rawRecords}
              filters={filters}
              skipped={rawSkipped}
            />
          </>
        );
      } else {
        if (loading.analysis) {
          return <div className="loading">Loading analysis data...</div>;
        }
        if (error.analysis && analysisRows.length === 0) {
          return (
            <div>
              <div className="error">{error.analysis}</div>
              <div className="file-upload-area" onClick={() => analysisFileInput?.click()}>
                <input
                  ref={(el) => setAnalysisFileInput(el)}
                  type="file"
                  accept=".csv"
                  onChange={handleAnalysisFileUpload}
                />
                <div className="file-upload-text">Click to upload CSV file</div>
              </div>
            </div>
          );
        }
        if (!loading.analysis && analysisRows.length === 0 && !error.analysis) {
          return <div className="loading">No data loaded. Files should be in public/output/</div>;
        }
        return (
          <>
            <FilterBar
              filters={filters}
              onFiltersChange={setFilters}
              analysisRows={analysisRows}
            />
            <AnalysisViewer rows={analysisRows} filters={filters} />
          </>
        );
      }
    } catch (err) {
      console.error('Error rendering content:', err);
      return (
        <div className="error">
          Error rendering content: {err instanceof Error ? err.message : String(err)}
        </div>
      );
    }
  };

  return (
    <div className="app">
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'raw' ? 'active' : ''}`}
          onClick={() => setActiveTab('raw')}
        >
          Raw Viewer (JSONL)
        </button>
        <button
          className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          Analysis Viewer (CSV)
        </button>
        <div className="theme-toggle-container">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
      <div className="content-area">{renderContent()}</div>
    </div>
  );
}

export default App;

