# Implications Section — Citation Reference Sheet

**Purpose:** every number the Implications section needs, with its exact persisted
value, a rounded prose form, and where it came from — so prose-writing never
requires re-deriving or re-fetching a figure by hand.

Generated from persisted model outputs — values mirror the frozen model. This file
does not itself compute anything new beyond simple aggregation (sums/means/shares)
over already-persisted per-heading data, shown with its formula.

**Legend:** `LOCKED` = frozen, do not revisit without asking · `PROVISIONAL` = usable
but pending confirmation, must be hedged in prose · `EXTERNAL` = supplied context
fact, not derived from a repo artifact — verify independently before citing.

## Files read (source of truth)

| File | Found? | Used for |
|---|---|---|
| `CLAUDE.md` | Yes | Locked decisions, clustering params, emission-factor citations, provenance strings, quarantine notes |
| `output/steel_clusters.csv` | Yes | Frozen steel per-heading assignments (35 rows: hs4, description, direct_intensity, tonnes, exposure, cluster_label) |
| **steel cluster-summary CSV** | **Not found as a separate file** | No such file exists in `output/`. Per-cluster `n_headings` / `exposure_share` / `mean_direct` / `mean_tonnes` are **derived** below from `steel_clusters.csv` (formula shown per row), not copied from a summary file. CLAUDE.md's "Frozen membership" section states the same figures in rounded prose — cited alongside for cross-check. |
| `output/electricity_grid_intensity_bases.csv` | Yes | `ember_iea_benchmark`, `grid_intensity_ncg_adjusted`, `geothermal_ncg_delta` (3 rows) |
| `output/electricity_renewable_sweep.csv` | Yes | 21-row renewable-share sweep (0–100%, 5pp step): renewable_share, intensity, exposure |
| `output/electricity_exposure_current.csv` | Yes | Current-state exposure, `exported_mwh` and its two border components, source, reference year, PROVISIONAL status |
| Cross-sector (6-good) exposure ranking CSV | **Not found** | The 68% / 91% / 23% / 7% / 2% sector figures exist only as LOCKED prose in `CLAUDE.md` ("Locked decisions"). No underlying per-sector exposure CSV was found in this repo — flagged, not fabricated. |

---

## GUARDRAILS — read before writing a single sentence

1. **`exported_mwh` (2,543,000 MWh) and the ~1.19 MtCO2 electricity exposure are
   PROVISIONAL and a FLOOR, not a point estimate.** The ENTSO-E factsheet arrow
   value is an hourly-netted annual directional figure — true CBAM-relevant gross
   inflow is **≥** this number. Any electricity-magnitude claim in prose must be
   hedged ("provisional," "at least," "a lower-bound estimate") — never stated as
   a settled figure.
2. **Cite 5.8%** for the geothermal NCG finding (`grid_intensity_ncg_adjusted`
   0.4681 vs. `EMBER_IEA_BENCHMARK` 0.4425 → +0.0256, **+5.796% ≈ 5.8%**). **Do NOT
   cite 6.4%** anywhere in prose — that number (+6.421%) comes from comparing
   0.4681 against our OWN geothermal-zero validation build (0.4399), a different,
   internal comparison base (used only to check the build is sound, not as an
   external benchmark). Mixing the two creates a prose/model inconsistency.
3. **CBAM electricity market-coupling scope is an open framing question.** Whether
   /how CBAM applies to electricity given EU internal market-coupling mechanics is
   not resolved by this model. Flag it as an open question in prose — do not
   assert a settled position.

---

## Standing facts (EXTERNAL — for framing sentences, not model pillars)

| Fact | Detail | Source | Status |
|---|---|---|---|
| CBAM timeline | Definitive period began Jan 2026; first certificate surrender Sept 2027; phases in to 2034 | Per CLAUDE.md "Framing" section | EXTERNAL |
| 2024 pivot | Türkiye moved net importer → net exporter of electricity in 2024; record demand 342 TWh | Ember Türkiye Electricity Review 2025 | EXTERNAL |
| Sovereign rating | BB−/Ba3 — three notches below BBB− (investment grade) | As supplied for this task | EXTERNAL |

---

## PILLAR 1 — Exposure insulated from the buildout (steel, direct-emissions)

### Headline sector figures

