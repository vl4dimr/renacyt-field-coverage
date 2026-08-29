# -*- coding: utf-8 -*-
"""
Agrega la cosecha por autor: subcampo/campo dominante, producción y ventana.
Entrada: data/openalex_authorships_pe_2015_2026.csv
Salida:  data/autores_pe.csv
"""
import pandas as pd

df = pd.read_csv("data/openalex_authorships_pe_2015_2026.csv", encoding="utf-8")
print("Autorías:", len(df), "| obras:", df.work_id.nunique(),
      "| autores:", df.author_id.nunique())

# deduplicar por autor-obra (por si una obra lista dos afiliaciones del mismo autor)
df = df.drop_duplicates(["work_id", "author_id"])

def moda(s):
    m = s.mode()
    return m.iloc[0] if len(m) else ""

ag = df.groupby("author_id").agg(
    author_name=("author_name", "first"),
    orcid=("orcid", lambda s: next((x for x in s if isinstance(x, str) and x), "")),
    n_obras=("work_id", "nunique"),
    citas=("citas", "sum"),
    primer_anio=("anio", "min"),
    ultimo_anio=("anio", "max"),
    subfield_dom=("subfield", moda),
    subfield_id_dom=("subfield_id", moda),
    field_dom=("field", moda),
    n_subfields=("subfield", "nunique"),
).reset_index()

ag.to_csv("data/autores_pe.csv", index=False, encoding="utf-8-sig")
print("Autores agregados:", len(ag))
print(ag.n_obras.describe())
print("\nTop 15 subcampos por nº de autores dominantes:")
print(ag.subfield_dom.value_counts().head(15))
