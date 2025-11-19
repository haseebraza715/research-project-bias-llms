#!/usr/bin/env python3
"""
Web-based viewer for LLM bias experiment results.
Starts a local web server to display results from JSONL files.
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from typing import List, Dict

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Global data storage
experiment_data: List[Dict] = []
current_file: Path = None


def load_jsonl_file(file_path: Path) -> List[Dict]:
    """Load data from a JSONL file."""
    data = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    except Exception as e:
        print(f"Error loading file: {e}")
    return data


@app.route("/")
def index():
    """Main page."""
    return render_template("viewer.html")


@app.route("/api/data")
def get_data():
    """Get all experiment data."""
    return jsonify({
        "data": experiment_data,
        "total": len(experiment_data),
        "successful": sum(1 for d in experiment_data if "error" not in d),
        "errors": sum(1 for d in experiment_data if "error" in d),
    })


@app.route("/api/filter", methods=["POST"])
def filter_data():
    """Filter data based on criteria."""
    filters = request.json
    filtered = experiment_data.copy()
    
    if filters.get("model") and filters["model"] != "All":
        filtered = [d for d in filtered if d.get("model_id") == filters["model"]]
    
    if filters.get("profile") and filters["profile"] != "All":
        filtered = [d for d in filtered if d.get("profile_id") == filters["profile"]]
    
    if filters.get("condition") and filters["condition"] != "All":
        filtered = [d for d in filtered if d.get("condition_id") == filters["condition"]]
    
    if filters.get("search"):
        search_term = filters["search"].lower()
        filtered = [
            d for d in filtered
            if search_term in d.get("response_text", "").lower()
            or search_term in d.get("prompt_id", "").lower()
            or search_term in d.get("profile_id", "").lower()
        ]
    
    return jsonify({"data": filtered, "count": len(filtered)})


@app.route("/api/load_file", methods=["POST"])
def load_file():
    """Load a new JSONL file."""
    global experiment_data, current_file
    
    file_path = request.json.get("file_path")
    if not file_path:
        # Try to load latest file
        output_dir = Path(__file__).parent.parent / "outputs" / "raw"
        if output_dir.exists():
            jsonl_files = list(output_dir.glob("*.jsonl"))
            if jsonl_files:
                file_path = str(max(jsonl_files, key=lambda p: p.stat().st_mtime))
    
    if file_path and Path(file_path).exists():
        experiment_data = load_jsonl_file(Path(file_path))
        current_file = Path(file_path)
        
        # Get unique values for filters
        models = sorted(set(d.get("model_id", "Unknown") for d in experiment_data))
        profiles = sorted(set(d.get("profile_id", "Unknown") for d in experiment_data))
        conditions = sorted(set(d.get("condition_id", "Unknown") for d in experiment_data))
        
        return jsonify({
            "success": True,
            "file": str(current_file),
            "total": len(experiment_data),
            "models": models,
            "profiles": profiles,
            "conditions": conditions,
        })
    
    return jsonify({"success": False, "error": "File not found"})


@app.route("/api/files")
def list_files():
    """List available JSONL files."""
    output_dir = Path(__file__).parent.parent / "outputs" / "raw"
    if not output_dir.exists():
        return jsonify({"files": []})
    
    files = [
        {
            "path": str(f),
            "name": f.name,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime,
        }
        for f in output_dir.glob("*.jsonl")
    ]
    files.sort(key=lambda x: x["modified"], reverse=True)
    
    return jsonify({"files": files})


def main():
    # Load latest file on startup
    output_dir = Path(__file__).parent.parent / "outputs" / "raw"
    if output_dir.exists():
        jsonl_files = list(output_dir.glob("*.jsonl"))
        if jsonl_files:
            latest_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)
            global experiment_data, current_file
            experiment_data = load_jsonl_file(latest_file)
            current_file = latest_file
            print(f"Loaded {len(experiment_data)} records from {latest_file.name}")
    
    print("\n" + "="*60)
    print("LLM Bias Experiment Results Viewer")
    print("="*60)
    print(f"\nStarting web server...")
    print(f"Open your browser and go to: http://localhost:5000")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=False, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
