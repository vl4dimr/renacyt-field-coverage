# -*- coding: utf-8 -*-
"""
Análisis de cobertura del registro por subcampo y campo.

Cobertura(s) = autores certificados con subcampo dominante s / autores totales
               con subcampo dominante s, con IC de Wilson al 95%.

Salidas:
  outputs/cobertura_subcampos.csv
  outputs/cobertura_campos.csv
  outputs/resumen_cobertura.json
"""
import json
import numpy as np
import pandas as pd
from scipy import stats

MIN_AUTORES = 30          # umbral para reportar un subcampo individualmente
CORTE_SENSIBILIDAD = 2023 # produccion hasta 2023 (desfase con corte RENACYT may-2024)

oa = pd.read_csv("data/autores_pe_enlazados.csv", encoding="utf-8-sig")


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / den
    ancho = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (max(0, centro - ancho), min(1, centro + ancho))


def cobertura(df, clave):
    g = df.groupby(clave).agg(
        autores=("author_id", "count"),
        certificados=("certificado", "sum"),
        obras=("n_obras", "sum"),
        obras_mediana=("n_obras", "median"),
    ).reset_index()
    g["cobertura_pct"] = (100 * g.certificados / g.autores).round(1)
    ci = g.apply(lambda r: wilson(r.certificados, r.autores), axis=1)
    g["ci_low"] = [round(100 * a, 1) for a, b in ci]
    g["ci_high"] = [round(100 * b, 1) for a, b in ci]
    return g.sort_values("cobertura_pct", ascending=False)


# ---- principal: todos los autores
sub = cobertura(oa, "subfield_dom")
sub_rep = sub[sub.autores >= MIN_AUTORES].copy()
cam = cobertura(oa, "field_dom")

# ---- sensibilidad: solo autores cuya primera publicación es <= 2023
oa_s = oa[oa.primer_anio <= CORTE_SENSIBILIDAD]
sub_s = cobertura(oa_s, "subfield_dom")
sub_s = sub_s[sub_s.autores >= MIN_AUTORES][["subfield_dom", "cobertura_pct"]]
sub_rep = sub_rep.merge(sub_s.rename(columns={"cobertura_pct": "cobertura_hasta2023_pct"}),
                        on="subfield_dom", how="left")

# ---- sensibilidad B: autores con >=2 obras (excluye apariciones únicas)
oa_2 = oa[oa.n_obras >= 2]
sub_2 = cobertura(oa_2, "subfield_dom")
sub_2 = sub_2[sub_2.autores >= MIN_AUTORES][["subfield_dom", "cobertura_pct"]]
sub_rep = sub_rep.merge(sub_2.rename(columns={"cobertura_pct": "cobertura_2obras_pct"}),
                        on="subfield_dom", how="left")

sub_rep.to_csv("outputs/cobertura_subcampos.csv", index=False, encoding="utf-8-sig")
cam.to_csv("outputs/cobertura_campos.csv", index=False, encoding="utf-8-sig")

# ---- correlaciones exploratorias: ¿qué predice la cobertura?
# tamaño del subcampo, produccion mediana, "juventud" (anio medio de entrada)
juv = oa.groupby("subfield_dom")["primer_anio"].mean()
sub_rep["anio_medio_entrada"] = sub_rep.subfield_dom.map(juv).round(2)
rho_size, p_size = stats.spearmanr(sub_rep.autores, sub_rep.cobertura_pct)
rho_prod, p_prod = stats.spearmanr(sub_rep.obras_mediana, sub_rep.cobertura_pct)
rho_juv, p_juv = stats.spearmanr(sub_rep.anio_medio_entrada, sub_rep.cobertura_pct)

resumen = {
    "autores_totales": int(len(oa)),
    "certificados": int(oa.certificado.sum()),
    "cobertura_global_pct": round(100 * oa.certificado.mean(), 1),
    "subcampos_reportados": int(len(sub_rep)),
    "umbral_min_autores": MIN_AUTORES,
    "top10_cobertura": sub_rep.head(10)[["subfield_dom", "autores",
                                          "cobertura_pct"]].to_dict("records"),
    "bottom10_cobertura": sub_rep.tail(10)[["subfield_dom", "autores",
                                             "cobertura_pct"]].to_dict("records"),
    "cobertura_por_campo": cam[["field_dom", "autores",
                                 "cobertura_pct"]].to_dict("records"),
    "correlaciones_spearman": {
        "tamano_subcampo": {"rho": round(float(rho_size), 3), "p": float(f"{p_size:.2e}")},
        "produccion_mediana": {"rho": round(float(rho_prod), 3), "p": float(f"{p_prod:.2e}")},
        "anio_medio_entrada": {"rho": round(float(rho_juv), 3), "p": float(f"{p_juv:.2e}")},
    },
    "referencia_ia": {
        "subcampo_1702": sub[sub.subfield_id_dom == "1702"][
            ["autores", "certificados", "cobertura_pct"]].to_dict("records")
        if "subfield_id_dom" in sub.columns else "ver cobertura_subcampos.csv",
    },
}
with open("outputs/resumen_cobertura.json", "w", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2)
print(json.dumps(resumen, ensure_ascii=False, indent=2)[:3000])