| Figure | Precise value (as persisted) | Prose form | Citable source | Repo file | Status |
|---|---|---|---|---|---|
| Steel share of CBAM exposure | 68% | "68%" | CLAUDE.md, "Locked decisions" | CLAUDE.md (no backing CSV found) | LOCKED |
| Steel + cement share | 91% | "91%" — the two-sector cliff | CLAUDE.md, "Locked decisions" | CLAUDE.md (no backing CSV found) | LOCKED |
| Cement / aluminium / fertilisers / hydrogen shares | 23% / 7% / 2% / ~0% | as listed | CLAUDE.md, "Locked decisions" | CLAUDE.md (no backing CSV found) | LOCKED |

### Steel clustering parameters

| Figure | Precise value | Prose form | Citable source | Repo file | Status |
|---|---|---|---|---|---|
| Join level | HS4 | "HS4-level" | CLAUDE.md, "Locked decisions" | CLAUDE.md | LOCKED |
| Model type | Direct-emissions only (exposure = direct × tonnes; no indirect, no grid factor) | "direct-emissions-only exposure model" | CLAUDE.md, "Locked decisions" | CLAUDE.md | LOCKED |
| Cleaned heading count | 35 (of 42; 7 dropped, tonnes ≤ 1000) | "35 HS4 headings" | CLAUDE.md, "Clustering (steel) — FROZEN" | CLAUDE.md + `output/steel_clusters.csv` (35 data rows) | LOCKED |
| k (clusters) | 3, fixed | "three clusters" | CLAUDE.md, "Clustering (steel) — FROZEN" | CLAUDE.md | LOCKED |
| Silhouette score | 0.508 | "silhouette 0.51" | CLAUDE.md, "Clustering (steel) — FROZEN" | CLAUDE.md | LOCKED |

### The three steel clusters

Formula for `exposure_share`: `Σ(exposure where cluster_label = X) ÷ Σ(exposure, all 35 rows)`, computed directly from `output/steel_clusters.csv`. Denominator = 19,673,818.68 tCO2 (the 35-heading clustered book — see note below). `mean_direct` = `mean(direct_intensity)` within cluster; `mean_tonnes` = `mean(tonnes)` within cluster; `n_headings` = `count(hs4)` within cluster.

| Cluster | n_headings | exposure_share (derived, 35-book) | exposure_share (CLAUDE.md prose, 42-book) | mean_direct | mean_tonnes | Status |
|---|---|---|---|---|---|---|
| commodity-volume | 14 | 0.817624 (81.76%) | 81.7% | 2.628463 | 416,014.20 | LOCKED |
| specialty-intensity | 12 | 0.150775 (15.08%) | 15.1% | 5.994044 | 39,752.75 | LOCKED |
| moderate-middle | 9 | 0.031601 (3.16%) | 3.2% | 2.763360 | 25,476.44 | LOCKED |

Note: the two `exposure_share` columns differ only in denominator — CLAUDE.md's prose figures are shares of the full 42-heading steel book (including the 7 dropped near-zero-volume headings, whose combined exposure is ~0.02% of the total); the derived column here is shares of the 35-heading clustered book that's actually persisted in `steel_clusters.csv`. The two never differ by more than ~0.03 percentage points — either is safe to cite; do not present both as if they contradict.

### Heading 7308 (single-heading spotlight)

Formula: read directly from `output/steel_clusters.csv`; share = `7308 exposure ÷ Σ(exposure, all 35 rows)`.

| Figure | Precise value | Prose form | Citable source | Repo file | Status |
|---|---|---|---|---|---|
| direct_intensity | 5.52 | "5.52 tCO2/t" | Row hs4=7308 | `output/steel_clusters.csv` | LOCKED |
| tonnes | 511,885.065 | "~512,000 tonnes" | Row hs4=7308 | `output/steel_clusters.csv` | LOCKED |
| exposure | 2,825,605.56 tCO2 | "~2.83 MtCO2" | Row hs4=7308 | `output/steel_clusters.csv` | LOCKED |
| Share of total steel exposure | 2,825,605.56 ÷ 19,673,818.68 = 0.143623 (14.36%) | "~14% of total steel CBAM exposure — one heading" | Derived from `output/steel_clusters.csv` | `output/steel_clusters.csv` | LOCKED |
| Cluster membership | commodity-volume | "the largest single exposure inside the commodity-volume cluster" | Row hs4=7308 | `output/steel_clusters.csv` | LOCKED |

