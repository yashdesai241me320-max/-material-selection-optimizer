# Material Selection Optimizer

A full-stack decision-support tool for engineers choosing between candidate
materials against multiple, often conflicting, criteria (strength, weight,
cost, corrosion resistance, etc.).

**Stack:** Flask (Python) REST API · MySQL · vanilla HTML/CSS/JS frontend

## Why this project is interesting (for interviews)

Most "material selection" tools are just a filtered SQL query. This one runs
an actual multi-criteria decision-making (MCDM) pipeline:

1. **Skyline / Pareto-dominance filtering** (`algorithms.py::skyline_filter`)
   A material is only kept if no other material beats it on *every* selected
   criterion at once. Classic multi-objective database algorithm (same idea
   behind "find hotels that are cheap AND close to the beach"). O(n²·k).

2. **TOPSIS ranking** (`algorithms.py::topsis_rank`)
   Vector-normalizes the decision matrix, applies user-supplied weights,
   computes each material's Euclidean distance to an ideal and anti-ideal
   solution, and ranks by relative closeness. O(n·k).

3. **Min-heap Top-K selection** (`algorithms.py::top_k_heap`)
   Rather than fully sorting every candidate, a size-K min-heap keeps only
   the current best K as it streams through — O(n log k) instead of
   O(n log n).

## Setup

### 1. Database
```bash
mysql -u root -p < backend/db_schema.sql
```
This creates the `material_optimizer` database and seeds it with 26 real
engineering materials (steels, aluminium alloys, titanium, polymers,
composites, ceramics) with 9 properties each.

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# set your MySQL credentials if not using defaults (root / no password)
export DB_USER=root
export DB_PASSWORD=yourpassword

python app.py
```
API runs at `http://localhost:5000`.

### 3. Frontend
Just open `frontend/index.html` in a browser, or serve it:
```bash
cd frontend
python -m http.server 8000
```
Then visit `http://localhost:8000`.

## API

| Method | Endpoint          | Description                              |
|--------|-------------------|-------------------------------------------|
| GET    | `/api/health`     | Liveness check                            |
| GET    | `/api/materials`  | All materials (optional `?category=`)     |
| GET    | `/api/properties` | Property metadata (label, unit, goal)     |
| POST   | `/api/compare`    | Runs skyline + TOPSIS + top-K pipeline    |

**POST /api/compare** body:
```json
{
  "category": "All",
  "criteria": [
    {"property": "yield_strength", "weight": 5, "goal": "max"},
    {"property": "cost_per_kg", "weight": 3, "goal": "min"},
    {"property": "density", "weight": 3, "goal": "min"}
  ],
  "top_k": 5
}
```

## Project structure
```
material-selection-optimizer/
├── backend/
│   ├── app.py            # Flask API
│   ├── algorithms.py     # Skyline, TOPSIS, min-heap top-K
│   ├── db_schema.sql     # MySQL schema + 26-material seed data
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

## Suggested resume bullet

> Built a full-stack material selection optimizer (Flask, MySQL, JS) implementing
> Pareto-dominance skyline filtering and TOPSIS multi-criteria ranking with
> min-heap top-K selection, enabling engineers to trade off strength, weight,
> cost, and corrosion resistance across 25+ engineering materials.

## Possible extensions
- Add a materials-substitution graph (Dijkstra) for "closest alternative if X is unavailable"
- Radar chart per material using Chart.js for visual property comparison
- User accounts + saved comparison sessions (adds a second SQL table + auth)
- Export ranked results to PDF/Excel report
