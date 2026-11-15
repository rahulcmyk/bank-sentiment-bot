import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

df = pd.read_csv("bank_reviews_clean.csv")
analyzer = SentimentIntensityAnalyzer()

# Banking words VADER does not know (score from -4 to +4)
bank_words = {
    "blocked": -2.5, "frozen": -2.5, "freezes": -2.0, "stuck": -2.0,
    "locked": -2.0, "suspended": -2.5, "restricted": -2.0,
    "crash": -2.5, "crashes": -2.5, "crashing": -2.5, "crashed": -2.5,
    "error": -2.0, "errors": -2.0, "glitch": -2.0, "glitches": -2.0,
    "bug": -1.5, "bugs": -1.5, "buggy": -2.0,
    "failed": -2.5, "fails": -2.0, "failing": -2.0, "failure": -2.5,
    "unable": -2.0, "unresponsive": -2.5, "useless": -3.0, "rubbish": -3.0,
    "slow": -1.5, "laggy": -2.0, "lag": -1.5, "delay": -1.5, "delayed": -1.8,
    "scam": -3.5, "fraud": -3.0, "complaint": -1.5,
    "seamless": 2.5, "intuitive": 2.0, "instant": 1.5, "hassle-free": 2.5,
}
analyzer.lexicon.update(bank_words)

def score(text):
    return analyzer.polarity_scores(str(text))["compound"]

def text_label(s):
    if s >= 0.05:
        return "positive"
    if s <= -0.05:
        return "negative"
    return "neutral"

def star_label(r):
    if r <= 2:
        return "negative"
    if r == 3:
        return "neutral"
    return "positive"

print("Scoring reviews...")
df["sentiment_score"] = df["text"].apply(score)
df["sentiment_text"] = df["sentiment_score"].apply(text_label)
df["sentiment"] = df["rating"].apply(star_label)      # FINAL label (from stars)
df.to_csv("bank_reviews_scored.csv", index=False)

print("\nFINAL sentiment share per bank (%), based on star rating:")
print((pd.crosstab(df["bank"], df["sentiment"], normalize="index") * 100).round(1))

print("\nSanity check after adding banking words:")
low = df[df["rating"] <= 2]
high = df[df["rating"] >= 4]
print(f"1-2 star reviews the text also calls negative: {(low['sentiment_text'] == 'negative').mean() * 100:.1f}%  (before: 52.9%)")
print(f"4-5 star reviews the text also calls positive: {(high['sentiment_text'] == 'positive').mean() * 100:.1f}%  (before: 85.1%)")
print(f"Overall text and stars agree: {(df['sentiment_text'] == df['sentiment']).mean() * 100:.1f}%")
