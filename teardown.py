"""One-command teardown: numbers for a company report from a reviews csv.

Example:
  python3 teardown.py --csv reviews_hsbc_chase.csv --name hsbc \
    --start 2026-01-01 --end 2026-11-13 \
    --extra "Developer options block=developer|usb debug|debugging"

Needs columns: bank, date, rating, text. Stars are the sentiment label.
Writes teardown_<name>/ with summary, themes, monthly, samples.
"""
import argparse, os, warnings
import numpy as np
import pandas as pd
from themes import THEMES

warnings.filterwarnings("ignore", category=UserWarning)

p = argparse.ArgumentParser()
p.add_argument("--csv", required=True)
p.add_argument("--name", required=True)
p.add_argument("--start", required=True)
p.add_argument("--end", required=True)
p.add_argument("--banks", default="", help="comma list to keep (default all)")
p.add_argument("--extra", action="append", default=[], help="'Theme=regex'")
p.add_argument("--min-chars", type=int, default=20)
a = p.parse_args()

df = pd.read_csv(a.csv, parse_dates=["date"])
df["text"] = df["text"].fillna("").astype(str)
df = df[(df.date >= a.start) & (df.date <= a.end)].copy()
if a.banks:
    df = df[df.bank.isin([b.strip() for b in a.banks.split(",")])]

themes = {k: list(v) for k, v in THEMES.items()}
for e in a.extra:
    k, rx = e.split("=", 1)
    themes[k.strip()] = [rx.strip()]
low = df.text.str.lower()
for t, pats in themes.items():
    df[t] = low.str.contains("|".join(pats), regex=True)
cols = list(themes)

def moe(s):
    return 1.96 * s.std() / np.sqrt(len(s)) if len(s) > 1 else np.nan

def block(d):
    g = d.groupby("bank")
    out = pd.DataFrame({
        "reviews": g.size(),
        "avg_stars": g.rating.mean(),
        "pct_1_2": g.rating.apply(lambda s: (s <= 2).mean() * 100),
        "pct_4_5": g.rating.apply(lambda s: (s >= 4).mean() * 100),
        "margin_of_error": g.rating.apply(moe),
    })
    out["net_sentiment"] = out.pct_4_5 - out.pct_1_2
    return out.round(2)

summary = block(df)
long_ = df[df.text.str.len() >= a.min_chars]
robust = block(long_)[["reviews", "avg_stars", "net_sentiment"]]
robust.columns = [f"{c}_{a.min_chars}plus_chars" for c in robust.columns]
summary = summary.join(robust)
summary["median_chars"] = df.groupby("bank").text.apply(lambda s: s.str.len().median())

neg, pos = df[df.rating <= 2], df[df.rating >= 4]
comp = (neg.groupby("bank")[cols].mean() * 100).round(1).T
praise = (pos.groupby("bank")[cols].mean() * 100).round(1).T
comp.loc["(any theme matched)"] = (neg[cols].any(axis=1).groupby(neg.bank).mean() * 100).round(1)
comp.loc["(1-2 star reviews)"] = neg.groupby("bank").size()
praise.loc["(4-5 star reviews)"] = pos.groupby("bank").size()

df["month"] = df.date.dt.to_period("M")
m = df.groupby(["bank", "month"]).rating.agg(
    reviews="size", avg_stars="mean", margin_of_error=moe).round(2).reset_index()
s, e_ = pd.Timestamp(a.start), pd.Timestamp(a.end)
m["partial_month"] = m.month.apply(
    lambda x: x.start_time < s or x.end_time.normalize() > e_)

rng = np.random.default_rng(1)
lines = []
for b, g in neg.groupby("bank"):
    lines.append(f"== {b}: random 1-2 star reviews ==")
    for _, r in g.sample(min(8, len(g)), random_state=1).sort_values("date").iterrows():
        lines.append(f"{r.date.date()} {r.rating}* | " + r.text[:220].replace("\n", " "))
    lines.append("")

out = f"teardown_{a.name}"
os.makedirs(out, exist_ok=True)
summary.to_csv(f"{out}/summary.csv")
comp.to_csv(f"{out}/themes_complaints.csv")
praise.to_csv(f"{out}/themes_praise.csv")
m.to_csv(f"{out}/monthly.csv", index=False)
open(f"{out}/samples.txt", "w").write("\n".join(lines))

pd.set_option("display.width", 200)
print(f"Window {a.start} to {a.end}\n")
print(summary.T, "\n")
print("COMPLAINT themes (% of 1-2 star reviews)\n", comp, "\n")
print("PRAISE themes (% of 4-5 star reviews)\n", praise, "\n")
print(f"Saved to {out}/")
