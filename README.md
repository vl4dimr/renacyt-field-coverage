# Field-level registry coverage against open bibliographic data

[![DOI](https://zenodo.org/badge/1350503558.svg)](https://doi.org/10.5281/zenodo.22160752)

Replication package for *Measuring what registries miss: field-level coverage
of researcher certification against open bibliographic data* (submitted to the
Journal of Informetrics).

## Contents
- `data/renacyt_limpio.csv` — Peru's public researcher registry (RENACYT,
  cut-off 2024-05-30; CONCYTEC open data, ODC-By), cleaned.
- `data/autores_pe.csv` — 191,089 Peru-affiliated OpenAlex author profiles
  (2015–2026) with dominant subfield and production counts (output of
  scripts 01–02).
- `data/autores_pe_enlazados.csv` — the author table linked to the registry
  with the three-tier protocol (output of script 03).
- `scripts/01_harvest_openalex_all.py` — harvests all OpenAlex works with
  Peruvian affiliation, 2015 onward (streaming, cursor pagination, resumable).
  Re-run this to regenerate the raw authorship file (~60 MB, not shipped).
- `scripts/02_aggregate_authors.py` — aggregates authorships into author
  profiles with dominant subfield.
- `scripts/03_link_registry.py` — three-tier name linkage against the registry
  (protocol validated in https://doi.org/10.5281/zenodo.22099851).
- `scripts/04_coverage_analysis.py` — coverage per subfield/field with Wilson
  95% CIs, sensitivity analyses, Spearman correlations.
- `scripts/05_figures.py` — manuscript figures (600 dpi).
- `outputs/` — coverage tables (204 subfields, 26 fields), summary JSON, and
  figures.

## Reproduce
```
pip install pandas numpy scipy matplotlib requests
python scripts/01_harvest_openalex_all.py   # ~1-2 h, OpenAlex API (or skip: data/ ships the aggregated tables)
python scripts/02_aggregate_authors.py
python scripts/03_link_registry.py
python scripts/04_coverage_analysis.py
python scripts/05_figures.py
```

## Licences
Code: MIT. Derived data and outputs: CC BY 4.0. RENACYT source: ODC-By
(CONCYTEC). OpenAlex data: CC0.

## Related
- Linkage-protocol package: https://doi.org/10.5281/zenodo.22099851
- Prior single-field application: https://doi.org/10.5281/zenodo.22070643
