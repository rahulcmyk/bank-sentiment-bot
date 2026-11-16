"""Fix-priority engine: which complaint theme should a company fix first?

Ranking comes ONLY from review data:
  reach    = % of all reviews that mention the theme
  severity = (5 - average stars of those reviews) / 4   (0 = happy, 1 = all 1-star)
  impact   = reach x severity
  priority = impact x (3 / effort)   effort is 1-5, default 3 for every theme (edit with --effort)

Money is OPTIONAL and illustrative. It appears only if you pass --users, and it rests on
assumptions YOU supply (reviewers represent all users; unhappy users churn at --churn-uplift).

Example:
  python3 priority.py --csv reviews_hsbc_chase.csv --bank "HSBC Singapore" \
    --start 2026-01-01 --end 2026-11-13 \
    --extra "Developer options block=developer|usb debug|debugging" \
    --effort "Developer options block=2"
"""
import argparse, re, warnings
import numpy as np
import pandas as pd
from themes import THEMES

warnings.filterwarnings("ignore", category=UserWarning)

p = argparse.ArgumentParser()
p.add_argument("--csv", required=True)
p.add_argument("--bank", required=True)
p.add_argument("--start", required=True)
p.add_argument("--end", required=True)
p.add_argument("--extra", action="append", default=[], help="'Theme=regex'")
p.add_argument("--effort", action="append", default=[], help="'Theme=1..5' (1 easy, 5 hard)")
p.add_argument("--min-reviews", type=int, default=5)
p.add_argument("--users", type=float, default=None, help="active users (optional)")
p.add_argument("--revenue-per-user", type=float, default=None, help="yearly revenue per user")
p.add_argument("--churn-uplift", type=float, default=0.10, help="extra churn if affected (0.10 = 10%%)")
a = p.parse_args()

df = pd.read_csv(a.csv, parse_dates=["date"])
df["text"] = df["text"].fillna("").astype(str)
df = df[(df.bank == a.bank) & (df.date >= a.start) & (df.date <= a.end)].copy()
if df.empty:
    raise SystemExit("No reviews for that bank and window. Check the bank name and dates.")

themes = {k: list(v) for k, v in THEMES.items()}
for e in a.extra:
    k, rx = e.split("=", 1)
    themes[k.strip()] = [rx.strip()]
effort = {k: 3.0 for k in themes}
for e in a.effort:
    k, v = e.split("=", 1)
    if k.strip() not in effort:
        raise SystemExit(f"Unknown theme in --effort: {k}")
    effort[k.strip()] = float(v)

low = df.text.str.lower()
for t, pats in themes.items():
    df[t] = low.str.contains("|".join(pats), regex=True)

end = pd.Timestamp(a.end)
recent_cut = end - pd.Timedelta(days=60)
neg = df[df.rating <= 2]
neg_recent, neg_before = neg[neg.date > recent_cut], neg[neg.date <= recent_cut]

rows = []
for t in themes:
    m = df[t]
    n = int(m.sum())
    if n < a.min_reviews:
        continue
    reach = n / len(df) * 100
    stars = df.loc[m, "rating"].mean()
    severity = (5 - stars) / 4
    impact = reach * severity
    trend = np.nan
    if len(neg_recent) >= 15 and len(neg_before) >= 15:
        trend = (neg_recent[t].mean() - neg_before[t].mean()) * 100
    rows.append({"theme": t, "reviews": n, "reach_pct": reach, "avg_stars": stars,
                 "severity": severity, "impact": impact, "effort": effort[t],
                 "priority": impact * 3 / effort[t], "trend_pts_last60d": trend})
out = pd.DataFrame(rows).sort_values("priority", ascending=False).reset_index(drop=True)
out.insert(0, "rank", out.index + 1)

if a.users and a.revenue_per_user:
    out["users_affected"] = (a.users * out.reach_pct / 100).round(0)
    out["money_at_risk_per_year"] = (out.users_affected * a.churn_uplift * a.revenue_per_user).round(0)

slug = re.sub(r"[^a-z0-9]+", "_", a.bank.lower()).strip("_")
path = f"priority_{slug}.csv"
out.round(2).to_csv(path, index=False)

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 20)
print(f"{a.bank}: {len(df)} reviews, {a.start} to {a.end}\n")
print(out.round(2).to_string(index=False))
if "money_at_risk_per_year" in out:
    print(f"\nMONEY IS ILLUSTRATIVE: users={a.users:,.0f}, revenue/user={a.revenue_per_user}, "
          f"extra churn if affected={a.churn_uplift:.0%}. Reviewers are not all users; treat as a rough scale only.")
else:
    print("\nNo money columns: pass --users and --revenue-per-user to add an illustrative estimate.")
print(f"\nSaved {path}")
