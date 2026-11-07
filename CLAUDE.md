# turkey-cbam-exposure

## What this is
A Python model scoring Turkish industrial sectors' exposure to the EU Carbon
Border Adjustment Mechanism (CBAM). Output is cited in the Implications section
of a research note ("Paper Capacity: Why Turkey's Renewable Buildout Is Not
Delivering Clean Generation") — an analyst note for a banking application,
supervised by a Bristol academic.

The model MUST be genuinely ML-based (clustering), not threshold rules dressed
up as ML. This is non-negotiable.

## Framing (keep prose and model consistent)
- CBAM is binding as of the definitive period (Jan 2026) on a deferred-settlement
  basis: cost accrues now, first certificate surrender Sept 2027, phases in to
  2034. Do NOT describe CBAM as "not yet binding" or merely "emerging."
- The model measures ONE thing: carbon-cost-at-the-border for Turkey->EU trade.
  It does not measure financing, WACC, or LNG. Never imply it does.

## Model scope (FINAL — decided, do not expand without asking)
The model has three outputs, no more:
1. **Sector-level exposure ranking** across all six CBAM goods (steel, cement,
   aluminium, fertilisers, electricity, hydrogen). This is the headline.
2. **Steel — direct-emissions, clustered.** The only sector with enough HS4
   headings to have citable internal structure. This is the centrepiece (68%
   of exposure).
3. **Electricity — indirect/grid-emissions, computed.** The one good whose
   exposure is pure grid carbon, so it moves with renewable generation. This
   is where the renewable-energy link lives, and where turkey_grid_intensity
   is finally used as a model input.

Steel and electricity are the two faces of CBAM exposure — direct
(grid-independent, binding now) and indirect (grid-driven, renewable-dependent).
The contrast between them IS the analytical point tying the model to the paper's
Generation Gap opening.

- **No per-sector clustering beyond steel.** Cement (8 headings) and hydrogen
  (1) are too few — ranking only. Aluminium (~24) and fertilisers (~27) may be
  clustered as a diagnostic ONLY if silhouette clears ~0.3; otherwise ranking
  only. Do not force clustering where n can't support it.
- **VIIRS is CUT.** Nighttime-lights corroboration is redundant — official
  Eurostat trade data proves industrial activity harder than satellite radiance
  would. It had no citable sentence left. Do not reintroduce.

## CRITICAL guardrail (anti-thin-air)
The renewable-generation link lives in the ELECTRICITY good ONLY.
Steel exposure is DIRECT emissions (coking, blast furnace, process chemistry) —
it does NOT move when Turkey's renewable share moves. NEVER write or imply that
renewables reduce steel's CBAM exposure. That claim is unsupported by the model
and is exactly the failure mode to avoid.

## Data inputs (all cleaned; do not modify without asking)
- Item 1 — EU CBAM default emission values, Türkiye sheet. Columns: direct /
  indirect / total intensity per CN code, plus 2026/2028 mark-ups. Missing
  Türkiye values filled from `_Other Countries` sheet, flagged `is_fallback`.
  NOTE: indirect is N/A for steel and aluminium at HS4 — see retired option 3.
- Item 2 — `load_trade.py`: Eurostat Comext DS-045409, Turkey->EU imports, 2024,
  EU-27 aggregate reporter. Returns 65 HS4 headings: hs4 / tonnes / value_eur.
  (Comext quantity is in 100kg units — divided by 10 for tonnes.)
- Item 3 — `item3.csv`: consolidated 2024 hourly Turkish grid generation from
  EPİAŞ, 8,784 rows (366×24), deduped. Derived cols: gen_total_MWh,
  gen_thermal_MWh, gen_renewable_MWh, thermal_share.
- TO SOURCE (electricity good): Turkey->EU electricity export volume (MWh),
  recent full year. Eurostat electricity trade, or ENTSO-E / TEİAŞ
  interconnector flows (Bulgaria/Greece).

## Locked decisions (do not revisit without asking)
- Join level is HS4. Not CN8, not sector-level.
- **Sector exposure ranking — CSV-backed, adopted 2026-07-18**: steel 68.97%
  (~69%), cement 21.62%, aluminium 7.00%, fertilisers 2.11%, hydrogen 0.30%.
  steel + cement = 90.59%. Source: `output/cbam_cross_sector_exposure.csv`,
  built by `features/crossSectorExposure.py` (same direct × tonnes / HS4-join
  method as `steelFeatures.py`, applied to all five direct-emissions goods;
  electricity excluded — separate good, different units, not part of this
  table). This is now the locked figure — do not revisit without asking.
  **Supersedes the prior prose figure** (steel 68%, cement 23%, aluminium 7%,
  fertilisers 2%, hydrogen ~0%, steel+cement 91%), which had no reconstructable
  backing CSV. Adoption rationale: the computed table is method-validated
  (full-book steel, 42 headings, 19,676,944.91 tCO2, reconciles to the frozen
  cleaned-35 book's 19,673,818.68 tCO2 within 0.016% — confirmed, not assumed)
  and fully traceable, including the documented cement fallback (see below);
  the old 23% cement figure could not be reconstructed from any input. Divergence
  record: computed cement (21.62%) differed from the prior prose figure (23%)
  by −1.38pp, above the 1pp reproduction tolerance — every other sector matched
  within ~1pp. That divergence, not a data error, is why the figure changed.
  **Cement is the least Türkiye-specific sector figure**: 7 of its 8 CN codes
  use the generic EU default direct-emissions value (`_Other Countries and
  Territorie` sheet fallback, `is_fallback` flag) because the Türkiye sheet
  showed `–` for direct on those codes; only CN 25233000 (Aluminous cement) is
  Türkiye-specific. Flagged for a paper footnote — cement's number is the
  shakiest of the five on data-specificity grounds, independent of whether the
  exposure math itself is right.
- Exposure model is DIRECT-EMISSIONS ONLY, fully official inputs:
  exposure per HS4 heading = direct × tonnes. No indirect, no grid factor,
  no gap. (Electricity good is the one exception — see below — and uses grid
  intensity, not the direct-values file.)
- Indirect-emissions design (OPTION 3) is RETIRED. The EU default-values file
  reports indirect as N/A for steel and aluminium at HS4, so there was nothing
  to back a per-product electricity intensity out of. Do not revisit the
  gap / turkey-adjusted-indirect approach without a genuine per-heading indirect
  data source. N/A must never be coerced to 0.
- `turkey_grid_intensity` is TWO NAMED BASES, not one number — see
  "Electricity good" below. `grid_intensity_ncg_adjusted` = **0.4681
  tCO2/MWh** (2024) is operative for the electricity-good exposure input and
  prose context. `EMBER_IEA_BENCHMARK` = **0.4425** is a named external
  benchmark (Ember/IEA, geothermal-zero accounting) — kept, cited, NOT
  superseded or deleted. The 5.8% gap between them is a finding (omitted
  geothermal NCG degassing), not an error. NOT a steel-feature input either
  way.

## Clustering (steel) — FROZEN (do not re-run a k-sweep; re-derive only if an
input file changes, and if so re-run `features/steelClusterFrozen.py` and
update the numbers below)
- Module: `features/steelClusterFrozen.py`. `features/clustering.py` remains
  the exploratory/diagnostic pipeline (k-sweep, DBSCAN, transform comparisons)
  — kept for robustness checks, not re-run for the frozen result.
- Universe: canonical 35-heading set. Drop rule (single source of truth:
  `clustering.STEEL_DROP_TONNES_FLOOR` / `drop_near_zero_exporters`) — tonnes
  <= 1000 dropped. 7 removed: 7201, 7203, 7206, 7218, 7221, 7223, 7301. These
  are products Turkey barely exports to the EU — negligible exposure
  regardless of intensity, excluded from structure analysis but counted in
  the sector total (their combined exposure share is ~0.02%, see below). State
  this filter and rationale explicitly in the methods note (a supervisor will
  ask why 35 not 42).
- Feature space: `direct` (as-is) + `log1p(tonnes)`, both z-scored
  (StandardScaler). NEVER `value_eur`, NEVER `exposure` (circular — exposure =
  direct × tonnes), NEVER grid intensity (steel exposure is grid-independent;
  `steelClusterFrozen.py` must not import `gridIntensity`).
- k = 3, fixed (no sweep in this module). `random_state = 42`, passed
  explicitly to `KMeans`.
- **Silhouette = 0.508** (regression guard: `SILHOUETTE_EXPECTED = 0.51`,
  tolerance `± 0.05`, asserted in `tests/test_steel_cluster_frozen.py`).
  NOTE: this corrects the earlier exploratory-diagnostic figure of "~0.55" —
  that number came from a `sqrt` volume transform; the frozen spec mandates
  `log1p`, which scores slightly lower on silhouette but leaves the
  specialty-intensity membership identical and only shifts a few headings
  across the commodity/moderate boundary. 0.508 is the number to cite.
- Semantic labels are assigned deterministically by centroid position in the
  standardised feature space (highest-tonnes centroid -> commodity-volume,
  highest-direct of what remains -> specialty-intensity, remainder ->
  moderate-middle) — reproducible regardless of KMeans' arbitrary label
  numbering or input row order.
- **Frozen membership (verified against CN descriptions — labels match):**
    - **commodity-volume** (14 headings, 81.7% of total steel exposure, mean
      direct 2.63, mean tonnes 416k): 2601, 7207, 7208, 7209, 7210, 7213,
      7214, 7216, 7217, 7305, 7306, 7308, 7318, 7326 — flat-rolled, bars/rods,
      structural products, pipe/tube. Genuinely bulk/commodity steel.
    - **specialty-intensity** (12 headings, 15.1%, mean direct 5.99, mean
      tonnes 40k): 7219, 7220, 7222, 7224, 7225, 7226, 7227, 7228, 7229, 7302,
      7309, 7311 — stainless, alloy, silicon-electrical steel, pressure
      containers. Genuinely alloy/stainless/specialty.
    - **moderate-middle** (9 headings, 3.2%, mean direct 2.76, mean tonnes
      25k): 7202, 7205, 7211, 7212, 7215, 7303, 7304, 7307, 7310 — ferro-
      manganese, granules, cast-iron pipe fittings, misc small-volume.
      Neither-nor.
  The finding: steel exposure splits into a volume-driven and an
  intensity-driven type — NOT recoverable from the exposure ranking (which
  collapses both axes). This is the citable ML result.
- DBSCAN cross-check on the cleaned 35 was NOT re-run as part of the freeze
  (out of scope for `steelClusterFrozen.py` — it's k-means-only by design).
  If a DBSCAN corroboration is wanted for the Implications write-up, run it
  via `clustering.py`'s exploratory pipeline and report honestly whether it
  agrees; do not claim convergence that isn't there.
- Output: per-heading assignments (hs4, description, direct_intensity,
  tonnes, exposure, cluster_label) persisted to `output/steel_clusters.csv`
  by `features/steelClusterFrozen.py`'s `main()`. This file is what
  Implications cites — regenerate it if any upstream input changes, don't
  hand-edit it.

## Known open items (footnote-tier, deferred — do not act without asking)
- **HS4 2601** (agglomerated iron ores and concentrates), in the frozen steel
  clustering (`commodity-volume`, direct=0.18):
    1. Comext flow-direction unconfirmed — has not been verified that Turkey
       is genuinely the exporting party of record for this heading to EU-27
       in the pulled Comext data, rather than a reporting/re-export quirk.
    2. Carried intensity is 0.18 (our item1_cleaned aggregation), vs the
       officially published EU default for CN 2601 12 00 specifically, which
       is 0.31. Discrepancy not yet investigated.
  Neither blocks current results; both are footnote-tier for the methods
  note. Do not resolve or re-derive without asking.
- **Geothermal NCG factor vintage** (0.887 tCO2/MWh, Herrera Martinez et
  al. 2016, 12-plant 2015 weighted average): the Turkish geothermal fleet
  has grown materially since 2015, and the literature notes the factor
  evolves over a well's lifetime. Treat as a sensitivity, not a fixed
  constant. Footnote-tier, not blocking.
- **`exported_mwh` PROVISIONAL — pending Aras confirmation of gross figure
  + direction.** NOT locked. Adopted value: **2,543,000 MWh** (GROSS
  Turkey→EU physical flow, reference year 2024) = TR→GR 687,000 MWh +
  TR→BG 1,856,000 MWh. Source: ENTSO-E Statistical Factsheet 2024,
  "Physical energy flows" map (Balkans inset) —
  https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/Publications/Statistics/Factsheet/entsoe_sfs2024_web.pdf.
  Read directly off the map's directional arrows (not the net balance);
  both borders show Turkey netting as an exporter, consistent with
  Türkiye's 2024 net-exporter status — a consistency check, not proof,
  since this was read visually off a compressed map graphic rather than a
  raw structured data table (ENTSO-E Transparency Platform API access
  would give higher confidence but requires a registered token not
  available in this environment). A 2025 factsheet does not yet exist
  (2025 statistical reports were published March 2026 but the polished
  map factsheet has not followed) — 2024 used per the documented
  fallback. This is GROSS directional flow, NOT Turkey's net cross-border
  balance and NOT any "net exporter" headline figure. Confirm before
  treating as final.

## Electricity good — BUILT (`features/electricityGood.py`)
Fully separate module. Must never import `steelFeatures.py`, `clustering.py`,
or `steelClusterFrozen.py` — enforced by `tests/test_electricity_good.py`.
The renewable-generation link lives ONLY here.

- **Grid intensity is a computed function of the generation mix**, not a
  hardcoded input: `grid_intensity(mix, factors)` = generation-weighted sum
  over `TURKEY_EMISSION_FACTORS`.
- **Turkey-specific factors, sourced (not generic IPCC/IEA defaults):**
    - Geothermal = **0.887 tCO2/MWh, NOT zero.** Turkish geothermal
      (Kızıldere, Germencik etc.) degasses reservoir CO2 through
      non-condensable gas (NCG) venting. Herrera Martinez et al. (2016) —
      weighted average 887 g/kWh across 12 Turkish plants, 2015 data. ~7x
      the ~121 g/kWh global average cited in the same literature.
      **Vintage flag (footnote-tier, not blocking):** the Turkish geothermal
      fleet has grown materially since 2015, and the literature notes the
      NCG factor evolves over a well's lifetime (typically declining as
      reservoir gas dilutes) — treat 0.887 as a sensitivity, not a fixed
      constant, if a more recent fleet-weighted estimate surfaces.
    - Lignite = **1.08 tCO2/MWh**, Turkey-specific domestic low-calorific
      lignite. Sözen et al., Energy Policy (~2011-2012), "Carbon dioxide
      emission from the Turkish electricity sector and its mitigation
      options" — empirical Turkish fleet estimate (also validates gas at
      0.374, matching the generic 0.37 already in use).
    - Gas/LNG/naphtha 0.37, hard/imported/asphaltite coal 0.90, fuel oil
      0.65, wind/solar/hydro 0 (operational direct convention), biomass 0
      (biogenic convention) — generic IPCC/IEA, no Turkey-specific override
      located/needed.

