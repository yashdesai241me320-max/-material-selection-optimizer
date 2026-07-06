"""
app.py — Material Selection Optimizer API

Endpoints
---------
GET  /api/health              -> liveness check
GET  /api/materials           -> all materials in the DB
GET  /api/properties          -> metadata describing comparable properties
POST /api/compare             -> runs Skyline + TOPSIS + Top-K pipeline

POST /api/compare body:
{
  "category": "All" | "Ferrous" | "Non-Ferrous" | "Polymer" | "Composite" | "Ceramic",
  "criteria": [
     {"property": "yield_strength", "weight": 0.4, "goal": "max"},
     {"property": "cost_per_kg",    "weight": 0.3, "goal": "min"},
     {"property": "density",        "weight": 0.3, "goal": "min"}
  ],
  "top_k": 5
}
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

from algorithms import skyline_filter, topsis_rank, top_k_heap

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "material_optimizer"),
}

PROPERTY_METADATA = [
    {"key": "density", "label": "Density", "unit": "kg/m3", "default_goal": "min"},
    {"key": "yield_strength", "label": "Yield Strength", "unit": "MPa", "default_goal": "max"},
    {"key": "ultimate_tensile_strength", "label": "Ultimate Tensile Strength", "unit": "MPa", "default_goal": "max"},
    {"key": "youngs_modulus", "label": "Young's Modulus (Stiffness)", "unit": "GPa", "default_goal": "max"},
    {"key": "cost_per_kg", "label": "Cost", "unit": "INR/kg", "default_goal": "min"},
    {"key": "thermal_conductivity", "label": "Thermal Conductivity", "unit": "W/m.K", "default_goal": "max"},
    {"key": "corrosion_resistance", "label": "Corrosion Resistance", "unit": "1-10 rating", "default_goal": "max"},
    {"key": "melting_point", "label": "Melting Point", "unit": "°C", "default_goal": "max"},
    {"key": "hardness_bhn", "label": "Hardness", "unit": "BHN", "default_goal": "max"},
]


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_materials(category=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if category and category != "All":
        cursor.execute("SELECT * FROM materials WHERE category = %s", (category,))
    else:
        cursor.execute("SELECT * FROM materials")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/materials")
def materials():
    category = request.args.get("category")
    return jsonify(fetch_materials(category))


@app.route("/api/properties")
def properties():
    return jsonify(PROPERTY_METADATA)


@app.route("/api/compare", methods=["POST"])
def compare():
    payload = request.get_json(force=True)
    category = payload.get("category", "All")
    criteria = payload.get("criteria", [])
    top_k = int(payload.get("top_k", 5))

    if not criteria:
        return jsonify({"error": "At least one criterion is required."}), 400

    # normalize weights to sum to 1
    total_weight = sum(c["weight"] for c in criteria) or 1.0
    for c in criteria:
        c["weight"] = c["weight"] / total_weight

    candidates = fetch_materials(category)
    if not candidates:
        return jsonify({"error": "No materials found for the selected category."}), 404

    # 1. Pareto-optimal filtering (Skyline algorithm)
    skyline_set = skyline_filter(candidates, criteria)
    skyline_ids = {m["id"] for m in skyline_set}

    # 2. TOPSIS ranking over the FULL candidate pool (so non-skyline
    #    materials still get a score for comparison / transparency)
    ranked = topsis_rank(candidates, criteria)
    for m in ranked:
        m["is_pareto_optimal"] = m["id"] in skyline_ids

    # 3. Top-K selection via min-heap
    top_results = top_k_heap(ranked, top_k)

    return jsonify({
        "criteria_used": criteria,
        "total_candidates": len(candidates),
        "pareto_optimal_count": len(skyline_set),
        "results": top_results,
        "full_ranking": ranked,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
