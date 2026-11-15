#!/bin/bash
# Runs the whole pipeline in order. Use: bash run_all.sh
set -e
python3 scrape_reviews.py        # 1. collect reviews (slow)
python3 make_clean.py            # 2. fix the date window, park small banks
python3 score_sentiment_v2.py    # 3. sentiment (stars + VADER cross-check)
python3 find_themes.py           # 4. complaint and praise themes
python3 ranking.py               # 5. ranking with margin of error
python3 trend.py                 # 6. monthly trend + chart
python3 change_drivers.py        # 7. what changed in the bad months
python3 robust_check.py          # 8. check using only substantive reviews