- **TWO ACCOUNTING BASES — this is a structural decision, not a bug fix.**
  An earlier pass overwrote the 0.4425 figure with 0.4681 and mislabeled it
  as user-approved supersession. That was wrong: 0.4425 (Ember/IEA) and
  0.4681 (our build) are two DIFFERENT, both-legitimate accounting bases
  that disagree only on how geothermal NCG is treated. Corrected structure:
    - **`EMBER_IEA_BENCHMARK = 0.4425`** — standard grid-carbon accounting,
      geothermal ~0 (NCG omitted by convention). Named constant, cited, kept
      permanently. NOT legacy, NOT superseded, NOT deleted.
    - **`grid_intensity_ncg_adjusted = 0.4681`** — our bottom-up build, same
      generation mix, geothermal costed at its real 0.887 factor. This is
      the OPERATIVE figure for `electricity_exposure()` and the
      renewable-share sweep.
    - **Validation run** (`validate_against_benchmark`): forces geothermal to
      0 in our own build and checks it reproduces `EMBER_IEA_BENCHMARK`
      within ± 2%. Result: **0.4399 vs 0.4425, gap −0.6%, PASSES.** This
      confirms the 5.8% gap between the two bases is attributable entirely
      to the geothermal NCG treatment, not a mix/methodology error — if this
      validation ever fails, STOP and investigate before trusting either
      downstream figure (a non-geothermal factor or the mix would have
      drifted too).
    - **`geothermal_ncg_delta`** — the named, citable result: delta =
      +0.0256 tCO2/MWh (+5.8%). Provenance: "standard grid accounting
      understates Turkey's grid carbon intensity by 5.8% via omitted
      geothermal NCG degassing." Persisted to
      `output/electricity_grid_intensity_bases.csv` (three rows: benchmark,
      ncg_adjusted, delta) — Implications cites this file.
    - `features/gridIntensity.py`'s `EMISSION_FACTORS` computes the
      NCG-adjusted basis (kept in sync with `TURKEY_EMISSION_FACTORS`); the
      benchmark lives only in `electricityGood.py`.
