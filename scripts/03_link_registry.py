# -*- coding: utf-8 -*-
"""
Cruce nominal autores OpenAlex (todos los campos) x RENACYT.
Protocolo de tres niveles (exacta/alta/media) heredado del paquete
doi:10.5281/zenodo.22070643, aplicado a escala (~10^5 autores).

Salidas:
  data/autores_pe_enlazados.csv  (todos los autores, con columnas de match)
  outputs/link_reporte.json
"""
import json
import unicodedata
from collections import defaultdict

import pandas as pd

PARTICULAS = {"DE", "LA", "DEL", "LOS", "LAS", "Y", "DA", "DI", "VAN", "VON"}

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", str(s))
                if unicodedata.category(c) != "Mn")
    s = s.upper().replace("-", " ").replace(".", " ").replace("'", " ")
    return " ".join(t for t in s.split() if t)

def tokens(s):
    ts = norm(s).replace(",", " ").split()
    return [t for t in ts if t not in PARTICULAS]

ren = pd.read_csv("data/renacyt_limpio.csv", encoding="utf-8-sig")
oa = pd.read_csv("data/autores_pe.csv", encoding="utf-8-sig")

ren_tokens, ren_surnames, ren_given = {}, {}, {}
tok2rows = defaultdict(set)
for i, r in ren.iterrows():
    nombre = str(r["INVESTIGADOR"])
    ap, no = (nombre.split(",", 1) + [""])[:2]
    su, gi = tokens(ap), tokens(no)
    ren_surnames[i], ren_given[i] = set(su), set(gi)
    ren_tokens[i] = set(su) | set(gi)
    for t in ren_tokens[i]:
        tok2rows[t].add(i)

confianza, codigo = [], []
n_amb = 0
for name in oa["author_name"].astype(str).values:
    ts_all = tokens(name)
    ts = [t for t in ts_all if len(t) > 1]
    if len(ts) < 2:
        confianza.append("no_match"); codigo.append("")
        continue
    cand = None
    for t in ts:
        rows = tok2rows.get(t, set())
        cand = rows if cand is None else (cand & rows)
        if not cand:
            break
    cand = cand or set()
    tset = set(ts)
    tier, chosen = None, None
    exact = [c for c in cand if ren_tokens[c] == tset]
    if len(exact) == 1:
        tier, chosen = "exacta", exact[0]
    elif len(cand) == 1:
        c = next(iter(cand))
        if tset & ren_surnames[c] and tset & ren_given[c]:
            tier = "alta" if len(ts) >= 3 else "media"
            chosen = c
    if chosen is None:
        if len(cand) > 1:
            n_amb += 1
        confianza.append("no_match"); codigo.append("")
    else:
        confianza.append(tier)
        codigo.append(ren.loc[chosen, "CODIGO_RENACYT"])

oa["confianza_match"] = confianza
oa["CODIGO_RENACYT"] = codigo
oa["certificado"] = (oa["confianza_match"] != "no_match").astype(int)

# atributos del registro para los emparejados
ren_cols = ren.set_index("CODIGO_RENACYT")[["nivel", "sexo", "region",
                                            "macrozona", "anio_calificacion"]]
oa = oa.merge(ren_cols, left_on="CODIGO_RENACYT", right_index=True, how="left")
oa.to_csv("data/autores_pe_enlazados.csv", index=False, encoding="utf-8-sig")

rep = {
    "autores_openalex": int(len(oa)),
    "emparejados": int(oa.certificado.sum()),
    "tasa_global_pct": round(100 * oa.certificado.mean(), 1),
    "por_confianza": oa.loc[oa.certificado == 1, "confianza_match"].value_counts().to_dict(),
    "ambiguos_descartados": int(n_amb),
    "codigos_renacyt_unicos_cubiertos": int(oa.loc[oa.certificado == 1,
                                                  "CODIGO_RENACYT"].nunique()),
    "registro_total": int(len(ren)),
}
with open("outputs/link_reporte.json", "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print(json.dumps(rep, ensure_ascii=False, indent=2))
