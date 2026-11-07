# Data sources

All raw inputs are listed below with what they are, where they come from, when
they were retrieved, and under what licence/terms. Processed/derived files are
noted as such. See `CLAUDE.md` ("Data inputs") for how each file is used by
the model; see `scripts/fetch_data.py` for how to re-obtain the raw files that
are not committed to this repo.

File timestamps below are filesystem mtimes on the files as handed off to this
repo (2026-07-07) — a reasonable proxy for retrieval date, but not a confirmed
download-log date. Flagged `TODO: confirm` where the actual retrieval date
should be verified against the author's own records.

## Raw inputs (gitignored — see `scripts/fetch_data.py`)

### `item1.xlsx` — EU CBAM default emission values

- **What it is**: Annex I to the Commission Implementing Regulation
  establishing default values for embedded emissions under the EU Carbon
  Border Adjustment Mechanism (direct/indirect/total emission intensity per CN
  code, per country, with 2026/2027/2028 risk-based mark-ups). This repo uses
  the `Türkiye` sheet, with the `_Other Countries and Territorie` sheet as a
  fallback for codes where Türkiye has no specific value (see
  `cleanUp/item1CleanUp.py`, `is_fallback` flag).
- **Regulatory basis** (per the file's own "Overview" sheet disclaimer and
  "Version History" sheet): Commission Implementing Regulation (EU)
  2025/2621 of 16 December 2025, laying down rules for the application of
  Regulation (EU) 2023/956 as regards the establishment of default values.
  This workbook is version 1, dated 2026-02-04, "based on Implementing
  Regulation (EU) 2025/2621 published on 17 December 2025."
