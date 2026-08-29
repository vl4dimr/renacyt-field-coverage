# -*- coding: utf-8 -*-
"""Figuras del manuscrito JoI (ingles, estilo revista, 600 dpi)."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AZUL = "#1c5cab"
CLARO = "#86b6ef"
GRIS = "#9a9a94"
GRIS_CLARO = "#d4d2cb"
INK, INK2, GRID = "#1a1a19", "#6b6a64", "#eceae5"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 9, "axes.labelsize": 9, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "axes.edgecolor": "#c9c7c0", "axes.linewidth": 0.7,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 110, "savefig.dpi": 600, "savefig.bbox": "tight",
    "legend.frameon": False, "legend.fontsize": 8.5,
})

sub = pd.read_csv("outputs/cobertura_subcampos.csv", encoding="utf-8-sig")
cam = pd.read_csv("outputs/cobertura_campos.csv", encoding="utf-8-sig")
res = json.load(open("outputs/resumen_cobertura.json", encoding="utf-8"))
GLOBAL = res["cobertura_global_pct"]
FIG = "outputs/figures/"

# ---------------- fig 1: cobertura por campo (26) ----------------------------
cam = cam.sort_values("cobertura_pct")
fig, ax = plt.subplots(figsize=(6.8, 6.4))
colores = [AZUL if c >= GLOBAL else GRIS for c in cam.cobertura_pct]
bars = ax.barh(cam.field_dom, cam.cobertura_pct, color=colores, height=0.62)
for r, (v, lo, hi) in zip(bars, cam[["cobertura_pct", "ci_low", "ci_high"]].values):
    y = r.get_y() + r.get_height() / 2
    ax.plot([lo, hi], [y, y], color=INK, lw=0.9)
    ax.annotate(f" {v:.1f}", (hi, y), va="center", fontsize=7.5, color=INK2)
ax.axvline(GLOBAL, color=INK, lw=0.9, ls=(0, (4, 3)))
ax.annotate(f"overall {GLOBAL}%", (GLOBAL, len(cam) - 0.2), fontsize=8, color=INK,
            ha="left", xytext=(4, 0), textcoords="offset points")
ax.set_xlabel("Registry coverage (%), Wilson 95% CI")
ax.grid(axis="y", visible=False)
fig.savefig(FIG + "fig1_fields.png"); plt.close(fig)
print("fig1 ok")

# ---------------- fig 2: extremos de subcampo (top/bottom 15) ----------------
s = sub.sort_values("cobertura_pct", ascending=False)
top, bot = s.head(15), s.tail(15)
ex = pd.concat([top, bot]).iloc[::-1]
fig, ax = plt.subplots(figsize=(6.8, 7.2))
y = np.arange(len(ex))
col = [AZUL] * 15 + [GRIS] * 15
col = col[::-1]
ax.scatter(ex.cobertura_pct, y, s=42, color=col, zorder=3)
for yi, (lo, hi) in zip(y, ex[["ci_low", "ci_high"]].values):
    ax.plot([lo, hi], [yi, yi], color="#b9b6ae", lw=1.1, zorder=2)
ax.set_yticks(y, [f"{n}  (n={a:,})" for n, a in ex[["subfield_dom", "autores"]].values],
              fontsize=7.5)
ax.axvline(GLOBAL, color=INK, lw=0.9, ls=(0, (4, 3)))
ax.annotate(f"overall {GLOBAL}%", (GLOBAL, len(ex) - 0.5), fontsize=8, color=INK,
            ha="left", xytext=(4, 0), textcoords="offset points")
ax.set_xlabel("Registry coverage (%), Wilson 95% CI")
ax.grid(axis="y", visible=False)
fig.savefig(FIG + "fig2_subfield_extremes.png"); plt.close(fig)
print("fig2 ok")

# ---------------- fig 3: distribucion de cobertura + IA ----------------------
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.hist(sub.cobertura_pct, bins=24, color=CLARO, edgecolor="white", linewidth=0.6)
ax.axvline(GLOBAL, color=INK, lw=1.0, ls=(0, (4, 3)))
ax.annotate(f"overall {GLOBAL}%", (GLOBAL, ax.get_ylim()[1] * 0.95), fontsize=8,
            color=INK, ha="left", xytext=(4, 0), textcoords="offset points")
ia = sub[sub.subfield_dom == "Artificial Intelligence"]
if len(ia):
    v = float(ia.cobertura_pct.iloc[0])
    ax.axvline(v, color=AZUL, lw=1.2)
    ax.annotate(f"Artificial Intelligence {v:.1f}%", (v, ax.get_ylim()[1] * 0.75),
                fontsize=8, color=AZUL, ha="left", xytext=(4, 0),
                textcoords="offset points")
ax.set_xlabel("Registry coverage (%) across 204 subfields")
ax.set_ylabel("Subfields")
ax.grid(axis="x", visible=False)
fig.savefig(FIG + "fig3_distribution.png"); plt.close(fig)
print("fig3 ok")

# ---------------- fig 4: sensibilidad >=2 obras ------------------------------
fig, ax = plt.subplots(figsize=(5.6, 5.2))
ax.scatter(sub.cobertura_pct, sub.cobertura_2obras_pct, s=16, color=AZUL,
           alpha=0.55, edgecolors="none")
lim = max(sub.cobertura_2obras_pct.max(), sub.cobertura_pct.max()) + 4
ax.plot([0, lim], [0, lim], color=INK2, lw=0.9, ls=(0, (4, 3)))
ax.annotate("equal coverage", (lim * 0.72, lim * 0.66), fontsize=8, color=INK2,
            rotation=38)
ax.set_xlabel("Coverage, all authors (%)")
ax.set_ylabel("Coverage, authors with ≥2 works (%)")
ax.set_xlim(0, lim); ax.set_ylim(0, lim)
fig.savefig(FIG + "fig4_sensitivity.png"); plt.close(fig)
print("fig4 ok")
