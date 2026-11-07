# Open items

GitHub-issue-ready write-ups of every unresolved item surfaced by the repo
audit and named in `CLAUDE.md`. None of these have been acted on — per the
hard rule for this reproducibility pass, anything that looked wrong was
documented here, not fixed.

---

## 1. Confirm `exported_mwh` via the ENTSO-E Transparency Platform API

**Labels**: `data`, `blocking-provisional`

**Context**: `features/electricityGood.py`'s `EXPORTED_MWH` (2,543,000 MWh =
TR→GR 687,000 + TR→BG 1,856,000) was read manually off the directional
arrows on a published PDF map (ENTSO-E Statistical Factsheet 2024, "Physical
energy flows," Balkans inset) — not pulled from a structured data source.
It is explicitly flagged `PROVISIONAL` in the code, in `data/README.md`, and
in every output file that depends on it.

**What depends on it**: `electricity_exposure_current.csv`'s exposure figure
(≈1.2 MtCO₂) and the `exposure` column of `electricity_renewable_sweep.csv`
are both `intensity × EXPORTED_MWH` — both inherit the provisional status.

**Proposed next step**: pull the equivalent TR→GR / TR→BG physical flow
figures from the ENTSO-E Transparency Platform API
(https://transparency.entsoe.eu/), which requires a registered API token
(see `.env.example` — `ENTSOE_API_TOKEN`, loaded via `python-dotenv`, not
hardcoded). Compare against the factsheet-derived figure used here; if they
agree within a reasonable tolerance, promote `EXPORTED_MWH` from
provisional to locked and re-run `python -m cbam_exposure run` to
regenerate the two dependent output files (currently labelled PROVISIONAL
in their own columns) without that label.

**Why it matters**: this is the single open item standing between the
electricity-exposure figure and being citable as final rather than a lower
bound.

---

## 2. HS4 2601 — intensity and flow-direction discrepancy

**Labels**: `data`, `footnote-tier`

**Context**: HS4 2601 (agglomerated iron ores and concentrates) sits in the
frozen steel clustering's `commodity-volume` cluster with a carried direct
intensity of 0.18 tCO₂/t (this repo's aggregation of `item1_cleaned.csv`).
The officially published EU default for the more specific CN code 2601 12 00
is 0.31 tCO₂/t — a discrepancy not yet investigated.

Separately, it has not been verified that Türkiye is genuinely the exporting
party of record for this heading to EU-27 in the pulled Comext data, rather
than a reporting or re-export artifact.

**Proposed next step**: (a) check whether the 0.18 figure is a mean across
multiple CN8/CN6 children with real intensity spread, vs. CN 2601 12 00
specifically; (b) spot-check the Comext flow for this heading against a
second source (e.g. UN Comtrade) to confirm Türkiye-as-exporter is not a
transit/re-export quirk.

**Why it matters**: neither issue currently changes the frozen clustering
result (2601's exposure share is small), but both are the kind of thing a
supervisor or reviewer would ask about specifically, given how visible HS4
2601 is in the commodity-volume cluster.

---

## 3. Geothermal NCG emission factor — vintage check

**Labels**: `data`, `sensitivity`

**Context**: `TURKEY_EMISSION_FACTORS["Jeotermal"] = 0.887` tCO₂/MWh comes
from Herrera Martinez et al. (2016), a weighted average across 12 Turkish
plants using 2015 data. Türkiye's geothermal fleet has grown materially
since 2015, and the literature notes the NCG (non-condensable gas) factor
evolves over a well's lifetime — typically declining as reservoir gas
dilutes.

**Proposed next step**: if a more recent fleet-weighted NCG emission factor
for Turkish geothermal becomes available, re-run the two-basis comparison
(`validate_against_benchmark`, `geothermal_ncg_delta`) with the updated
factor as a sensitivity check, not a silent replacement — the current 0.887
figure should stay cited alongside any update, with the vintage difference
noted explicitly.

**Why it matters**: this factor directly drives the +5.8% two-basis delta
and the renewable-share sweep's non-zero floor (≈0.067 tCO₂/MWh at 100%
"renewable" share) — both are citable findings in the paper.

---

## 4. Possible newer CBAM default-values regulation supersedes `item1.xlsx`

**Labels**: `data`, `needs-decision`

**Context**: `data/item1.xlsx` (version 1, dated 2026-02-04, per its own
"Version History" sheet) is built from Commission Implementing Regulation
(EU) 2025/2621 of 16 December 2025. On 2026-07-30/31, the European
Commission published Commission Implementing Regulation (EU) 2026/1740,
which replaces Annex I and Annex IV of 2025/2621 with corrected default
values. This repo's steel/cement/aluminium/fertiliser/hydrogen exposure
figures — i.e. everything except the electricity good — are built from the
pre-correction annex.

**Proposed next step**: obtain the corrected Annex I/IV workbook, diff its
Türkiye-sheet values against the current `item1.xlsx` for the CN codes this
model actually uses, and decide whether the correction moves any locked
figure by more than the existing 1pp reproduction tolerance used when the
cross-sector table was adopted (see `CLAUDE.md`, "Locked decisions"). If it
does, that is a deliberate re-adoption decision for the model owner, not an
automatic update.

**Why it matters**: every sector-ranking and steel-clustering number in
this repo traces back to this one file. A corrected default-values
annex is exactly the kind of change CLAUDE.md's "do not modify data files
without asking" rule is meant to gate.

---

## 5. Cement's exposure figure is the least Türkiye-specific of the five

**Labels**: `footnote`, `paper-writing`

**Context**: 7 of cement's 8 CN codes show `–` for direct emissions on the
Türkiye sheet of `item1.xlsx` and are filled from the generic EU default
(`_Other Countries and Territorie` sheet, `is_fallback` flag in
`cleanUp/item1CleanUp.py`). Only CN 25233000 (Aluminous cement) carries a
Türkiye-specific value. This is already flagged in code comments,
`CLAUDE.md`, and `output/cbam_cross_sector_exposure.csv`'s `method` column
— this entry exists so it isn't lost as a standalone action item.

**Proposed next step**: none required for the model itself — this is a
data-provenance caveat for the paper's methods note/footnotes, not a bug.
Cite the fallback explicitly wherever cement's 21.62% figure is used.

**Why it matters**: a supervisor is likely to ask why cement's figure is
less certain than steel's — having the answer pre-written avoids scrambling
for it during review.
