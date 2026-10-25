#!/usr/bin/env python3
"""Figures for Ahimsa in Agentic AI (v2.1).  Charts are computed from the
companion program, so a figure can never drift from the numbers in the
text.  Writes assets/fig/*.png (colour) and assets/fig_bw/*.png (grayscale,
distinct line styles and hatching for black-ink print).

    python tools/make_figures.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import models_ahimsa_in_agentic_ai as m  # noqa: E402

W = 4.4                       # inches = printed width
DPI = 300
COL = dict(navy="#1A237E", purple="#6A1B9A", amber="#E09F3E", green="#3B8B5A",
           red="#C0392B", sky="#DCE6F5", pale="#EDEFF9", grey="#5A6B7B", ink="#1A1A1A")
BW = dict(navy="#000000", purple="#333333", amber="#777777", green="#555555",
          red="#000000", sky="#E6E6E6", pale="#F2F2F2", grey="#555555", ink="#000000")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5,
                     "axes.titlesize": 9, "axes.labelsize": 8.5,
                     "xtick.labelsize": 8, "ytick.labelsize": 8,
                     "legend.fontsize": 8, "axes.spines.top": False,
                     "axes.spines.right": False})


def save(fig, name, mode):
    out = ROOT / "assets" / ("fig" if mode == "color" else "fig_bw")
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.png", dpi=DPI, bbox_inches="tight", pad_inches=0.04,
                facecolor="white")
    plt.close(fig)
    if mode == "bw":                     # true grayscale for black-ink print
        from PIL import Image
        Image.open(out / f"{name}.png").convert("L").save(out / f"{name}.png")


def box(ax, x, y, w, h, text, fc, ec, tc="black", fs=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                fc=fc, ec=ec, lw=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, a, b, c, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=10, lw=1.0,
                                 color=c, linestyle=ls, shrinkA=0, shrinkB=0))


# ------------------------------------------------------------------ figures
def f01_translation(mode):
    C = COL if mode == "color" else BW
    fig, ax = plt.subplots(figsize=(W, 1.85))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.2); ax.axis("off")
    steps = [("Formalize", "harm vector\nH(a, s)\nCh. 5–7"), ("Bound", "ceilings\nH ≤ ε\nCh. 5"),
             ("Filter", "gate before\nexecution\nCh. 10"), ("Audit", "violations,\nnear misses\nCh. 16")]
    xs = [0.1, 2.6, 5.1, 7.6]
    for (t, s), x in zip(steps, xs):
        box(ax, x, 1.0, 2.2, 1.9, "", C["pale"], C["navy"])
        ax.text(x + 1.1, 2.5, t, ha="center", va="center", fontsize=8.8, fontweight="bold", color=C["navy"])
        ax.text(x + 1.1, 1.55, s, ha="center", va="center", fontsize=7.8, color=C["ink"])
    for x in xs[:-1]:
        arrow(ax, (x + 2.22, 1.95), (x + 2.58, 1.95), C["navy"])
    ax.plot([8.7, 8.7], [0.98, 0.62], color=C["purple"], lw=1.0, ls="--")
    ax.plot([8.7, 1.2], [0.62, 0.62], color=C["purple"], lw=1.0, ls="--")
    arrow(ax, (1.2, 0.62), (1.2, 0.98), C["purple"])
    ax.text(5.0, 0.22, "findings return into the specification", ha="center", fontsize=8,
            color=C["purple"], style="italic")
    save(fig, "f01_translation", mode)


def f02_cascade(mode):
    C = COL if mode == "color" else BW
    plain, guard = m.ch02_cascade()
    t = list(range(0, 7))
    fig, ax = plt.subplots(figsize=(W, 2.35))
    ax.plot(t, [0.02] + plain, marker="o", ms=3.5, color=C["red"], lw=1.6, label="no intermediate checks")
    ax.plot(t, [0.02] + guard, marker="s", ms=3.5, color=C["navy"], lw=1.6,
            ls="-" if mode == "color" else "--", label="check at every iteration")
    ax.annotate(f"{plain[-1]:.4f}", (6, plain[-1]), xytext=(4.6, 0.31), fontsize=8,
                arrowprops=dict(arrowstyle="-", color=C["grey"], lw=0.6))
    ax.annotate(f"{guard[-1]:.4f}", (6, guard[-1]), xytext=(5.0, 0.06), fontsize=8,
                arrowprops=dict(arrowstyle="-", color=C["grey"], lw=0.6))
    ax.set_xlabel("unattended planning iteration t"); ax.set_ylabel("decision error $e_t$")
    ax.set_xticks(t); ax.set_ylim(0, 0.36); ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", color="#DDDDDD", lw=0.5)
    save(fig, "f02_cascade", mode)


def f03_window(mode):
    C = COL if mode == "color" else BW
    p, _, _ = m.ch02_window()
    n = list(range(1, 13))
    y = [1 - (1 - p) ** k for k in n]
    fig, ax = plt.subplots(figsize=(W, 2.2))
    ax.bar(n, y, color=C["sky"], edgecolor=C["navy"], lw=0.6,
           hatch=None if mode == "color" else "//")
    for k, lab in ((2, "0.0133"), (6, "0.0393")):
        ax.bar([k], [y[k - 1]], color=C["amber"] if mode == "color" else "#999999",
               edgecolor=C["navy"], lw=0.8)
        ax.text(k, y[k - 1] + 0.003, lab, ha="center", fontsize=8)
    ax.set_xlabel("autonomy window (steps between human reviews)")
    ax.set_ylabel("P(at least one erroneous\nirreversible write)")
    ax.set_xticks(n); ax.grid(axis="y", color="#DDDDDD", lw=0.5)
    save(fig, "f03_window", mode)


def f04_caia(mode):
    C = COL if mode == "color" else BW
    layers = [("Future Generation", "FG", True), ("Planetary Compassion", "PC", True),
              ("Equity and Protection", "VP", True),
              ("Human Flourishing", "HF", False), ("Empathy Intelligence", "EM", False),
              ("Suffering Reduction", "SR", False), ("Compassion Foundation", "CQ", False)]
    fig, ax = plt.subplots(figsize=(W, 3.3))
    ax.set_xlim(0, 10); ax.set_ylim(-1.55, 7.6); ax.axis("off")
    for i, (name, code, floor) in enumerate(layers):
        y = 6.2 - i * 0.9
        fc = C["pale"] if not floor else (C["sky"] if mode == "color" else "#D9D9D9")
        box(ax, 0.9, y, 6.9, 0.75, "", fc, C["navy"])
        ax.text(1.15, y + 0.375, f"{7 - i}", va="center", fontsize=8.5, fontweight="bold", color=C["navy"])
        ax.text(1.6, y + 0.375, name, va="center", fontsize=8.5, color=C["ink"])
        ax.text(7.55, y + 0.375, code, va="center", ha="right", fontsize=8.5, fontweight="bold", color=C["navy"])
        if floor:
            ax.text(7.95, y + 0.375, "floor", va="center", fontsize=7.8, color=C["purple"], fontweight="bold")
    ax.add_patch(FancyBboxPatch((0.15, -0.05), 0.5, 6.95, boxstyle="round,pad=0.02",
                                fc=C["purple"] if mode == "color" else "#444444", ec="none"))
    ax.text(0.40, 3.45, "Responsibility and Oversight spine", rotation=90, ha="center", va="center",
            fontsize=7.8, color="white")
    box(ax, 0.9, -1.45, 6.9, 0.8, "Ahimsa gate: ceilings, authority,\nconsent, current evidence",
        C["navy"], C["navy"], tc="white", fs=7.8, bold=True)
    arrow(ax, (4.35, -0.62), (4.35, -0.08), C["navy"])
    ax.text(7.95, -1.05, "fail:\nnever\nscored", va="center", fontsize=7.4, color=C["red"])
    ax.text(4.35, 7.32, "layers 5–7 carry floors: a score below its threshold τ vetoes the decision",
            ha="center", va="center", fontsize=7.4, color=C["purple"], style="italic")
    save(fig, "f04_caia", mode)


def f05_horizon(mode):
    C = COL if mode == "color" else BW
    d = (0.02, 0.04, 0.10, 0.15, 0.22, 0.30); b = (0.05,) * 6; g = 0.9
    cd, cb, sd, sb = [], [], 0.0, 0.0
    for t in range(6):
        sd += g ** (t + 1) * d[t]; sb += g ** (t + 1) * b[t]; cd.append(sd); cb.append(sb)
    hd, hb = m.ch05_horizon()[:2]
    assert round(cd[-1], 4) == hd and round(cb[-1], 4) == hb
    x = list(range(1, 7))
    fig, ax = plt.subplots(figsize=(W, 2.3))
    ax.plot(x, cd, marker="o", ms=3.5, color=C["red"], lw=1.6, label="Plan D (late harm)")
    ax.plot(x, cb, marker="s", ms=3.5, color=C["navy"], lw=1.6, ls="-" if mode == "color" else "--",
            label="Plan B (steady protection)")
    ax.axhline(0.30, color=C["grey"], ls=":", lw=1.2)
    ax.text(1.05, 0.315, "cumulative ceiling $\\epsilon_N = 0.30$", fontsize=8, color=C["grey"])
    ax.text(6.08, cd[-1], f"{hd:.4f}", va="center", fontsize=8)
    ax.text(6.08, cb[-1], f"{hb:.4f}", va="center", fontsize=8)
    ax.set_xlim(0.8, 6.8); ax.set_ylim(0, 0.58)
    ax.set_xlabel("step t"); ax.set_ylabel("time-decayed total $\\mathcal{H}_t$ ($\\gamma = 0.9$)")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.92)); ax.grid(axis="y", color="#DDDDDD", lw=0.5)
    save(fig, "f05_horizon", mode)


def f06_dispositions(mode):
    C = COL if mode == "color" else BW
    fig, ax = plt.subplots(figsize=(W, 3.7))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    X, BW_ = 0.6, 5.6           # question boxes
    q = [(9.0, "Typed action proposed"), (7.4, "Authority and consent valid?"),
         (5.8, "Evidence current?"), (4.2, "Within every ceiling?"),
         (2.6, "Physical ceiling breached\n(direct severe harm)?")]
    box(ax, X, q[0][0] - 0.45, BW_, 0.9, q[0][1], C["navy"], C["navy"], tc="white", bold=True, fs=8)
    for y, t in q[1:]:
        box(ax, X, y - 0.5, BW_, 1.0, t, C["pale"], C["navy"], fs=8)
    cx = X + BW_ / 2
    for (y1, _), (y2, _) in zip(q, q[1:]):
        arrow(ax, (cx, y1 - 0.52), (cx, y2 + 0.52), C["navy"])
        if y1 != 9.0:
            ax.text(cx + 0.15, (y1 + y2) / 2 - 0.1, "yes", fontsize=7.4, color=C["grey"])
    outs = [(7.4, "DENY", "no"), (5.8, "REFRESH", "no"), (4.2, "PERMIT", "yes"), (2.6, "ESCALATE", "yes")]
    colours = [C["red"], C["amber"], C["green"], C["purple"]]
    for (y, t, lab), c in zip(outs, colours):
        arrow(ax, (X + BW_ + 0.02, y), (7.45, y), C["navy"])
        ax.text(6.45, y + 0.15, lab, fontsize=7.4, color=C["grey"])
        box(ax, 7.5, y - 0.42, 2.4, 0.84, t, c, c, tc="white", bold=True, fs=8)
    arrow(ax, (cx, 2.08), (cx, 1.22), C["navy"])
    ax.text(cx + 0.15, 1.55, "no", fontsize=7.4, color=C["grey"])
    box(ax, X, 0.3, BW_, 0.9, "REFORMULATE", C["navy"] if mode == "color" else "#444444",
        C["navy"], tc="white", bold=True, fs=8)
    ax.text(6.45, 0.75, "narrow, slow or shift;\nevery new action starts\nagain at the top", fontsize=7.2,
            color=C["grey"], va="center", style="italic")
    save(fig, "f06_dispositions", mode)


def f07_drift(mode):
    C = COL if mode == "color" else BW
    fire, warn = m.ch12_breaker()
    z = m.DRIFT; w = list(range(1, 11))
    fig, ax = plt.subplots(figsize=(W, 2.3))
    ax.axhspan(2.0, 3.0, color=C["amber"] if mode == "color" else "#DDDDDD", alpha=0.25 if mode == "color" else 0.6, lw=0)
    ax.axhline(3.0, color=C["red"], lw=1.2)
    ax.plot(w, z, marker="o", ms=3.5, color=C["navy"], lw=1.6)
    ax.text(1.0, 2.45, "warning band (2.0–3.0)", fontsize=8, color=C["ink"])
    ax.text(1.0, 3.12, "breaker threshold 3.0", fontsize=8, color=C["red"])
    ax.annotate(f"first warning: week {warn}", (warn, z[warn - 1]), xytext=(7.35, 1.35), fontsize=8,
                arrowprops=dict(arrowstyle="->", color=C["grey"], lw=0.7))
    ax.annotate(f"breaker fires: week {fire}", (fire, z[fire - 1]), xytext=(7.35, 0.55), fontsize=8,
                arrowprops=dict(arrowstyle="->", color=C["grey"], lw=0.7))
    ax.set_xticks(w); ax.set_ylim(0, 3.9); ax.set_xlabel("week"); ax.set_ylabel("drift reading z")
    save(fig, "f07_drift", mode)


def f08_gap(mode):
    C = COL if mode == "color" else BW
    yrs = list(range(0, 6))
    r_req = m.ch17_required_rate()
    cap = [1.35 ** t for t in yrs]; con = [1.12 ** t for t in yrs]; req = [r_req ** t for t in yrs]
    assert round(cap[-1], 2) == m.ch17_gap()[0]
    fig, ax = plt.subplots(figsize=(W, 2.35))
    ax.plot(yrs, cap, marker="o", ms=3.5, color=C["red"], lw=1.6, label="capability (×1.35 per year)")
    ax.plot(yrs, req, marker="^", ms=3.5, color=C["green"], lw=1.6, ls="-." ,
            label=f"constraint needed for 80% share (×{r_req})")
    ax.plot(yrs, con, marker="s", ms=3.5, color=C["navy"], lw=1.6, ls="--", label="constraint (×1.12 per year)")
    ax.text(5.08, cap[-1], f"{cap[-1]:.2f}", va="center", fontsize=8)
    ax.text(5.08, req[-1], f"{req[-1]:.2f}", va="center", fontsize=8)
    ax.text(5.08, con[-1], f"{con[-1]:.2f}", va="center", fontsize=8)
    ax.set_xlim(-0.2, 5.7); ax.set_xlabel("year"); ax.set_ylabel("index (year 0 = 1)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#DDDDDD", lw=0.5)
    save(fig, "f08_gap", mode)


ALL = [f01_translation, f02_cascade, f03_window, f04_caia, f05_horizon, f06_dispositions, f07_drift, f08_gap]

def action_boundary():
    """Figure 10.1 (drawn for revision 1.2): colour copy and grayscale copy."""
    from PIL import Image
    if not (ROOT / "assets" / "action_boundary.png").exists():
        return                              # not part of the companion repository
    src = Image.open(ROOT / "assets" / "action_boundary.png")
    (ROOT / "assets" / "fig").mkdir(exist_ok=True); (ROOT / "assets" / "fig_bw").mkdir(exist_ok=True)
    src.convert("RGB").save(ROOT / "assets" / "fig" / "action_boundary.png")
    src.convert("L").save(ROOT / "assets" / "fig_bw" / "action_boundary.png")


if __name__ == "__main__":
    action_boundary()
    for f in ALL:
        for mode in ("color", "bw"):
            f(mode)
    print("figures:", len(ALL), "x 2")
