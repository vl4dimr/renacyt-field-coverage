# -*- coding: utf-8 -*-
"""
Cosecha COMPLETA de OpenAlex: todas las obras 2015+ con al menos una autoría
afiliada a Perú, con su subcampo primario. Escritura en streaming (CSV) y
reanudación por cursor guardado.

Salida: data/openalex_authorships_pe_2015_2026.csv
        (una fila por autoría peruana por obra)
"""
import csv
import json
import os
import time
import urllib.request
import urllib.parse

BASE = "https://api.openalex.org/works"
OUT = "data/openalex_authorships_pe_2015_2026.csv"
CURSOR_FILE = "data/harvest_cursor.json"
HEADERS = {"User-Agent": "peru-registry-coverage-research"}
FILTER = "authorships.countries:countries/pe,from_publication_date:2015-01-01"
SELECT = "id,publication_year,type,cited_by_count,primary_topic,authorships"


def fetch(url, retries=6):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            wait = min(60, 3 * (i + 1))
            print(f"  reintento {i+1} en {wait}s: {e}", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Fallo persistente: {url}")


# --- reanudación ---
cursor, pagina, obras = "*", 0, 0
mode = "w"
if os.path.exists(CURSOR_FILE):
    st = json.load(open(CURSOR_FILE, encoding="utf-8"))
    cursor, pagina, obras = st["cursor"], st["pagina"], st["obras"]
    mode = "a"
    print(f"Reanudando en página {pagina} (obras {obras})", flush=True)

f = open(OUT, mode, newline="", encoding="utf-8")
w = csv.writer(f)
if mode == "w":
    w.writerow(["work_id", "anio", "tipo", "citas", "field", "subfield_id",
                "subfield", "author_id", "author_name", "orcid"])

t0 = time.time()
while cursor:
    params = {"filter": FILTER, "per-page": "200", "cursor": cursor, "select": SELECT}
    data = fetch(BASE + "?" + urllib.parse.urlencode(params))
    for wk in data.get("results", []):
        obras += 1
        wid = wk["id"].rsplit("/", 1)[-1]
        pt = wk.get("primary_topic") or {}
        sf = pt.get("subfield") or {}
        fld = (pt.get("field") or {}).get("display_name", "")
        sf_id = str(sf.get("id", "")).rsplit("/", 1)[-1]
        sf_name = sf.get("display_name", "")
        for a in wk.get("authorships", []):
            if "PE" not in (a.get("countries") or []):
                continue
            au = a.get("author") or {}
            w.writerow([wid, wk.get("publication_year"), wk.get("type"),
                        wk.get("cited_by_count"), fld, sf_id, sf_name,
                        str(au.get("id", "")).rsplit("/", 1)[-1],
                        au.get("display_name", ""), au.get("orcid") or ""])
    cursor = (data.get("meta") or {}).get("next_cursor")
    pagina += 1
    if pagina % 10 == 0:
        f.flush()
        json.dump({"cursor": cursor, "pagina": pagina, "obras": obras},
                  open(CURSOR_FILE, "w", encoding="utf-8"))
        el = time.time() - t0
        print(f"página {pagina} | obras {obras} | {el/60:.1f} min", flush=True)
    time.sleep(0.12)

f.close()
if os.path.exists(CURSOR_FILE):
    os.remove(CURSOR_FILE)
print(f"COSECHA COMPLETA: {obras} obras en {(time.time()-t0)/60:.1f} min", flush=True)
