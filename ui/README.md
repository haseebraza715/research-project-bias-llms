# Bias LLM Agent - Experiment Viewer UI

A minimal React + TypeScript UI for inspecting experiment artifacts from the bias-llm-agent project.

## Features

- **Raw Viewer (JSONL)**: View and inspect raw experiment runs with full prompt and response details
- **Analysis Viewer (CSV)**: View aggregated analysis data in a table format with detailed metrics
- **Advanced Filtering**: Filter by persona, question, model, family, API model name, errors only, and text search
- **Sorting**: Sort by timestamp, persona ID, question ID, or model ID
- **Dark Theme**: Black background with white text only, minimal separators
- **Performance Optimized**: Renders first 2000 rows with lazy loading support

## Setup

1. Install dependencies:
```bash
cd ui
npm install
```

2. Copy data files to public directory:
```bash
./copy-data.sh
```

Or manually:
```bash
mkdir -p public/output/raw public/output/analysis
cp ../output/raw/runs.jsonl public/output/raw/runs.jsonl
cp ../output/analysis/runs.csv public/output/analysis/runs.csv
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

**Note**: If you update the source files in `../output/`, run `./copy-data.sh` again and restart the dev server.

## File Loading

The UI supports two loading modes:

### 1. Fetch from Server (Default)
- **Raw JSONL**: Tries to fetch from `/output/raw/runs.jsonl`
- **Analysis CSV**: Tries to fetch from `/output/analysis/runs.csv`

The files are automatically copied to `ui/public/output/` when you run the setup. If you update the source files in `../output/`, you'll need to copy them again:

```bash
cp ../output/raw/runs.jsonl public/output/raw/runs.jsonl
cp ../output/analysis/runs.csv public/output/analysis/runs.csv
```

### 2. File Upload (Fallback)
If fetching fails, the UI will show a file upload area. Click to upload:
- JSONL files for the Raw Viewer tab
- CSV files for the Analysis Viewer tab

## Vite Configuration

To serve the data files during development, you can configure Vite to serve static files from the parent directory. Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    fs: {
      allow: ['..']
    }
  },
  publicDir: '../output'
})
```

Alternatively, you can copy the output files to a `public` directory in the `ui` folder, or use a proxy configuration.

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
ui/
├── src/
│   ├── components/
│   │   ├── FilterBar.tsx      # Shared filter bar component
│   │   ├── RawViewer.tsx      # Raw JSONL viewer
│   │   └── AnalysisViewer.tsx # CSV analysis viewer
│   ├── utils/
│   │   ├── loadJsonl.ts       # JSONL file loader
│   │   ├── loadCsv.ts         # CSV file parser
│   │   ├── filtering.ts       # Filter and sort utilities
│   │   └── csvExport.ts       # CSV export functionality
│   ├── types.ts               # TypeScript type definitions
│   ├── App.tsx                # Main app component
│   ├── main.tsx               # Entry point
│   └── styles.css             # Dark theme styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## CSV Schema

The Analysis CSV must contain these columns (in order):

- timestamp
- persona_id
- question_id
- model_id
- model_family
- api_model_name
- has_error
- status_code
- response_text_length
- persona_leakage_detected
- persona_leakage_count
- roleplay_adoption_detected
- roleplay_adoption_count
- refusal_flag_detected
- refusal_flag_count
- harmful_content_flag_detected
- harmful_content_flag_count
- hedging_count
- hedging_per_100_words
- certainty_count
- certainty_per_100_words
- moral_language_count
- moral_language_per_100_words
- prescriptive_verbs_count
- prescriptive_verbs_per_100_words
- prompt_tokens
- completion_tokens
- total_tokens

## Usage

1. **Switch Tabs**: Click between "Raw Viewer (JSONL)" and "Analysis Viewer (CSV)" tabs
2. **Filter Data**: Use the filter bar to narrow down results by persona, question, model, etc.
3. **Search**: Use the search box for text-based filtering
4. **Sort**: Select a sort option from the dropdown
5. **View Details**: 
   - Raw Viewer: Click a record in the left list to view full details on the right
   - Analysis Viewer: Click a table row to open a detail drawer
6. **Export**: Click "Download filtered CSV" in the Analysis Viewer to export filtered data

## Styling

The UI uses a strict dark theme:
- Background: Black (#000000)
- Text: White (#ffffff)
- No accent colors
- Low-opacity white separators only
- Monospace font for code/prompts/JSON

