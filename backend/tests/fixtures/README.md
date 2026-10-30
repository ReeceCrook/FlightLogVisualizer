# FlightLogVisualizer test fixtures

All files are fake. Names, tails, and flights are invented. Every airport code
was checked against the OurAirports `airports.csv` snapshot of 2026-10-28.

Hours below are what a correct parser should produce. Use them as test assertions.

## netjets_quirks.csv: small, every known trap
Same layout as the real NetJets crew-times export: CRLF line endings, quoted
strings, unquoted numbers, a 20-field totals footer under a 21-field header.

| Expectation | Value |
|---|---|
| Flight rows (footer excluded) | 20 |
| Block hours | 36.3 (footer also says 36.3) |
| PIC / Night / IFR hours | 23.8 / 8.5 / 5.40 |
| Simulator rows | 1 (`XSIM`, tail `SIM_XL1`, TOL to TOL) |
| Legs with literal `null` airport | 2 (NEW to null, null to CMH) |
| Origin = destination | 2 (1 sim, 1 real local flight at APA) |
| Crew names | 0 (`Paired With` empty on every row) |

Airport traps inside:
- `CMH` and `KCMH`-style mixing: 3-letter codes until 2014, 4-letter after.
- `07FA` (Ocean Reef Club, FL): local identifier whose IATA code is `OCA`.
- `N66`: FAA local identifier; OurAirports ident is `KN66`.
- `SDL`: Scottsdale to a US pilot, but IATA `SDL` is Sundsvall, Sweden.
- `BLM`: Monmouth Executive (KBLM), but an exact `ident` match hits a Mexican airstrip.
- `KPFN`: closed airport (old Panama City). Only found via the `keywords` column.
- `6S5`: retired code for Ravalli County (now `K6S5` / `HRF`); only in `keywords`.
- `2016-01-01 02:10 Z`: still Dec 31 in US local time (year-boundary test).
- `IFR Hrs` 1.25 (hundredths) while everything else is tenths.

## netjets_large.csv: synthetic 17-year career (performance and globe)
| Expectation | Value |
|---|---|
| Flight rows | 3,446 (Mar 2008 to Oct 2025) |
| Block hours | 9,766.3 (footer matches) |
| PIC / Night / IFR hours | 6,320.7 / 2,109.8 / 669.60 |
| Simulator rows | 4 |
| Distinct tails | 243 |
| Distinct crew names | 18 (`Paired With` IS filled here, format "First Last", a guess) |

3-letter codes before 2012, 4-letter after 2014, mixed in between. Includes
`HXD` (Hilton Head to a US pilot, Delingha, China by IATA) and international legs
to Canada, Mexico, the Caribbean, and Europe.

## foreflight_ga.csv: GA pilot, student to instrument rating (Colorado)
Layout is approximated from ForeFlight's published field list. Verify against a
real export when you can.

- Preamble row, blank row, `Aircraft Table` section (type row + header + 4 aircraft),
  blank row, `Flights Table` section (type row + header + flights). All rows padded
  to 61 columns.

| Expectation | Value |
|---|---|
| Flight rows | 205 (2021-05-01 to 2025-09-19) |
| TotalTime sum | 383.2 h |
| PIC sum | 326.9 h (25 PIC cells are `H:MM`, rest decimal) |
| Simulator rows | 4 (`BATD-1`, TotalTime 0, SimulatedFlight sum 5.9) |
| Catch-up entry | 1 (12.4 h, no airports) |
| Rows using `Route` | 80 (From = To = KBJC, stops in Route) |

Traps: From = To with a Route is a cross-country, not a local flight. `TimeOut` is
`HHMM` with leading zeros (`0830`); Excel strips them. Local codes `1V6`, `18V`.
Crew in `Person1` as `Name;Role;Email`. Approaches packed as `count;type;rwy;apt;;`.
A comment contains embedded double quotes.

## myflightbook_cfi.csv: flight instructor (Florida + Bahamas)
| Expectation | Value |
|---|---|
| Rows | 575 (1/4/2023 to 10/14/2025) |
| Total Flight Time | 1,233.8 h (35 cells in `H:MM`) |
| Simulator rows | 27 (`SIM-RB1`, total 0) |
| Anonymous-aircraft rows | 130 (tail `#100234`) |
| Bahamas trips | 45 (`MYNN`, `MYEH`, `MYAM`) |

Traps: UTF-8 BOM + CRLF. Dates `M/d/yyyy` (no leading zeros). Only a `Route`
column, no From/To. Lowercase and padded codes (`korl `, ` kism`) and double spaces.
A comment contains a newline inside quotes. Local codes `X04`, `X05`. Some
`Landings` cells blank while `FS Day Landings` is set.

## logten_airline.tsv: long-haul airline pilot, F/O then Captain
Column names are a best guess. LogTen's real export may differ.

| Expectation | Value |
|---|---|
| Rows | 540 (02/03/2019 to 05/10/2025, `dd/MM/yyyy`) |
| Total Time | 5,478.33 h (all `H:MM`) |
| PIC / SIC | 2,330.75 / 3,147.58 h (Captain from 2023) |
| Positioning (deadhead) legs | 17 (Total Time `0:00`) |
| Antimeridian crossings | 32 (SYD/NRT/HKG to or from LAX/SFO/ANC) |
| Legs where In < Out (overnight) | 244 |

Traps: tab-separated. `dd/MM/yyyy` is ambiguous with US dates for days 1 to 12.
IATA codes only. Crew columns use `SELF` for the logbook owner.

## generic_german_messy.csv: column-mapping screen stress test
Semicolon-delimited, Windows-1252 encoded, German headers
(`Datum;Von;Nach;Kennzeichen;Muster;Blockzeit;PIC;Copilot;Bemerkung`).

| Expectation | Value |
|---|---|
| Rows | 16 (15 non-blank) |
| Blockzeit sum, raw | 20.4 h |

Traps: decimal comma (`1,2`), `DD.MM.YYYY` dates, umlauts and accents in names,
a semicolon inside a quoted field, ` eddf ` and `edfe` (case and spaces), one
exact duplicate row, one blank row, one zero-time row, one negative time (-0.4),
and `ZZZZ` (the flight-plan placeholder for "no ICAO code").
Decide how the app treats the duplicate, zero, and negative rows, then write the
expected total into your tests.

## invalid_*.csv: inputs that must fail cleanly
- `invalid_empty.csv`: 0 bytes.
- `invalid_headers_only.csv`: NetJets header, no data.
- `invalid_not_a_logbook.csv`: a bakery inventory.
Each should produce a clear user-facing error, never a 500.