Note (cross-reference, not a contradiction): 7308's `direct_intensity` (5.52) sits close to `specialty-intensity`'s floor (5.36) — the largest single commodity-volume exposure is also the closest commodity-volume heading to the specialty-intensity boundary. Worth a sentence if the prose discusses cluster-boundary cases, not a data error.

### Total steel exposure book

| Figure | Precise value | Prose form | Citable source | Repo file | Status |
|---|---|---|---|---|---|
| Total steel exposure (35-heading clustered book) | Σ exposure, all 35 rows = 19,673,818.68 tCO2 | "~19.7 MtCO2" | Derived: `Σ(exposure)` over all rows in `output/steel_clusters.csv` | `output/steel_clusters.csv` | LOCKED |

---

## PILLAR 2 — The lever has a floor (renewable-share sweep, electricity good)

| Figure | Precise value | Prose form | Citable source | Repo file | Status |
|---|---|---|---|---|---|
| Operative grid intensity (geothermal-real basis) | 0.468148 tCO2/MWh | "0.4681 tCO2/MWh" | Row `grid_intensity_ncg_adjusted` | `output/electricity_grid_intensity_bases.csv` | LOCKED |
| Renewable-share sweep range | 0.00 to 1.00 (renewable_share column) | "0–100% renewable share" | Full column | `output/electricity_renewable_sweep.csv` | LOCKED |
| Sweep step | 0.05 (5 percentage points) | "5-point-pass increments" | Derived: consecutive row spacing | `output/electricity_renewable_sweep.csv` | LOCKED |
| Sweep row count | 21 | "21 scenario points" | `len(sweep)` | `output/electricity_renewable_sweep.csv` | LOCKED |
| Intensity floor at 100% renewable share | 0.067185 tCO2/MWh | "~0.067 tCO2/MWh — not zero" | Row renewable_share=1.00 | `output/electricity_renewable_sweep.csv` | LOCKED |
| Basis note | Geothermal-real (0.887 tCO2/MWh factor applied at every scenario point) | "the floor exists because geothermal keeps its real emission factor even at 100% 'renewable' share" | CLAUDE.md, "Electricity good — Renewable-share lever" | CLAUDE.md + `output/electricity_renewable_sweep.csv` | LOCKED |

---

## PILLAR 3 — Reported cleanliness overstated (two-basis grid intensity)

| Figure | Precise value | Prose form | Citable source | Repo file | Status |
|---|---|---|---|---|---|
| `EMBER_IEA_BENCHMARK` | 0.4425 tCO2/MWh | "0.4425 tCO2/MWh (Ember/IEA, geothermal-zero)" | Row `ember_iea_benchmark` | `output/electricity_grid_intensity_bases.csv` | LOCKED |
| `grid_intensity_ncg_adjusted` | 0.468148 tCO2/MWh | "0.4681 tCO2/MWh (our build, geothermal-real)" | Row `grid_intensity_ncg_adjusted` | `output/electricity_grid_intensity_bases.csv` | LOCKED |
| `geothermal_ncg_delta` (absolute) | +0.025648 tCO2/MWh | "+0.0256 tCO2/MWh" | Row `geothermal_ncg_delta` | `output/electricity_grid_intensity_bases.csv` | LOCKED |
| `geothermal_ncg_delta` (percent, CORRECT figure to cite) | 0.025648 ÷ 0.4425 = 0.057960 (5.796%) | **"+5.8%"** | Derived from `output/electricity_grid_intensity_bases.csv` (matches provenance string in same file) | `output/electricity_grid_intensity_bases.csv` | LOCKED |
| Provenance string | "standard grid accounting understates Turkey's grid carbon intensity by 5.8% (+0.0256 tCO2/MWh) via omitted geothermal NCG (non-condensable gas) degassing" | verbatim | Row `geothermal_ncg_delta`, description column | `output/electricity_grid_intensity_bases.csv` | LOCKED |
| Geothermal-zero validation build | 0.4399 tCO2/MWh | "0.4399 tCO2/MWh" | CLAUDE.md, "Electricity good — TWO ACCOUNTING BASES" (not separately persisted to a CSV) | CLAUDE.md | LOCKED |
| Validation gap vs. benchmark | 0.4399 vs 0.4425 = −0.0026, **−0.6%**, within ±2% tolerance → PASSES | "validation confirms the gap is attributable to geothermal, not a build error" | CLAUDE.md, same section | CLAUDE.md | LOCKED |
| Alternate percent (DO NOT CITE) | (0.468148 − 0.4399) ÷ 0.4399 = 0.064213 (6.421% ≈ "6.4%") | — never state in prose — | Derived, internal comparison base only (ncg_adjusted vs. the validation build, not vs. the benchmark) | n/a | **DO NOT USE** |

