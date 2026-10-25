"""Deterministic worked-example functions for
"Ahimsa in Agentic AI: Algorithmic Non-Violence and the Architecture of
Compassionate Code" by Dr. Sri Amit Ray (Compassionate AI Lab, 2026).
ISBN 978-81-69641-29-6 (First Edition, 2026).

Every function is pure and reproducible: no randomness, no network, no
wall-clock inputs. The worked examples in the book quote these outputs.
The inputs are small illustrative numbers chosen to show the reasoning
of each chapter; replace them with values measured in your own
deployment before using any function for planning.

Run:   python models_ahimsa_in_agentic_ai.py
Test:  python -m unittest test_models.py
"""
from __future__ import annotations

import math

DIMENSIONS = ("physical", "psychological", "rights", "integrity")


def _finite(x, lo=None):
    """True for a real, finite number (bool excluded) not below lo."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    if not math.isfinite(x):
        return False
    return lo is None or x >= lo


def within_ceilings(vector, ceilings):
    """Componentwise test H_j <= eps_j.  Missing, non-finite or negative
    values never pass; neither does a vector of the wrong length."""
    if len(vector) != len(ceilings) or not ceilings:
        return False
    return all(_finite(h, 0.0) and _finite(e, 0.0) and h <= e
               for h, e in zip(vector, ceilings))


# ---------------------------------------------------------------- ch01
def ch01_harm_vector(raw=(0.10, 0.20, 0.05, 0.30),
                     weights=(1.0, 1.0, 1.5, 1.0),
                     ceilings=(0.05, 0.05, 0.02, 0.10)):
    """Publishing support conversations: weighted harm per dimension
    H_j = w_j * raw_j against its ceiling.  Returns (H, violations)."""
    h = tuple(round(w * r, 4) for w, r in zip(weights, raw))
    return h, [x > e for x, e in zip(h, ceilings)]


def ch01_inaction(fall_risk=0.12, alert=(0.01, 0.03, 0.01, 0.01),
                  ceilings=(0.05, 0.10, 0.10, 0.10)):
    """The harm of inaction: a monitoring agent sees a rising fall risk.
    Doing nothing carries physical harm fall_risk; alerting the
    caregiver carries the small alert vector.  Returns
    (inaction passes, alert passes)."""
    idle = (fall_risk, 0.0, 0.0, 0.0)
    return within_ceilings(idle, ceilings), within_ceilings(alert, ceilings)


# ---------------------------------------------------------------- ch02
def ch02_cascade(e0=0.02, r=1.6, suppress=0.25, n=6):
    """Error after t unattended iterations, without and with an
    intermediate check that keeps a quarter of the amplified error."""
    plain = [round(e0 * r ** t, 4) for t in range(1, n + 1)]
    guard = [round(e0 * (r * suppress) ** t, 4) for t in range(1, n + 1)]
    return plain, guard


def ch02_window(p_step=0.02, irreversible=4, tools=12, steps=6, review=2):
    """Chance that an unreviewed window contains at least one erroneous
    irreversible write, for a window of `steps` and of `review` steps.
    Returns (per-step chance, P(window=steps), P(window=review))."""
    p = p_step * irreversible / tools
    return (round(p, 5), round(1 - (1 - p) ** steps, 4),
            round(1 - (1 - p) ** review, 4))


# ---------------------------------------------------------------- ch03
def ch03_penalty(lam, scale=1.0):
    """Soft score R - lambda*H for the aggressive and the protective plan
    (rewards optionally rescaled).  Returns (aggressive, protective)."""
    return (round(100 * scale - lam * 40, 2), round(60 * scale - lam * 2, 2))


def ch03_crossover(scale=1.0):
    """Penalty at which the two soft scores are equal."""
    return round((100 - 60) * scale / (40 - 2), 4)


def ch03_gate(harm=(40, 2), ceiling=5):
    """Hard test: harm at or below the ceiling."""
    return [h <= ceiling for h in harm]


# ---------------------------------------------------------------- ch04
def ch04_lexicographic(options=(("A", 0.04, 0.90), ("B", 0.01, 0.70),
                                ("C", 0.01, 0.75), ("D", 0.07, 0.95)),
                       ceiling=0.05):
    """Postulate 3: among feasible options, least severe harm first, then
    utility.  Returns (feasible names, lexicographic pick, pure-utility
    pick among feasible, pure-utility pick overall)."""
    feas = [o for o in options if o[1] <= ceiling]
    lex = min(feas, key=lambda o: (o[1], -o[2]))[0]
    util_feas = max(feas, key=lambda o: o[2])[0]
    util_all = max(options, key=lambda o: o[2])[0]
    return [o[0] for o in feas], lex, util_feas, util_all


def ch04_uncertainty_default(confidence, threshold=0.80):
    """Postulate 2: below the confidence threshold, the loop takes the
    state-preserving branch.  A missing, non-finite or out-of-range
    confidence is not a high one: it takes the protective branch too.
    The threshold is policy and must be a finite value in [0, 1]."""
    if not _finite(threshold, 0.0) or threshold > 1.0:
        raise ValueError("threshold must be a finite value in [0, 1]")
    if not _finite(confidence, 0.0) or confidence > 1.0:
        return "preserve-and-escalate"
    return "execute" if confidence >= threshold else "preserve-and-escalate"


# ---------------------------------------------------------------- ch05
def ch05_horizon(d=(0.02, 0.04, 0.10, 0.15, 0.22, 0.30), b=(0.05,) * 6,
                 gam=0.9, ceiling=0.30):
    """Time-decayed totals of plans D and B.  Returns
    (H_D, H_B, ratio, undecayed D, undecayed B, D passes, B passes)."""
    hd = sum(gam ** (t + 1) * x for t, x in enumerate(d))
    hb = sum(gam ** (t + 1) * x for t, x in enumerate(b))
    return (round(hd, 4), round(hb, 4), round(hd / hb, 2),
            round(sum(d), 2), round(sum(b), 2), hd <= ceiling, hb <= ceiling)


def ch05_margin(estimate=0.07, margin=0.02, vuln=1.25, ceiling=0.10):
    """Conservative check U = v*(h + m) <= eps.  Returns
    (point estimate passes, U, U passes)."""
    u = round(vuln * (estimate + margin), 4)
    return estimate <= ceiling, u, u <= ceiling


def ch05_empty_set(candidates=(("reschedule-all", (0.02, 0.12, 0.04, 0.03)),
                               ("auto-cancel", (0.01, 0.15, 0.06, 0.02)),
                               ("bulk-notify", (0.01, 0.04, 0.14, 0.05))),
                   fallbacks=(("hold-and-ask", (0.00, 0.03, 0.01, 0.01)),
                              ("narrow-to-urgent", (0.01, 0.06, 0.03, 0.02))),
                   ceilings=(0.05, 0.10, 0.10, 0.10)):
    """Empty feasible set: no ordinary candidate passes, so pre-authorized
    protective fallbacks are evaluated against the same ceilings.
    Returns (feasible candidates, feasible fallbacks)."""
    feas = [n for n, h in candidates if within_ceilings(h, ceilings)]
    fb = [n for n, h in fallbacks if within_ceilings(h, ceilings)]
    return feas, fb


# ---------------------------------------------------------------- ch06
def ch06_scalar_vs_vector(h=(0.12, 0.00, 0.00, 0.00),
                          ceilings=(0.05, 0.10, 0.10, 0.10)):
    """A single total budget compensates across dimensions; componentwise
    ceilings do not.  Returns (sum H, sum eps, scalar passes,
    componentwise passes)."""
    return (round(sum(h), 2), round(sum(ceilings), 2),
            sum(h) <= sum(ceilings), within_ceilings(h, ceilings))


def ch06_hazard_matrix(register=(("direct", "rights"), ("indirect", "rights"),
                                 ("indirect", "psychological"),
                                 ("structural", "rights"),
                                 ("structural", "psychological"),
                                 ("neglect", "integrity"),
                                 ("neglect", "rights"))):
    """Count register entries per causal row and per outcome column of the
    4 x 4 hazard matrix.  Returns (rows, columns, empty cells)."""
    causes = ("direct", "indirect", "structural", "neglect")
    rows = {c: sum(1 for r, _ in register if r == c) for c in causes}
    cols = {d: sum(1 for _, k in register if k == d) for d in DIMENSIONS}
    cells = {(c, d) for c, d in register}
    return rows, cols, 16 - len(cells)


def ch06_counterfactual(p_a=(0.70, 0.20, 0.10), p_b=(0.85, 0.12, 0.03),
                        loss=(0.0, 0.2, 0.9)):
    """Expected harm difference Delta = E_a[l] - E_b[l] over three
    outcome states (fine, delayed, injured)."""
    ea = sum(p * l for p, l in zip(p_a, loss))
    eb = sum(p * l for p, l in zip(p_b, loss))
    return round(ea, 4), round(eb, 4), round(ea - eb, 4)


# ---------------------------------------------------------------- ch07
CQ_INPUTS = (((0.70, 0.02, 0.03, 1), (0.60, 0.02, 0.03, 1), (0.20, 0.10, 0.60, 3)),
             ((0.50, 0.02, 0.03, 1), (0.50, 0.02, 0.03, 1), (0.45, 0.04, 0.06, 3)))


def ch07_cq(inputs=CQ_INPUTS, extra=1.5, stab=1e-9):
    """Vulnerability-weighted Compassion Quotient per policy.  Rows are
    (benefit, suffering, harm, cost weight).  Returns per policy
    (benefit, weighted cost, raw CQ, bounded CQ01, unweighted net)."""
    out = []
    for rows in inputs:
        ben = sum(b for b, s, h, v in rows)
        cost = sum(extra * v * (s + h) for b, s, h, v in rows)
        cq = ben / (cost + stab)
        out.append((round(ben, 2), round(cost, 2), round(cq, 2),
                    round(cq / (1 + cq), 2),
                    round(sum(b - s - h for b, s, h, v in rows), 2)))
    return out


def ch07_minimax(u=(0.30, 0.20, 0.90), v=(0.50, 0.40, 0.60)):
    """Protect the most vulnerable: smaller worst harm wins.
    Returns (max U, max V, mean U, mean V, choice)."""
    choice = "U" if max(u) < max(v) else "V"
    return (max(u), max(v), round(sum(u) / len(u), 4),
            round(sum(v) / len(v), 4), choice)


def ch07_error_weighting(cost_false_denial=5.0, cost_false_grant=1.0,
                         p_eligible=0.30):
    """Opposite-direction error weighting: grant when the probability of
    eligibility reaches c_FG / (c_FG + c_FD).  Returns (threshold,
    decision with weighting, decision at the symmetric 0.5)."""
    t = cost_false_grant / (cost_false_grant + cost_false_denial)
    return (round(t, 4), "grant" if p_eligible >= t else "deny",
            "grant" if p_eligible >= 0.5 else "deny")


# ---------------------------------------------------------------- ch08
def ch08_authority(step_seconds=40, window_steps=10, escalation_p95=420):
    """Is human authority real?  The p95 time to a human decision must not
    exceed the autonomy window.  Returns (window in seconds, authority
    real?, smallest window in steps that the current latency fits)."""
    window = step_seconds * window_steps
    needed = math.ceil(escalation_p95 / step_seconds)
    return window, escalation_p95 <= window, needed


def ch08_ledger_completeness(fields_present=6, fields_required=7):
    """Responsibility ledger: an action is ready for autonomous execution
    only when every required field is present."""
    return fields_present == fields_required, fields_required - fields_present


# ---------------------------------------------------------------- ch09
CAI_WEIGHTS = (0.20, 0.15, 0.10, 0.15, 0.15, 0.10, 0.15)


def ch09_cai(scores=(0.70, 0.60, 0.80, 0.70, 0.30, 0.55, 0.70),
             weights=CAI_WEIGHTS, floors=(0.50, 0.40, 0.50)):
    """Compassionate AI Index and the three protection floors on VP, PC
    and FG (score positions 5, 6, 7).  Returns (CAI, floors pass)."""
    cai = round(sum(s * w for s, w in zip(scores, weights)), 4)
    vp, pc, fg = scores[4], scores[5], scores[6]
    return cai, vp >= floors[0] and pc >= floors[1] and fg >= floors[2]


def ch09_weight_attack(scores=(0.70, 0.60, 0.80, 0.70, 0.30, 0.55, 0.70)):
    """Shifting weight away from VP raises the index but cannot pass the
    floor.  Returns (CAI with VP weight 0.05 and CQ weight 0.30,
    floors pass)."""
    w = (0.30, 0.15, 0.10, 0.15, 0.05, 0.10, 0.15)
    return ch09_cai(scores, w)


# ---------------------------------------------------------------- ch10
TOOL_CALLS = {"notify-clinician": (0.01, 0.02, 0.01, 0.02),
              "read-public-report": (0.02, 0.01, 0.03, 0.05),
              "send-patient-summary": (0.02, 0.10, 0.30, 0.05),
              "publish-dataset": (0.02, 0.15, 0.60, 0.20),
              "override-device-cmd": (0.70, 0.10, 0.10, 0.40)}


def ch10_filter(calls=TOOL_CALLS, eps=(0.05, 0.10, 0.10, 0.10),
                escalate_physical=True):
    """Disposition per tool call: permit if every component passes;
    escalate if the physical ceiling is breached (direct severe harm);
    otherwise reformulate."""
    out = {}
    for name, h in calls.items():
        if within_ceilings(h, eps):
            out[name] = "permit"
        elif escalate_physical and h[0] > eps[0]:
            out[name] = "escalate"
        else:
            out[name] = "reformulate"
    return out


def ch10_path_coverage(paths=7, gated=5):
    """Share of consequential execution paths that cross the gate."""
    return round(gated / paths, 2), paths - gated


# ---------------------------------------------------------------- ch11
def ch11_restricted_game(floor=4.5):
    """Joint profiles left when each payoff must reach the floor."""
    game = {("C", "C"): (8, 8), ("C", "D"): (2, 10),
            ("D", "C"): (10, 2), ("D", "D"): (4, 4)}
    return [k for k, p in game.items() if min(p) >= floor]


def ch11_allocation(pool=6.0, demand=(5.0, 5.0), share_v=0.40, floor_v=3.0):
    """Utilization-first split versus a floor for the vulnerable class V.
    Returns ((V, S) before, (V, S) after, (served share before, after))."""
    v0 = pool * share_v
    v1 = max(v0, floor_v)
    return ((round(v0, 2), round(pool - v0, 2)), (v1, pool - v1),
            (round(v0 / demand[0], 2), round(v1 / demand[0], 2)))


def ch11_correlated_pair(p=0.04, rho=0.18):
    """Two agents sharing a dependency: independent pair p^2 versus the
    exact Pearson joint failure p^2 + rho*p*(1-p)."""
    return round(p * p, 4), round(p * p + rho * p * (1 - p), 6)


# ---------------------------------------------------------------- ch12
DRIFT = (0.4, 0.6, 0.9, 1.1, 1.5, 1.8, 2.2, 2.6, 3.2, 3.6)


def ch12_breaker(z=DRIFT, threshold=3.0, warn=2.0):
    """First week the drift reading exceeds the threshold, and the first
    week it enters the warning band."""
    fire = next((w for w, x in enumerate(z, 1) if x > threshold), None)
    first_warn = next((w for w, x in enumerate(z, 1) if x > warn), None)
    return fire, first_warn


def ch12_degraded_capacity(volume=150, review_share=0.30, reviewers=40):
    """Degraded mode routes a share of actions to human review.
    Returns (reviews needed per hour, backlog per hour, share that
    capacity supports)."""
    need = volume * review_share
    return (round(need, 1), round(max(0.0, need - reviewers), 1),
            round(reviewers / volume, 4))


# ---------------------------------------------------------------- ch13
GROUPS = (("urban documented", 4000, 3600, True),
          ("urban undocumented", 220, 30, False),
          ("rural language-minority", 900, 610, True),
          ("rural remote", 700, 240, False))


def ch13_exclusion(groups=GROUPS):
    """Exclusion error by subgroup.  Returns (missing per group, missing
    rates, total missing, missing inside unaudited groups)."""
    missing = [e - n for _, e, n, _ in groups]
    rates = [round((e - n) / e, 4) for _, e, n, _ in groups]
    unaudited = sum(e - n for _, e, n, a in groups if not a)
    return missing, rates, sum(missing), unaudited


def ch13_applicant_view(groups=GROUPS, applicants=4870):
    """Headline metric on applicants only versus the enrolled share of
    all eligible people.  Returns (applicants, enrolled, eligible,
    served share of applicants, enrolled share of eligible)."""
    eligible = sum(e for _, e, _, _ in groups)
    enrolled = sum(n for _, _, n, _ in groups)
    return (applicants, enrolled, eligible, round(enrolled / applicants, 2),
            round(enrolled / eligible, 2))


def ch13_alerts(alerts=(60, 25), precision=(0.15, 0.40)):
    """Alert fatigue: true alerts per shift for two alert policies."""
    return [round(a * p, 1) for a, p in zip(alerts, precision)]


# ---------------------------------------------------------------- ch14
def ch14_stopping(v=1.2, latency=0.20, decel=0.8, buffer=0.15, clearance=1.5):
    """Forward stopping distance v*t + v^2/(2a) + b and the largest speed
    that fits the clearance.  Returns (required, remaining, v_max)."""
    req = v * latency + v * v / (2 * decel) + buffer
    vmax = -decel * latency + math.sqrt((decel * latency) ** 2
                                        + 2 * decel * (clearance - buffer))
    return round(req, 2), round(clearance - req, 2), round(vmax, 3)


def ch14_amplification(k=1.15, cycles=(4, 10)):
    """Response level x_t = k^(t-1) with x_1 = 1."""
    return [round(k ** (c - 1), 2) for c in cycles]


def ch14_zone_floor(capacity=100, demand=(70, 50, 20),
                    history=(0.55, 0.40, 0.05), floor_share=0.60):
    """Delivery floor.  A utilization-first planner splits capacity by
    historical order share; the floor guarantees low-density zone 3 at
    least floor_share of its demand and splits the rest by history.
    Returns (before, after, zone 3 served share before and after)."""
    before = [round(capacity * h, 1) for h in history]
    z3 = max(before[2], floor_share * demand[2])
    rest = capacity - z3
    tot = history[0] + history[1]
    after = [round(rest * history[0] / tot, 1),
             round(rest * history[1] / tot, 1), round(z3, 1)]
    return before, after, (round(before[2] / demand[2], 2),
                           round(after[2] / demand[2], 2))


# ---------------------------------------------------------------- ch15
def ch15_contestation(appeals=120, beyond_bound=18):
    """Share of appeals answered after the response-time bound."""
    return round(beyond_bound / appeals, 3)


def ch15_maturity(counts=(3, 3, 2, 1, 0), needed=2):
    """A level counts only if it and every level below it have at least
    `needed` working controls.  Returns (level reached, next gap)."""
    level = 0
    for c in counts:
        if c >= needed:
            level += 1
        else:
            break
    return level, (level + 1 if level < len(counts) else None)


# ---------------------------------------------------------------- ch16
def ch16_audit(actions=340000, violations=12, near=850, reached=62000,
               affected=100000, coverage_floor=0.80):
    """Audit pack rates per million, ratio, coverage and its floor."""
    cov = reached / affected
    return (round(violations / actions * 1e6, 1), round(near / actions * 1e6, 1),
            round(near / violations, 1), round(cov, 2), cov >= coverage_floor)


def ch16_near_band(ratios=(0.42, 0.81, 0.95, 1.07, 0.55, 0.99, 0.80, 0.30,
                           1.20, 0.88), low=0.8):
    """Classify checks by U/eps: near-threshold band (low, 1], violations
    above 1, the rest clear."""
    near = sum(1 for r in ratios if low < r <= 1.0)
    viol = sum(1 for r in ratios if r > 1.0)
    return near, viol, len(ratios) - near - viol


# ---------------------------------------------------------------- ch17
def ch17_gap(c=1.35, r=1.12, years=5):
    """Capability and constraint indices after n years, their gap, and
    the constraint index as a share of capability."""
    cap, con = c ** years, r ** years
    return round(cap, 2), round(con, 2), round(cap / con, 2), round(con / cap, 2)


def ch17_required_rate(c=1.35, years=5, min_share=0.80):
    """Constraint growth needed to keep the share at min_share."""
    return round(c * min_share ** (1.0 / years), 4)


# ---------------------------------------------------------------- ch18
def ch18_floor_review(bindings=(("VP", 14), ("PC", 0), ("FG", 2))):
    """Floors that never bound in a year are flagged for review."""
    return [name for name, n in bindings if n == 0]


def ch18_commitments(evidenced=6, total=10):
    """Share of the ten commitments with working evidence."""
    return round(evidenced / total, 2)


# ------------------------------------------------------------ appendix D
def appendix_d_upper(est=(0.01, 0.02, 0.02, 0.01),
                     margin=(0.005, 0.01, 0.02, 0.01), vuln=1.5,
                     ceilings=(0.05, 0.10, 0.10, 0.10)):
    """Checked vector v*(h + m) for the minimized reminder template."""
    u = tuple(round(vuln * (h + m), 4) for h, m in zip(est, margin))
    return u, within_ceilings(u, ceilings)


def appendix_d_summary_draft(rights=0.12, margin=0.02, vuln=1.5, ceiling=0.10):
    """Rights check for the first draft with a clinical summary."""
    u = round(vuln * (rights + margin), 4)
    return u, u <= ceiling


if __name__ == "__main__":
    rows = [
        ("ch01_harm_vector", ch01_harm_vector()),
        ("ch01_inaction", ch01_inaction()),
        ("ch02_cascade", ch02_cascade()),
        ("ch02_window", ch02_window()),
        ("ch03_penalty_0.3", ch03_penalty(0.3)),
        ("ch03_penalty_2.0", ch03_penalty(2.0)),
        ("ch03_crossover", ch03_crossover()),
        ("ch03_rescaled_x3", (ch03_penalty(2.0, 3.0), ch03_crossover(3.0))),
        ("ch03_gate", ch03_gate()),
        ("ch04_lexicographic", ch04_lexicographic()),
        ("ch04_default", (ch04_uncertainty_default(0.92),
                          ch04_uncertainty_default(0.64))),
        ("ch05_horizon", ch05_horizon()),
        ("ch05_margin", ch05_margin()),
        ("ch05_empty_set", ch05_empty_set()),
        ("ch06_scalar_vs_vector", ch06_scalar_vs_vector()),
        ("ch06_hazard_matrix", ch06_hazard_matrix()),
        ("ch06_counterfactual", ch06_counterfactual()),
        ("ch07_cq", ch07_cq()),
        ("ch07_minimax", ch07_minimax()),
        ("ch07_error_weighting", ch07_error_weighting()),
        ("ch08_authority", ch08_authority()),
        ("ch08_ledger", ch08_ledger_completeness()),
        ("ch09_cai", ch09_cai()),
        ("ch09_redesign", ch09_cai((0.70, 0.60, 0.80, 0.70, 0.50, 0.55, 0.70))),
        ("ch09_weight_attack", ch09_weight_attack()),
        ("ch10_filter", ch10_filter()),
        ("ch10_path_coverage", ch10_path_coverage()),
        ("ch11_restricted_game", ch11_restricted_game()),
        ("ch11_allocation", ch11_allocation()),
        ("ch11_correlated_pair", ch11_correlated_pair()),
        ("ch12_breaker", ch12_breaker()),
        ("ch12_degraded_capacity", ch12_degraded_capacity()),
        ("ch13_exclusion", ch13_exclusion()),
        ("ch13_applicant_view", ch13_applicant_view()),
        ("ch13_alerts", ch13_alerts()),
        ("ch14_stopping", ch14_stopping()),
        ("ch14_stopping_slow_sensor", ch14_stopping(latency=0.35)),
        ("ch14_amplification", ch14_amplification()),
        ("ch14_zone_floor", ch14_zone_floor()),
        ("ch15_contestation", ch15_contestation()),
        ("ch15_maturity", ch15_maturity()),
        ("ch16_audit", ch16_audit()),
        ("ch16_near_band", ch16_near_band()),
        ("ch17_gap", ch17_gap()),
        ("ch17_required_rate", ch17_required_rate()),
        ("ch18_floor_review", ch18_floor_review()),
        ("ch18_commitments", ch18_commitments()),
        ("appendix_d_upper", appendix_d_upper()),
        ("appendix_d_summary_draft", appendix_d_summary_draft()),
    ]
    for name, value in rows:
        print(f"{name:26s} {value}")
