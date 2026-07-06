"""
algorithms.py
--------------------------------------------------------------
The DSA core of the Material Selection Optimizer.

Three algorithms, each solving a distinct part of the multi-criteria
decision making (MCDM) problem:

1. skyline_filter()   -> Pareto-dominance / Skyline computation
                         (classic multi-objective database algorithm)
                         Complexity: O(n^2 * k)  n = materials, k = criteria

2. topsis_rank()      -> Technique for Order Preference by Similarity
                         to Ideal Solution. Normalizes the decision
                         matrix, builds an ideal & anti-ideal solution,
                         ranks by relative closeness.
                         Complexity: O(n * k)

3. top_k_heap()       -> Min-heap based Top-K selection instead of a
                         full O(n log n) sort when only the best K
                         candidates are needed.
                         Complexity: O(n log k)
--------------------------------------------------------------
"""

import heapq
import math


def dominates(a, b, criteria):
    """
    Returns True if material `a` dominates material `b` across all
    given criteria (a is at least as good on every criterion, and
    strictly better on at least one).

    criteria: list of dicts -> {"property": str, "goal": "max"|"min"}
    """
    at_least_as_good_everywhere = True
    strictly_better_somewhere = False

    for c in criteria:
        prop, goal = c["property"], c["goal"]
        av, bv = a[prop], b[prop]

        if goal == "max":
            if av < bv:
                at_least_as_good_everywhere = False
            if av > bv:
                strictly_better_somewhere = True
        else:  # "min"
            if av > bv:
                at_least_as_good_everywhere = False
            if av < bv:
                strictly_better_somewhere = True

    return at_least_as_good_everywhere and strictly_better_somewhere


def skyline_filter(materials, criteria):
    """
    Pareto-optimal (skyline) set: a material is kept only if no other
    material dominates it on every selected criterion simultaneously.

    This is the classic 'Block Nested Loop' skyline algorithm used in
    multi-objective database queries (e.g. "find hotels that are both
    cheap AND close to the beach" -> here: "find materials that are
    both light AND strong AND cheap").
    """
    skyline = []
    for i, candidate in enumerate(materials):
        dominated = False
        for j, other in enumerate(materials):
            if i == j:
                continue
            if dominates(other, candidate, criteria):
                dominated = True
                break
        if not dominated:
            skyline.append(candidate)
    return skyline


def _normalize_column(values):
    """Vector normalization: x_ij / sqrt(sum(x_ij^2)) -- used by TOPSIS."""
    denom = math.sqrt(sum(v * v for v in values)) or 1e-9
    return [v / denom for v in values]


def topsis_rank(materials, criteria):
    """
    TOPSIS multi-criteria ranking.

    Steps:
      1. Build decision matrix (rows = materials, cols = criteria)
      2. Vector-normalize each column
      3. Apply user-supplied weights
      4. Determine ideal best (A+) and ideal worst (A-) per column,
         respecting each criterion's max/min goal
      5. Compute Euclidean distance of every material from A+ and A-
      6. Closeness coefficient C = D- / (D+ + D-);  rank descending

    Returns materials annotated with `topsis_score` and `rank`.
    """
    if not materials:
        return []

    props = [c["property"] for c in criteria]
    weights = [c["weight"] for c in criteria]
    goals = [c["goal"] for c in criteria]

    # 1 + 2: normalize each criterion column across all materials
    normalized_cols = []
    for p in props:
        col = [m[p] for m in materials]
        normalized_cols.append(_normalize_column(col))

    # 3: apply weights -> weighted normalized matrix, per material
    weighted = []
    for idx in range(len(materials)):
        row = [normalized_cols[c][idx] * weights[c] for c in range(len(props))]
        weighted.append(row)

    # 4: ideal best / worst per column
    ideal_best, ideal_worst = [], []
    for c in range(len(props)):
        col_vals = [row[c] for row in weighted]
        if goals[c] == "max":
            ideal_best.append(max(col_vals))
            ideal_worst.append(min(col_vals))
        else:
            ideal_best.append(min(col_vals))
            ideal_worst.append(max(col_vals))

    # 5 + 6: distances and closeness coefficient
    results = []
    for idx, m in enumerate(materials):
        row = weighted[idx]
        d_pos = math.sqrt(sum((row[c] - ideal_best[c]) ** 2 for c in range(len(props))))
        d_neg = math.sqrt(sum((row[c] - ideal_worst[c]) ** 2 for c in range(len(props))))
        closeness = d_neg / (d_pos + d_neg) if (d_pos + d_neg) > 0 else 0.0

        enriched = dict(m)
        enriched["topsis_score"] = round(closeness, 6)
        results.append(enriched)

    results.sort(key=lambda x: x["topsis_score"], reverse=True)
    for rank, r in enumerate(results, start=1):
        r["rank"] = rank

    return results


def top_k_heap(scored_materials, k):
    """
    Selects the top-K materials by topsis_score using a min-heap of
    size K, rather than sorting the entire list.

    Why it matters: when the candidate pool is large and only the top
    K results are shown to the user, this runs in O(n log k) instead
    of O(n log n) for a full sort.
    """
    heap = []
    for m in scored_materials:
        entry = (m["topsis_score"], m)
        if len(heap) < k:
            heapq.heappush(heap, entry)
        elif entry[0] > heap[0][0]:
            heapq.heapreplace(heap, entry)

    top = [item[1] for item in heap]
    top.sort(key=lambda x: x["topsis_score"], reverse=True)
    return top
