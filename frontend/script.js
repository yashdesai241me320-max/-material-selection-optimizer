const API_BASE = "http://localhost:5000/api";

let PROPERTIES = [];
let criteriaCount = 0;

const criteriaListEl = document.getElementById("criteriaList");
const categorySelect = document.getElementById("categorySelect");
const apiStatusEl = document.getElementById("apiStatus");
const resultsListEl = document.getElementById("resultsList");
const emptyStateEl = document.getElementById("emptyState");
const summaryStripEl = document.getElementById("summaryStrip");

async function init() {
  try {
    const [propsRes, healthRes] = await Promise.all([
      fetch(`${API_BASE}/properties`),
      fetch(`${API_BASE}/health`),
    ]);
    PROPERTIES = await propsRes.json();
    if (healthRes.ok) {
      apiStatusEl.textContent = "● Connected to backend";
      apiStatusEl.className = "api-status ok";
    }
    populateCategories();
    addCriterionRow("yield_strength", "max", 5);
    addCriterionRow("cost_per_kg", "min", 3);
    addCriterionRow("density", "min", 3);
  } catch (err) {
    apiStatusEl.textContent = "● Backend not reachable (start the Flask API on :5000)";
    apiStatusEl.className = "api-status err";
  }
}

async function populateCategories() {
  try {
    const res = await fetch(`${API_BASE}/materials`);
    const materials = await res.json();
    const categories = [...new Set(materials.map(m => m.category))];
    categories.forEach(cat => {
      const opt = document.createElement("option");
      opt.value = cat;
      opt.textContent = cat;
      categorySelect.appendChild(opt);
    });
  } catch (err) { /* handled by init() status already */ }
}

function addCriterionRow(defaultProp = null, defaultGoal = null, defaultWeight = 5) {
  criteriaCount++;
  const id = `criterion-${criteriaCount}`;

  const row = document.createElement("div");
  row.className = "criterion-row";
  row.dataset.id = id;

  const propOptions = PROPERTIES.map(p =>
    `<option value="${p.key}">${p.label} (${p.unit})</option>`
  ).join("");

  row.innerHTML = `
    <div class="criterion-row-top">
      <select class="prop-select">${propOptions}</select>
      <button class="remove-criterion" title="Remove">✕</button>
    </div>
    <div class="goal-toggle">
      <button type="button" class="goal-max">MAXIMIZE</button>
      <button type="button" class="goal-min">MINIMIZE</button>
    </div>
    <div class="weight-row" style="margin-top:10px;">
      <input type="range" min="1" max="10" value="${defaultWeight}" class="weight-slider" />
      <span class="weight-value">${defaultWeight}</span>
    </div>
  `;

  criteriaListEl.appendChild(row);

  const propSelect = row.querySelector(".prop-select");
  if (defaultProp) propSelect.value = defaultProp;

  const goalMaxBtn = row.querySelector(".goal-max");
  const goalMinBtn = row.querySelector(".goal-min");

  const setGoal = (goal) => {
    row.dataset.goal = goal;
    goalMaxBtn.classList.toggle("active", goal === "max");
    goalMinBtn.classList.toggle("active", goal === "min");
  };

  goalMaxBtn.addEventListener("click", () => setGoal("max"));
  goalMinBtn.addEventListener("click", () => setGoal("min"));

  // default goal: what the user passed in, or the property's own default
  const propMeta = PROPERTIES.find(p => p.key === propSelect.value);
  setGoal(defaultGoal || (propMeta ? propMeta.default_goal : "max"));

  propSelect.addEventListener("change", () => {
    const meta = PROPERTIES.find(p => p.key === propSelect.value);
    setGoal(meta ? meta.default_goal : "max");
  });

  const slider = row.querySelector(".weight-slider");
  const weightValue = row.querySelector(".weight-value");
  slider.addEventListener("input", () => { weightValue.textContent = slider.value; });

  row.querySelector(".remove-criterion").addEventListener("click", () => row.remove());
}

document.getElementById("addCriterionBtn").addEventListener("click", () => addCriterionRow());

function collectCriteria() {
  return [...criteriaListEl.querySelectorAll(".criterion-row")].map(row => ({
    property: row.querySelector(".prop-select").value,
    goal: row.dataset.goal,
    weight: parseInt(row.querySelector(".weight-slider").value, 10),
  }));
}

document.getElementById("runBtn").addEventListener("click", runOptimization);

async function runOptimization() {
  const criteria = collectCriteria();
  const category = categorySelect.value;
  const top_k = parseInt(document.getElementById("topKInput").value, 10) || 5;

  if (criteria.length === 0) {
    alert("Add at least one criterion first.");
    return;
  }

  const btn = document.getElementById("runBtn");
  btn.textContent = "RUNNING…";
  btn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, criteria, top_k }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");
    renderResults(data);
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    btn.textContent = "RUN OPTIMIZATION";
    btn.disabled = false;
  }
}

function renderResults(data) {
  emptyStateEl.style.display = "none";
  summaryStripEl.classList.remove("hidden");
  document.getElementById("totalCandidates").textContent = data.total_candidates;
  document.getElementById("paretoCount").textContent = data.pareto_optimal_count;

  resultsListEl.innerHTML = "";

  const maxScore = Math.max(...data.results.map(r => r.topsis_score), 0.0001);

  data.results.forEach(material => {
    const card = document.createElement("div");
    card.className = "result-card";

    const detailProps = Object.entries(material)
      .filter(([k]) => !["id", "topsis_score", "rank", "is_pareto_optimal", "name", "category"].includes(k))
      .map(([k, v]) => {
        const meta = PROPERTIES.find(p => p.key === k);
        const label = meta ? meta.label : k;
        const unit = meta ? meta.unit : "";
        return `<div class="detail-prop"><span class="k">${label}</span><span class="v">${v} ${unit}</span></div>`;
      }).join("");

    card.innerHTML = `
      <div class="result-top">
        <div class="rank-badge">${String(material.rank).padStart(2, "0")}</div>
        <div class="result-name-block">
          <div class="result-name">${material.name}</div>
          <div class="result-category">${material.category}</div>
        </div>
        ${material.is_pareto_optimal ? '<span class="pareto-tag">PARETO OPTIMAL</span>' : ''}
        <div class="score-block">
          <div class="score-value">${material.topsis_score.toFixed(3)}</div>
          <div class="score-label">TOPSIS score</div>
        </div>
      </div>
      <div class="score-bar-track">
        <div class="score-bar-fill" style="width:${(material.topsis_score / maxScore) * 100}%"></div>
      </div>
      <div class="detail-props">${detailProps}</div>
    `;

    card.addEventListener("click", () => card.classList.toggle("expanded"));
    resultsListEl.appendChild(card);
  });
}

init();
