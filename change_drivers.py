import pandas as pd

df = pd.read_csv("bank_reviews_themed.csv")
cols = [c for c in df.columns if df[c].dtype == bool]
neg = (df["rating"] <= 2).astype(float)
comp = df[cols].astype(float).mul(neg, axis=0) * 100
comp["bank"] = df["bank"]
comp["month"] = df["month"]
comp["neg"] = neg * 100

cases = [
    ("Revolut", "2026-10", ["2026-06", "2026-07", "2026-08", "2026-09"]),
    ("DBS digibank", "2026-08", ["2026-06", "2026-07"]),
    ("Liv X", "2026-10", ["2026-09"]),
]
for bank, m, base in cases:
    g = comp[comp["bank"] == bank]
    now = g[g["month"] == m][cols + ["neg"]].mean()
    before = g[g["month"].isin(base)][cols + ["neg"]].mean()
    t = pd.DataFrame({"before": before, "now": now})
    t["change"] = t["now"] - t["before"]
    print(f"\n{bank}: {m} compared with {', '.join(base)}")
    print(f"All 1-2 star reviews: {t.loc['neg','before']:.1f}% -> {t.loc['neg','now']:.1f}%")
    print(t.drop("neg").sort_values("change", ascending=False).round(1).head(5))
