# Forge Field Ops Dashboard

A single-file, self-contained HTML dashboard (`forge_ops_dashboard.html`) for
tracking install rate, pay tiers, weekly trends, rep outliers, and a zoomable
market heat map across Verizon/Frontier and Brightspeed.

Open `forge_ops_dashboard.html` in any browser — no server or network needed.

## Refreshing with new exports

1. Convert the raw partner exports to CSV (needs `pandas`, `lxml`,
   `numbers-parser`):

   ```
   python3 extract_inputs.py Orders.xls Verizon_Sales_Activity_Report.numbers
   ```

2. Build the account-level dataset (update `ASOF` and `BS_START` in
   `build_data.py` for the new exports — they drive the past-pending cutoff):

   ```
   python3 build_data.py          # -> dash_accounts.json
   ```

3. Rebuild geo assets only if new zip codes appear (needs
   `npm i d3-geo topojson-client us-atlas`; add the new zip centroids to the
   table in the script):

   ```
   node build_geo.mjs             # -> geo_states.json, geo_zips.json
   ```

4. Assemble:

   ```
   python3 assemble.py            # -> forge_ops_dashboard.html
   ```

## Definitions baked into the dashboard

- **Sold account** — Brightspeed rows with an order number (ABANDONED rows are
  dead leads and excluded); Verizon rows rolled up to one record per account
  number, anchored on the fiber DATA line. Verizon and Frontier are one company.
- **Install rate (had-a-chance, default)** — installed ÷ (installed +
  canceled + pendings already past their install date); orders not yet due
  don't count either way. Toggles for resolved (÷ installed + canceled) and
  all-sold bases.
- **As-of dates** — the exports aren't pulled live; "past" is judged against
  each report's own as-of date (`ASOF` in `build_data.py`), inferred from the
  latest activity in the file.
- **Reporting window** — June 1 onward; Brightspeed intentionally limited to
  orders created July 1 onward (`BS_START`).
- **Past-pending** — still pending and past its order due date (Brightspeed) or
  scheduled activation date (Verizon).
- **Pay tiers** — <70% → $10, 70–75% → $15, ≥75% → $20 per installed account.

Raw exports and intermediate CSVs contain customer PII (names, addresses,
phone numbers) — do **not** commit them. The built dashboard embeds only
rep-level and zip-level aggregates.
