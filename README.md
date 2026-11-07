# turkey-cbam-exposure

A clustering-based model of Türkiye's exposure to the EU Carbon Border
Adjustment Mechanism (CBAM). Its output is cited in the Implications section
of "Paper Capacity: Why Türkiye's Renewable Buildout Is Not Delivering Clean
Generation" — an analyst note for a banking application, supervised as part
of a research project at the University of Bristol.

## What question this model answers

CBAM is binding as of the definitive period (January 2026) on a
deferred-settlement basis: carbon cost accrues on imports now, with the first
certificate surrender due September 2027, phasing in to full liability by
2034. This model asks one question only: **what is Türkiye's
carbon-cost-at-the-border exposure, by CBAM good, for Türkiye→EU trade?** It
does not model financing, WACC, or LNG substitution — those belong to the
paper's other sections, not this model.

Two of the six CBAM goods carry the analytical weight:

- **Steel (direct emissions)** — exposure is grid-independent. It is a
  function of coking/blast-furnace process chemistry and trade volume, not of
  Türkiye's electricity mix.
- **Electricity (indirect/grid emissions)** — exposure is pure grid carbon
  intensity, so it is the one good that moves with renewable generation. This
  is where the model connects to the paper's "Generation Gap" argument: a
  larger renewable buildout does not mechanically translate into a
  proportionally lower CBAM bill (see "Modelling decisions" below).

## Quickstart

```bash
# 1. Install (pinned dependencies from pyproject.toml)
pip install -e ".[dev]"

# 2. Raw data: already committed? check with:
python scripts/fetch_data.py
# If files are missing, it prints exactly which ones and where to get them
# (see data/README.md for full source URLs, licences, retrieval notes).

# 3. Run the full pipeline — rebuilds every output/ CSV and exhibit figure
python -m cbam_exposure run

# 4. Run the test suite
pytest tests/ -v
```

Note on CI: the three raw data files (`item1.xlsx`, `item2.csv`, `item3.csv`)
are gitignored (large/restricted — see `data/README.md`), so GitHub Actions
cannot check them out. `tests/test_locked_outputs.py` reads only the
already-committed `output/*.csv` files and runs unconditionally in CI; the 33
other tests need the raw files and skip cleanly there (`pytest -v` will show
them as `SKIPPED`, not failed) while running fully in local dev.

## Results

| Output | Value | Status |
|---|---|---|
| Sector exposure ranking: steel | 68.97% (~69%) | locked |
| Sector exposure ranking: cement | 21.62% | locked |
| Sector exposure ranking: aluminium | 7.00% | locked |
| Sector exposure ranking: fertilisers | 2.11% | locked |
| Sector exposure ranking: hydrogen | 0.30% | locked |
| Steel + cement, share of total exposure | ~90.6% | locked |
| Steel k-means | k=3, silhouette ≈ 0.51, n=35 cleaned HS4 headings | locked |
| Steel cluster: commodity-volume | ~82% of steel book, mean direct ≈ 2.63 tCO₂/t | locked |
| Steel cluster: specialty-intensity | ~15%, mean direct ≈ 5.99 tCO₂/t | locked |
| Steel cluster: moderate-middle | ~3% | locked |
| Grid intensity — EMBER/IEA basis (geothermal = 0) | 0.4425 tCO₂/MWh | locked, external benchmark |
| Grid intensity — NCG-adjusted basis (geothermal = 0.887) | 0.4681 tCO₂/MWh | locked, operative figure |
| Geothermal NCG delta | +5.8% | locked finding |
| Exported electricity, Türkiye→EU gross (TR→GR + TR→BG) | ≈ 2.54M MWh | **PROVISIONAL** — pending ENTSO-E API confirmation, see `docs/open_issues.md` |
| Electricity CBAM exposure, current state | ≈ 1.2 MtCO₂ | **PROVISIONAL** — inherits the exported-MWh uncertainty above |

Every number here is asserted in `tests/test_locked_outputs.py` with a
documented tolerance; re-run `python -m cbam_exposure run` and `pytest` after
any data or code change to confirm nothing moved.

## Modelling decisions

**(a) Steel's exposure is grid-independent; the renewable link runs only
through electricity.** Steel is CBAM's direct-emissions good — exposure
comes from coking, blast-furnace reduction, and process chemistry, priced at
a fixed per-tonne direct-emissions intensity. It does not move when Türkiye's
renewable generation share moves. The only good in this model whose exposure
is a function of the grid mix is electricity (indirect/grid emissions by
construction). Any claim that a renewable buildout reduces steel's CBAM
exposure is unsupported by this model and is the specific failure mode this
repo is built to avoid.

