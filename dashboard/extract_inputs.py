#!/usr/bin/env python3
"""Convert the raw partner exports into the CSVs build_data.py expects.

Usage: python3 extract_inputs.py <brightspeed_orders.xls> <verizon_report.numbers>

The Brightspeed "xls" is actually an HTML table export; the Verizon report is
an Apple Numbers file. Requires: pandas, lxml, numbers-parser.
"""
import csv
import sys

import pandas as pd
from numbers_parser import Document

bs_path, vz_path = sys.argv[1], sys.argv[2]

tables = pd.read_html(bs_path, header=0)
tables[0].to_csv("brightspeed_orders.csv", index=False)
print("brightspeed_orders.csv:", tables[0].shape)

doc = Document(vz_path)
rows = doc.sheets[0].tables[0].rows(values_only=True)
with open("verizon_orders.csv", "w", newline="") as f:
    w = csv.writer(f)
    for r in rows:
        w.writerow(["" if v is None else v for v in r])
print("verizon_orders.csv:", len(rows), "rows")