- **URL**: European Commission, Taxation and Customs Union, CBAM definitive
  regime page — https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism/cbam-definitive-regime_en
  (the Excel workbook is linked from this page as "Default values definitive
  period"). The regulation text itself is on EUR-Lex:
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ%3AL_202502621
- **Retrieval date**: TODO: confirm (file mtime 2026-07-07)
- **Licence/terms**: EU institutional document / official regulation text —
  freely reusable per the European Commission's standard reuse policy
  (Commission Decision 2011/833/EU); not subject to third-party IP
  restrictions.
- **⚠ Open item — possible newer corrected values**: on 2026-07-30/31, the
  European Commission published Commission Implementing Regulation (EU)
  2026/1740, which replaces Annex I and Annex IV of 2025/2621 with corrected
  default values. This workbook (v1, 2026-02-04) predates that correction.
  **Not resolved here per the hard rule not to touch model inputs without
  asking** — flagged in `docs/open_issues.md` for the model owner to decide
  whether to re-pull against the corrected annex.

### `item2.csv` — Eurostat Comext Türkiye→EU trade

- **What it is**: Eurostat Comext dataset DS-045409 ("EU trade since 1988 by
  HS2, 4, 6 and CN8"), filtered in `cleanUp/item2CleanUp.py` to Türkiye as
  partner, EU-27 aggregate as reporter, year 2024, HS4-level product codes.
  Comext reports quantity in units of 100 kg; `load_trade()` converts to
  tonnes.
- **URL**: Eurostat Comext dissemination portal —
  https://ec.europa.eu/eurostat/web/international-trade-in-goods/data/database
  (dataset catalog entry: https://data.europa.eu/data/datasets/mhb0ozm8ou0p2svtmzg).
  TODO: confirm the exact query/extraction parameters used for this pull (the
  committed `item2.csv` is a raw extract, not a documented API query).
- **Retrieval date**: TODO: confirm (file mtime 2026-07-07)
- **Licence/terms**: Eurostat data reuse policy — free reuse with source
  acknowledgement (© European Union, 1995-present, reuse authorised provided
  the source is acknowledged), per Eurostat's standard terms.

### `item3.csv` — EPİAŞ hourly Turkish grid generation

- **What it is**: Consolidated 2024 hourly Turkish electricity generation by
  fuel type (8,784 rows = 366 days × 24 hours, deduplicated), with derived
  columns (`gen_total_MWh`, `gen_thermal_MWh`, `gen_renewable_MWh`,
  `thermal_share`) added on top of the raw per-fuel MWh columns. This is
  **already a processed/consolidated file**, not a raw platform export —
  see `scripts/fetch_data.py` for what re-deriving it from scratch would
  require.
- **URL**: EPİAŞ (Enerji Piyasaları İşletme A.Ş.) Transparency Platform
  ("Şeffaflık Platformu"), Real-Time Generation service —
  https://seffaflik.epias.com.tr/transparency/ (API docs:
  https://seffaflik.epias.com.tr/electricity-service/technical/en/index.html).
- **Retrieval date**: TODO: confirm (file mtime 2026-07-07)
- **Licence/terms**: TODO: confirm — EPİAŞ publishes this data openly on the
  Transparency Platform for public market-transparency purposes, but the
  platform's specific reuse/redistribution terms should be checked before
  wider publication of the raw series (the consolidated derived columns used
  by this model are not at issue; the question is redistributing the
  underlying per-hour fuel-mix figures).

## External benchmarks (no local file — cited as named constants in code)

### ENTSO-E Statistical Factsheet 2024 — Turkey↔EU electricity flows

- **What it is**: Source for `EXPORTED_MWH` in `features/electricityGood.py`
  — gross Turkey→Greece (687,000 MWh) and Turkey→Bulgaria (1,856,000 MWh)
  physical electricity flows, read off the factsheet's "Physical energy
  flows" map (Balkans inset). **PROVISIONAL** — see `docs/open_issues.md`.
- **URL**: https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/Publications/Statistics/Factsheet/entsoe_sfs2024_web.pdf
- **Retrieval date**: TODO: confirm
- **Licence/terms**: ENTSO-E publishes statistical factsheets for public
  use with attribution; TODO: confirm exact redistribution terms if the map
  graphic itself (not just the read-off values) is reproduced in the paper.

### EMBER/IEA benchmark — grid carbon intensity (geothermal-zero basis)

- **What it is**: `EMBER_IEA_BENCHMARK = 0.4425` tCO2/MWh in
  `features/electricityGood.py` — the standard (geothermal-NCG-omitting)
  grid-carbon-intensity convention that the model's own NCG-adjusted build
  (0.4681) is validated against.
- **URL**: Ember's Yearly Electricity Data — https://ember-energy.org/data/yearly-electricity-data/
  (Ember's Türkiye country page: https://ember-climate.org/countries-and-regions/countries/turkey/).
  TODO: confirm the exact table/vintage this 0.4425 figure was read from —
  CLAUDE.md and the code cite it only as "Ember/IEA," not a specific
  table/page.
- **Retrieval date**: TODO: confirm
- **Licence/terms**: Ember publishes its Yearly Electricity Data under CC BY
  4.0 (free reuse with attribution); IEA data terms are more restrictive —
  TODO: confirm which organization's figure this specific number traces to
  before citing a licence.

### TEİAŞ Grafik 15 — considered, not used

- **What it is**: `CLAUDE.md`'s "Data inputs" section lists TEİAŞ (Türkiye
  Elektrik İletim A.Ş.) interconnector flow data as one candidate source for
  Turkey→EU electricity export volume ("ENTSO-E / TEİAŞ interconnector
  flows (Bulgaria/Greece)"). **This was not the source adopted** — the model
  uses the ENTSO-E Statistical Factsheet instead (see above). No TEİAŞ file
  or figure appears anywhere in the codebase. Documented here only because
  it was named as a candidate source; not an active input.

## Orphaned / unused files (kept, not deleted — see repo audit)

- **`euGridBaseline.csv`**: EEA (European Environment Agency) greenhouse-gas
  emission intensity of electricity generation indicator, downloaded from
  https://www.eea.europa.eu/en/analysis/indicators/greenhouse-gas-emission-intensity-of-1
  (URL is embedded in the file's own header). Not imported by any module in
  this repo — kept as-is per the "don't modify data files without asking"
  rule, not featured in the model.
- **`item1_cleaned.csv`, `item2_cleaned.csv`**: outputs of
  `cleanUp/item1CleanUp.py` and `cleanUp/item2CleanUp.py`'s `main()`
  functions respectively. Nothing downstream reads these — every
  `features/*.py` module re-parses the raw `item1.xlsx` / `item2.csv`
  directly via `parse_turkiye_defaults()` / `load_trade()`. Kept as
  pipeline-run artifacts, not treated as model inputs.