### Emission factors with citations

| Fuel | Factor (tCO2/MWh) | Citation | Source | Status |
|---|---|---|---|---|
| Geothermal | 0.887 | Herrera Martinez et al. (2016), weighted average across 12 Turkish plants, 2015 data; ~7x the ~121 g/kWh global average | CLAUDE.md, "Electricity good" + "Known open items" (vintage flag: fleet has grown since 2015, factor evolves over well lifetime — footnote-tier) | LOCKED (factor) / footnote-tier (vintage) |
| Lignite | 1.08 | Sözen et al., Energy Policy (~2011-2012), "Carbon dioxide emission from the Turkish electricity sector and its mitigation options" — Turkey-specific, not generic 1.10; same study also validates gas at 0.374 (matches generic 0.37 in use) | CLAUDE.md, "Electricity good" | LOCKED |
| Gas / LNG / naphtha | 0.37 | IPCC/IEA generic; corroborated Turkey-specific (0.374) by Sözen et al. | CLAUDE.md, "Emission factors" | LOCKED |
| Hard / imported / asphaltite coal | 0.90 | IPCC/IEA generic | CLAUDE.md, "Emission factors" | LOCKED |
| Fuel oil | 0.65 | IPCC/IEA generic | CLAUDE.md, "Emission factors" | LOCKED |
| Wind / solar / hydro | ≈0 | Operational direct-emissions convention (stated explicitly, not defaulted silently) | CLAUDE.md, "Emission factors" | LOCKED |
| Biomass | ≈0 | Biogenic/carbon-neutral convention | CLAUDE.md, "Emission factors" | LOCKED |

---

## LANDING

| Figure | Precise value | Prose form | Citable source | Repo file | Status |
|---|---|---|---|---|---|
| Current-state electricity exposure | 1,190,499.10 tCO2 | "~1,190,499 tCO2" | `exposure_tco2` column | `output/electricity_exposure_current.csv` | **PROVISIONAL** |
| `exported_mwh` (gross, TR→EU) | 2,543,000 MWh | "2,543,000 MWh gross" | `exported_mwh` column | `output/electricity_exposure_current.csv` | **PROVISIONAL** |
| — TR→GR component | 687,000 MWh | "687,000 MWh to Greece" | `exported_mwh_tr_gr` column | `output/electricity_exposure_current.csv` | **PROVISIONAL** |
| — TR→BG component | 1,856,000 MWh | "1,856,000 MWh to Bulgaria" | `exported_mwh_tr_bg` column | `output/electricity_exposure_current.csv` | **PROVISIONAL** |
| Source | ENTSO-E Statistical Factsheet 2024, "Physical energy flows" map (Balkans inset) | as given | `exported_mwh_source` column | `output/electricity_exposure_current.csv` | **PROVISIONAL** |
| Reference year | 2024 | "2024 (Türkiye's first net-export year — flows volatile)" | `exported_mwh_reference_year` column | `output/electricity_exposure_current.csv` | **PROVISIONAL** |
| Status string (verbatim) | "PROVISIONAL -- pending Aras confirmation of gross figure + direction" | — | `exported_mwh_status` column | `output/electricity_exposure_current.csv` | **PROVISIONAL** |

### The 91%-insulated / one-lever framing

| Claim | Supporting figures | Status |
|---|---|---|
| ~91% of CBAM exposure (steel + cement) is direct-emissions, grid-independent — does not move with the renewable buildout | Steel 68% + cement 23% = 91% (CLAUDE.md, "Locked decisions"); steel model is direct-emissions-only (CLAUDE.md, "CRITICAL guardrail") | LOCKED |
| The renewable-generation link exists in exactly one place — the electricity good — and even there it has a floor, not a path to zero | `grid_intensity_ncg_adjusted` 0.4681 → sweep floor 0.067 at 100% share (`output/electricity_renewable_sweep.csv`); floor is non-zero because geothermal keeps its real 0.887 factor | LOCKED |
| The one lever's own reported magnitude is provisional and understated by both accounting basis (geothermal NCG) and by data status (exported_mwh) | 5.8% NCG understatement (LOCKED) + exported_mwh/exposure PROVISIONAL, stated as a floor not a point estimate | Mixed — see per-row status above |
