"""Marketing message tester: do an app's promises match what customers say?

For each promise (fast, easy, secure, reliable, rewards and low cost, support):
  claimed      = does the app's own Google Play text make this promise? (needs --descriptions)
  kept_mentions   = reviews that praise it in customers' words
  broken_mentions = reviews that say it failed
  kept_share   = kept / (kept + broken)

Example:
  python3 claims_check.py --csv reviews_hsbc_chase.csv --name hsbc \
    --start 2026-01-01 --end 2026-11-13 --descriptions descriptions.csv

Reads: reviews csv (bank, date, rating, text). Optional descriptions csv from fetch_claims.py.
Writes: claims_<name>.csv. Keyword rules are rough: use it to find gaps, then read the reviews.
"""
import argparse
import re
import warnings
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

# promise: (words in marketing text, words customers use when it is kept, when it is broken)
CLAIMS = {
    "Fast": (r"fast|quick|instant|in seconds|real.?time",
             r"fast|quick|instant|smooth|speedy",
             r"slow|laggy|\blag\b|delay|takes (forever|ages|long)|hang|freez|loading"),
    "Easy": (r"easy|simple|effortless|seamless|intuitive|user.?friendly|convenien",
             r"easy|simple|intuitive|user.?friendly|convenient|straightforward",
             r"difficult|confusing|complicated|hard to|not user.?friendly|cumbersome|unintuitive"),
    "Secure": (r"secure|safe|protect|security|biometric|fraud",
               r"secure|safe|trust|protected",
               r"scam|fraud|hack|unauthori|locked out|security (issue|risk|restrict)|blocked"),
    "Reliable": (r"24/7|always|anytime|anywhere|reliable|available",
                 r"reliable|works (well|fine|perfect|great)|never (fails|crash)|no issues",
                 r"crash|not working|doesn.?t work|outage|\berror|\bbug|stuck|keeps failing"),
    "Rewards and low cost": (r"cashback|reward|interest|earn|bonus|no fee|free|zero fee|low fee|save",
                             r"cashback|reward|great rate|good rate|no fees?|free|worth it",
                             r"hidden fee|charged|expensive|rate (cut|drop|fell)|removed|overpriced|\bfees?\b"),
    "Support": (r"support|help|chat|assistance|24/7 service",
                r"helpful|great support|good support|quick response|good service|great service",
                r"no support|no response|no reply|unhelpful|can.?t reach|useless (support|service)|chatbot|\bbot\b"),
}

p = argparse.ArgumentParser()
p.add_argument("--csv", required=True)
p.add_argument("--name", required=True)
p.add_argument("--start", required=True)
p.add_argument("--end", required=True)
p.add_argument("--descriptions", default="")
a = p.parse_args()

df = pd.read_csv(a.csv, parse_dates=["date"])
df["text"] = df["text"].fillna("").astype(str).str.lower()
df = df[(df.date >= a.start) & (df.date <= a.end)]

marketing = {}
if a.descriptions:
    d = pd.read_csv(a.descriptions).fillna("")
    for _, r in d.iterrows():
        marketing[r["bank"]] = (r["title"] + " " + r["summary"] + " " + r["description"]).lower()

rows = []
for bank, g in df.groupby("bank"):
    for claim, (m_rx, kept_rx, broken_rx) in CLAIMS.items():
        kept = int((g.text.str.contains(kept_rx, regex=True) & (g.rating >= 4)).sum())
        broken = int((g.text.str.contains(broken_rx, regex=True) & (g.rating <= 2)).sum())
        claimed = (bool(re.search(m_rx, marketing[bank])) if bank in marketing else None)
        rows.append({"bank": bank, "promise": claim, "claimed_in_store_text": claimed,
                     "kept_mentions": kept, "broken_mentions": broken,
                     "kept_share_pct": round(kept / (kept + broken) * 100, 1) if kept + broken else None,
                     "reviews": len(g)})
out = pd.DataFrame(rows)
out.to_csv(f"claims_{a.name}.csv", index=False)

pd.set_option("display.width", 200)
for bank, g in out.groupby("bank"):
    print(f"\n{bank} ({g.reviews.iloc[0]} reviews)")
    print(g.drop(columns=["bank", "reviews"]).to_string(index=False))
print("\nkept = 4-5 star reviews praising it; broken = 1-2 star reviews saying it failed. Keyword rules are rough.")
print(f"Saved claims_{a.name}.csv")
