# Material Selection Optimizer

A full-stack decision-support tool for engineers choosing between candidate
materials against multiple, often conflicting, criteria (strength, weight,
cost, corrosion resistance, etc.).

**Stack:** Flask (Python) REST API · MySQL · vanilla HTML/CSS/JS frontend



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


## Possible extensions
- Add a materials-substitution graph (Dijkstra) for "closest alternative if X is unavailable"
- Radar chart per material using Chart.js for visual property comparison
- User accounts + saved comparison sessions (adds a second SQL table + auth)
- Export ranked results to PDF/Excel report