**(b) Direct emissions only — no indirect, no grid-adjustment factor, for
every good except electricity.** The EU's CBAM default-values file reports
indirect emissions as N/A for steel and aluminium at HS4 granularity, so
there is no official per-product electricity-intensity figure to back an
indirect-emissions exposure calculation with. Rather than estimate or
back-fill that gap, the model computes exposure as `direct × tonnes`
everywhere except electricity, keeping every input to the sector-ranking and
steel-clustering outputs traceable to an official EU/Eurostat source. (An
earlier design — computing a Türkiye-adjusted indirect-emissions gap — was
considered and retired for exactly this reason: N/A is not 0, and there was
nothing to back a per-heading electricity-intensity figure out of.)

**(c) Two grid-intensity bases, not one number, and why they differ.**
Standard grid-carbon accounting (the Ember/IEA convention) treats geothermal
generation as carbon-neutral — fine globally, where geothermal's share of
generation is small, but wrong for Türkiye specifically: Turkish geothermal
reservoirs (Kızıldere, Germencik, etc.) release substantial reservoir CO₂
through non-condensable-gas (NCG) venting during generation (0.887 tCO₂/MWh,
Herrera Martinez et al. 2016 — a Turkey-specific empirical factor, not a
generic default). This model reports both bases deliberately: `0.4425`
(EMBER_IEA_BENCHMARK, geothermal-zero, kept as a citable external reference)
and `0.4681` (the NCG-adjusted basis, operative for the electricity-good
exposure and the renewable-share sweep). The +5.8% gap between them is
validated as attributable entirely to the geothermal treatment — forcing
geothermal to zero in this model's own build reproduces the Ember/IEA
benchmark within −0.6%, confirming the rest of the mix/methodology is sound.
One consequence worth flagging explicitly: in the renewable-share sweep, a
hypothetical 100%-renewable generation mix still computes to ≈0.067 tCO₂/MWh,
not zero — because geothermal's own share of the renewable mix scales up
with it, and geothermal is not carbon-free in Türkiye's grid.

## Limitations and open items

See `docs/open_issues.md` for GitHub-issue-ready write-ups. In short:

- **Exported electricity volume (`EXPORTED_MWH`) is provisional.** The
  2.54M MWh figure was read manually off a published ENTSO-E factsheet map
  (directional arrows, not a structured data table) and needs confirmation
  via the ENTSO-E Transparency Platform API. The electricity exposure figure
  (≈1.2 MtCO₂) inherits this uncertainty and is a lower bound, not a final
  number.
- **HS4 2601** (agglomerated iron ores) carries an unresolved discrepancy
  between this model's aggregated intensity (0.18) and the officially
  published EU default for the more specific CN 2601 12 00 (0.31); the
  Comext flow-direction (is Türkiye genuinely the exporter of record, or a
  re-export/reporting artifact?) is also unconfirmed. Footnote-tier, not
  blocking.
- **Geothermal NCG factor vintage.** 0.887 tCO₂/MWh is a 2015, 12-plant
  weighted average (Herrera Martinez et al. 2016); Türkiye's geothermal fleet
  has grown materially since, and the literature notes the factor evolves
  over a well's lifetime. Treat as a sensitivity, not a fixed constant.
- **A newer EU default-values regulation may supersede this model's steel/
  cement/aluminium/fertiliser inputs.** `item1.xlsx` (v1, dated 2026-02-04)
  is built from Commission Implementing Regulation (EU) 2025/2621. On
  2026-07-30/31 the Commission published (EU) 2026/1740, replacing Annex I
  and Annex IV of that regulation with corrected default values. Not acted
  on here — flagged in `docs/open_issues.md`.
- **Cement's figure is the least Türkiye-specific of the five sectors.**
  7 of cement's 8 CN codes use the generic EU default direct-emissions value
  (the Türkiye sheet showed no value for those codes); only CN 25233000
  (Aluminous cement) is Türkiye-specific.
- **No per-sector clustering beyond steel.** Cement (8 CN headings) and
  hydrogen (1) have too few headings to support clustering — ranking only.
  Aluminium (~24) and fertilisers (~27) were not clustered in this version;
  CLAUDE.md allows it as a diagnostic only if silhouette clears ~0.3.

## Repo layout

```
cleanUp/        raw -> cleaned parsers (item1 = EU default values, item2 = Comext trade)
features/       the model itself — steel features, exploratory + frozen clustering,
                grid intensity, electricity good, cross-sector exposure table
viz/            matplotlib exhibits, read-only on output/ CSVs
cbam_exposure/  CLI wrapper — `python -m cbam_exposure run` sequences the above
tests/          pytest suite, incl. tests/test_locked_outputs.py (CI-safe regression pins)
data/           raw inputs (gitignored, see data/README.md) + small processed CSVs
output/         every generated CSV and exhibit figure (committed — small files)
scripts/        fetch_data.py — checks for raw files, prints retrieval instructions
docs/           open_issues.md — issue-ready write-ups of unresolved items
.github/        CI workflow (pytest on every push/PR)
CLAUDE.md       the full model specification — locked decisions, guardrails, test spec
```

`CLAUDE.md` is the authoritative spec for every modelling decision, locked
number, and guardrail in this repo — this README summarizes it for a reader
coming in cold; `CLAUDE.md` is the source of truth if the two ever disagree.
