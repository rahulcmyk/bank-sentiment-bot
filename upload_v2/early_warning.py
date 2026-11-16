"""Early warning: finds weeks when a bank's share of 1-2 star reviews jumps above its recent normal.

Rule (kept simple on purpose):
  - baseline = the previous 4 weeks of the same bank
  - alert when this week's negative share is at least MIN_JUMP points higher than baseline
    AND the jump is statistically strong (z-score >= MIN_Z)
  - weeks with too few reviews are skipped, because small samples jump around by luck
For each alert, it names the complaint theme that grew the most.
"""
import numpy as np
import pandas as pd

MIN_WEEK_REVIEWS = 25    # skip weeks with fewer reviews than this
MIN_BASE_REVIEWS = 60    # need at least this many reviews in the 4-week baseline
MIN_JUMP = 8.0           # percentage points
MIN_Z = 3.0              # strength of the jump

df = pd.read_csv("bank_reviews_themed.csv", parse_dates=["date"])
themes = [c for c in df.columns if df[c].dtype == bool]
df["week"] = df["date"].dt.to_period("W").dt.start_time
df["neg"] = (df["rating"] <= 2).astype(float)
for t in themes:
    df["c_" + t] = df[t].astype(float) * df["neg"]    # complaint about this theme

def z_score(p_week, n_week, p_base):
    se = np.sqrt(max(p_base * (1 - p_base), 1e-9) / n_week)
    return (p_week - p_base) / se

alerts = []
weekly_rows = []
for bank, g in df.groupby("bank"):
    weeks = sorted(g["week"].unique())
    for i, w in enumerate(weeks):
        cur = g[g["week"] == w]
        base = g[g["week"].isin(weeks[max(0, i - 4):i])]
        n, nb = len(cur), len(base)
        p, pb = cur["neg"].mean(), (base["neg"].mean() if nb else np.nan)
        weekly_rows.append({"bank": bank, "week": w.date(), "reviews": n, "negative_pct": round(p * 100, 1)})
        if n < MIN_WEEK_REVIEWS or nb < MIN_BASE_REVIEWS:
            continue
        jump = (p - pb) * 100
        z = z_score(p, n, pb)
        if jump >= MIN_JUMP and z >= MIN_Z:
            changes = {t: (cur["c_" + t].mean() - base["c_" + t].mean()) * 100 for t in themes}
            top = sorted(changes.items(), key=lambda x: -x[1])[:2]
            alerts.append({
                "bank": bank,
                "week_starting": w.date(),
                "reviews_that_week": n,
                "negative_before_pct": round(pb * 100, 1),
                "negative_now_pct": round(p * 100, 1),
                "jump_points": round(jump, 1),
                "z_score": round(z, 1),
                "main_driver": f"{top[0][0]} (+{top[0][1]:.1f})",
                "second_driver": f"{top[1][0]} (+{top[1][1]:.1f})",
            })

out = pd.DataFrame(alerts)
out.to_csv("early_warning_alerts.csv", index=False)
pd.DataFrame(weekly_rows).to_csv("weekly_negative_share.csv", index=False)

print(f"Rule: jump >= {MIN_JUMP} points and z >= {MIN_Z}, weeks with >= {MIN_WEEK_REVIEWS} reviews, 4-week baseline.\n")
if out.empty:
    print("No alerts.")
else:
    print(out.to_string(index=False))