- Current (2024) renewable generation share: **42.0%**.
- exposure = `grid_intensity_ncg_adjusted` × Turkey→EU electricity exports
  (MWh). Same shape as steel's direct × tonnes.
- **`exported_mwh` is SOURCED but PROVISIONAL — see "Known open items" for
  the full quarantine (value, exact source URL, year, gross-not-net
  confirmation).** `electricity_exposure()` and `renewable_share_sweep()`
  still accept `exported_mwh` as an explicit parameter (default `None`, so
  other callers don't silently inherit a number); `main()` wires in the
  provisional 2,543,000 MWh figure. Current-state exposure computed:
  **~1,190,499 tCO2** (provisional). Persisted to
  `output/electricity_exposure_current.csv` and
  `output/electricity_renewable_sweep.csv`, both explicitly labeled
  PROVISIONAL in their own columns/filenames — do not cite as final without
  resolving the open item.
- **Renewable-share lever** (`intensity_under_renewable_share`,
  `renewable_share_sweep`): rescales generation to a target renewable share,
  holding total generation and each group's (renewable/non-renewable)
  internal fuel-mix proportions fixed. Geothermal keeps its real 0.887
  factor at every scenario point — **100% "renewable" share still computes
  ~0.067 tCO2/MWh, not 0**, because geothermal's share of the renewable mix
  scales up with it. This is the honest version of the paper's point: a
  bigger renewable buildout is not automatically a proportionally cleaner
  grid if geothermal is a growing part of that buildout. Do not describe a
  higher renewable share as driving intensity to zero.
- Sweep persisted to `output/electricity_renewable_sweep.csv` (columns:
  renewable_share, intensity, exposure — exposure now populated using the
  PROVISIONAL `exported_mwh`, see "Known open items"). This file is what
  Implications cites for the renewable-scenario chart; regenerate, don't
  hand-edit. Re-persist once `exported_mwh` is confirmed (not provisional).

## Remaining sequence
1. ~~Freeze steel clustering~~ DONE — see "Clustering (steel) — FROZEN" above.
2. Build electricity good — DONE, including `exported_mwh` (see
   "Electricity good" above and "Known open items" for its PROVISIONAL
   status). Grid intensity, Turkey-specific factors, two-basis structure,
   the renewable-share lever, and full exposure are built, wired, and
   tested. Model is functionally COMPLETE; `exported_mwh` confirmation is
   the one open item before treating outputs as final.
3. Write Implications section (weight-bearing prose; cites steel + electricity
   + ranking). Write this BEFORE visualizations — prose decides what's worth
   drawing.
4. Visualizations — driven by Implications: the sector cliff, the steel
   two-cluster structure, the electricity renewable-scenario curve.
5. Prose resequencing (funnel toward CBAM) + CBAM framing fix; repo hygiene
   (README, provenance manifest, one-script-regenerates-everything);
   compression + formatting pass.

## Architecture rules
- Pure functions returning DataFrames. Not OOP.
- Dataclasses for data holders only; no getters/setters (Java habits — resist).
- No CBAMCalculator / ScenarioRunner classes yet. A class earns its place only
  when it holds real state (e.g. scenario ETS-price paths). Build it then, not
  before. Do not create half-built abstractions to fill out structure.
- When something is broken, rewrite it — do not wrap or patch around it.

## Testing (required)
Every data-derived number gets an assertion:
- item 2 loads 65 HS4 headings; all codes length 4
- steel share of exposure > 0.6
- grid thermal share ≈ 57.8%
- turkey_grid_intensity in 0.4–0.5 tCO2/MWh
- steel feature table: ~42 rows pre-filter, no silently-zeroed N/A direct
  values, direct shows real spread (not collapsed to a constant), exposure
  non-null wherever there's trade, tonnes = 0 (not null) for no-trade headings
- clustering (exploratory, `clustering.py`): on cleaned 35, chosen k-means
  clustering is non-trivial (largest cluster not ~all headings), silhouette
  for chosen k reported and >= 0.3, every heading gets a label, DBSCAN runs
  without error
- clustering (frozen, `steelClusterFrozen.py`): drop list matches the
  canonical rule (7 dropped, exact hs4 set), k fixed at 3, silhouette within
  tolerance of 0.51 (regression guard), semantic labels match centroid
  ranking, labels reproducible across repeat runs, module never imports grid
  intensity, exposure shares sum to ~1.0
- electricity good (`electricityGood.py`): validation run (geothermal
  forced to 0) reproduces `EMBER_IEA_BENCHMARK` within ± 2%, the two-basis
  delta is positive and in the 3-10% range with "geothermal" in its
  provenance string, geothermal factor > 0 (never silently zeroed), every
  emission factor has a real source string, module never imports any steel
  module, `electricity_exposure()` returns `exposure=None` (not 0, not
  fabricated) when `exported_mwh` isn't supplied, renewable-share sweep
  bounds are sane (0% share > 100% share on intensity, 100% share still > 0
  because geothermal), current renewable share is a fraction in (0,1),
  `EXPORTED_MWH` equals the sum of its two named border components and cites
  an ENTSO-E source with reference year 2024, module source is flagged
  PROVISIONAL with both "gross" and "net" mentioned (guards against someone
  silently marking it locked), full exposure with the sourced value computes
  to `intensity × EXPORTED_MWH`
These tests are the audit trail — they prove the numbers, and fail loudly if an
input file changes.

## Emission factors (tCO2 per MWh electricity)
Natural gas / LNG / naphtha: 0.37 (IPCC/IEA generic; corroborated
Turkey-specific by Sözen et al.) · Lignite: **1.08, Turkey-specific**
(Sözen et al., not generic 1.10) · Hard/imported/asphaltite coal: 0.90
(IPCC/IEA generic) · Fuel oil: 0.65 (IPCC/IEA generic) · Wind/solar/hydro:
0 (operational direct convention) · Biomass: 0 (biogenic convention) ·
**Geothermal: 0.887, Turkey-specific, NOT zero** (Herrera Martinez et al.
2016 — Turkish reservoir CO2 degassing; vintage flag, see "Known open
items") · this is the NCG-adjusted basis; see "Electricity good" for the
separate EMBER_IEA_BENCHMARK (0.4425, geothermal-zero) it's checked against.
Imports (Uluslararası) and waste heat (Atık Isı): excluded from generation
total. Full source citations in `features/electricityGood.py`.

## Working style
- One bounded task at a time. Stop after each and show the result for review
  before continuing. Do not build the whole pipeline in one pass.
- Ask before installing dependencies or modifying the cleaned data files.
- Register for any prose/comments: analyst-facing, direct, no padding.