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

2. Build the account-level dataset (edit `TODAY` in `build_data.py` to the
   report date — it drives the past-pending cutoff):

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
- **Install rate (resolved)** — installed ÷ (installed + canceled). The
  "all sold" toggle divides by every sold account instead.
- **Past-pending** — still pending and past its order due date (Brightspeed) or
  scheduled activation date (Verizon).
- **Pay tiers** — <70% → $10, 70–75% → $15, ≥75% → $20 per installed account.

Raw exports and intermediate CSVs contain customer PII (names, addresses,
phone numbers) — do **not** commit them. The built dashboard embeds only
rep-level and zip-level aggregates.
