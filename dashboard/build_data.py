#!/usr/bin/env python3
"""Build the account-level dataset for the Forge ops dashboard.

Reads the raw Brightspeed (BASS) and Verizon/Frontier activity exports and
emits one compact, PII-free record per sold account:
  c  : company 'B' (Brightspeed) | 'V' (Verizon/Frontier)
  rep: salesperson (title case)
  zip: 5-digit zip or None (Verizon fiber rows carry no address)
  st : outcome 'I' installed | 'C' canceled | 'P' pending
  pp : 1 if pending AND past its due/scheduled-activation date
  ch : 1 if installed then disconnected (Verizon 'Inactive')
  wk : sale week (Monday, ISO date) from order create date
  iw : install week (Monday, ISO date) or None

Brightspeed "ABANDONED" rows have no order number / account — they are dead
leads, not sold accounts, and are excluded. Verizon rows are product lines;
they are rolled up to one record per customer_account_number anchored on the
fiber DATA line when one exists (status precedence Active > Inactive >
Pending > Canceled).
"""
import json
import pandas as pd

TODAY = pd.Timestamp("2026-07-15")


def monday(ts):
    if pd.isna(ts):
        return None
    return (ts - pd.Timedelta(days=ts.weekday())).strftime("%Y-%m-%d")


def zip5(v):
    if pd.isna(v):
        return None
    return str(int(v)).zfill(5)


accounts = []
zip_info = {}

# ---------------- Brightspeed ----------------
bs = pd.read_csv("brightspeed_orders.csv")
sold = bs[bs["Order #"].notna()].copy()
sold["create"] = pd.to_datetime(sold["Create Time"], errors="coerce")
sold["due"] = pd.to_datetime(sold["Order Due Date"], errors="coerce")
sold["chg"] = pd.to_datetime(sold["Status Change Date"], errors="coerce")

ST = {
    "Submitted - COMPLETED": "I",
    "CANCELLED": "C",
    "Submitted - PROVIDER IN PROCESS": "P",
    "CREATED": "P",
}

# collapse re-orders on the same account number (keep best outcome, latest sale)
prec = {"I": 0, "P": 1, "C": 2}
sold["st"] = sold["Order Status"].map(ST)
sold["acct_key"] = sold["Account Number"].astype("string").fillna(
    "ord:" + sold["Order #"].astype(str)
)
sold = sold.sort_values(["acct_key", "st", "create"], key=lambda s: s.map(prec) if s.name == "st" else s)
sold = sold.groupby("acct_key", as_index=False).first()

for _, r in sold.iterrows():
    st = r["st"]
    z = zip5(r["Zip Code"])
    if z:
        zip_info.setdefault(z, {"city": str(r["City"]).title(), "state": r["State"]})
    accounts.append({
        "c": "B",
        "rep": str(r["Sales Person Name"]).title(),
        "zip": z,
        "st": st,
        "pp": 1 if (st == "P" and pd.notna(r["due"]) and r["due"] < TODAY) else 0,
        "ch": 0,
        "wk": monday(r["create"]),
        "iw": monday(r["chg"]) if st == "I" else None,
    })

print("Brightspeed accounts:", sum(1 for a in accounts if a["c"] == "B"))

# ---------------- Verizon / Frontier ----------------
vz = pd.read_csv("verizon_orders.csv")
vz["od"] = pd.to_datetime(vz["order_date"], errors="coerce")
vz["sched"] = pd.to_datetime(vz["scheduled_activation_date"], errors="coerce")
vz["act"] = pd.to_datetime(vz["activation_date"], errors="coerce")
vz["is_data"] = vz["product_plan_category"].str.contains("DATA", na=False)

vprec = {"Active": 0, "Inactive": 1, "Pending": 2, "Canceled": 3}
VST = {"Active": "I", "Inactive": "I", "Pending": "P", "Canceled": "C"}

for acct, g in vz.groupby("customer_account_number"):
    anchor_rows = g[g["is_data"]] if g["is_data"].any() else g
    anchor_rows = anchor_rows.sort_values("order_status", key=lambda s: s.map(vprec))
    a = anchor_rows.iloc[0]
    st = VST[a["order_status"]]
    z = None
    zrows = g[g["customer_zip"].notna()]
    if len(zrows):
        zr = zrows.iloc[0]
        z = zip5(zr["customer_zip"])
        zip_info.setdefault(z, {"city": str(zr["customer_city"]).title(),
                                "state": "VA" if zr["customer_state"] == "VI" else zr["customer_state"]})
    accounts.append({
        "c": "V",
        "rep": str(a["agent_name"]).title(),
        "zip": z,
        "st": st,
        "pp": 1 if (st == "P" and pd.notna(a["sched"]) and a["sched"] < TODAY) else 0,
        "ch": 1 if a["order_status"] == "Inactive" else 0,
        "wk": monday(a["od"]),
        "iw": monday(a["act"]) if (st == "I" and pd.notna(a["act"])) else None,
    })

print("Verizon accounts:", sum(1 for a in accounts if a["c"] == "V"))

# fix VA typo in source ('VI')
for z, info in zip_info.items():
    if info["state"] == "VI":
        info["state"] = "VA"

with open("dash_accounts.json", "w") as f:
    json.dump({"today": TODAY.strftime("%Y-%m-%d"), "accounts": accounts,
               "zips": zip_info}, f)

# sanity summary
df = pd.DataFrame(accounts)
for c, g in df.groupby("c"):
    i = (g["st"] == "I").sum(); cc = (g["st"] == "C").sum(); p = (g["st"] == "P").sum()
    print(f"{c}: sold={len(g)} inst={i} canc={cc} pend={p} pastpend={g['pp'].sum()} "
          f"resolved_rate={i/(i+cc):.1%} gross_rate={i/len(g):.1%}")
i = (df["st"] == "I").sum(); cc = (df["st"] == "C").sum()
print(f"ALL: sold={len(df)} resolved_rate={i/(i+cc):.1%} gross_rate={i/len(df):.1%}")
print("weeks:", sorted(df["wk"].dropna().unique()))
