#!/usr/bin/env python3
"""Inject the data payloads into the dashboard template.

Inputs (same directory): dashboard_template.html, dash_accounts.json,
geo_states.json, geo_zips.json. Output: forge_ops_dashboard.html.
"""
tpl = open("dashboard_template.html").read()
out = (tpl.replace("__DATA__", open("dash_accounts.json").read())
          .replace("__STATES__", open("geo_states.json").read())
          .replace("__ZIPXY__", open("geo_zips.json").read()))
open("forge_ops_dashboard.html", "w").write(out)
print("wrote forge_ops_dashboard.html", len(out), "bytes")
