#!/bin/bash
# Script to copy data files from parent directory to public directory

mkdir -p public/output/raw public/output/analysis

if [ -f "../output/raw/runs.jsonl" ]; then
  cp ../output/raw/runs.jsonl public/output/raw/runs.jsonl
  echo "✓ Copied runs.jsonl"
else
  echo "✗ Source file not found: ../output/raw/runs.jsonl"
fi

if [ -f "../output/analysis/runs.csv" ]; then
  cp ../output/analysis/runs.csv public/output/analysis/runs.csv
  echo "✓ Copied runs.csv"
else
  echo "✗ Source file not found: ../output/analysis/runs.csv"
fi

echo "Done! Restart the dev server if it's running."

