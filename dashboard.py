"""Local dashboard over teardown outputs and priority results.

Run:  pip install streamlit   (once)
      streamlit run dashboard.py

Reads teardown_*/ folders (from teardown.py) and priority_*.csv (from priority.py).
Everything stays on your computer.
"""
import glob
import os
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Bank Review Teardowns", layout="wide")


def hbar(series, label="% of reviews"):
    """Horizontal bars, longest first, full theme names."""
    d = series.reset_index()
    d.columns = ["theme", "value"]
    return (alt.Chart(d).mark_bar()
            .encode(x=alt.X("value:Q", title=label),
                    y=alt.Y("theme:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
                    tooltip=["theme", "value"])
            .properties(height=max(120, 28 * len(d))))

st.title("Bank Review Teardowns")

folders = sorted(d.rstrip("/") for d in glob.glob("teardown_*/"))
if not folders:
    st.warning("No teardown_* folders found. Run teardown.py first.")
    st.stop()

name = st.sidebar.selectbox("Teardown", folders)
st.sidebar.caption("Stars are the sentiment label: 1-2 negative, 4-5 positive. "
                   "Net sentiment = % positive minus % negative.")

def load(fname, **kw):
    path = os.path.join(name, fname)
    return pd.read_csv(path, **kw) if os.path.exists(path) else None

summary = load("summary.csv", index_col=0)
comp = load("themes_complaints.csv", index_col=0)
praise = load("themes_praise.csv", index_col=0)
monthly = load("monthly.csv")

t1, t2, t3, t4, t5 = st.tabs(["Overview", "Themes", "Monthly", "Priority", "Samples"])

with t1:
    if summary is None:
        st.info("No summary.csv in this folder.")
    else:
        st.subheader("Net sentiment by app")
        st.bar_chart(summary["net_sentiment"])
        st.dataframe(summary.round(2), use_container_width=True)
        st.caption("margin_of_error is the 95% margin on the average stars. "
                   "The *_20plus_chars columns repeat the numbers using only longer reviews, "
                   "because very short reviews inflate ratings.")

with t2:
    if comp is None:
        st.info("No theme files in this folder.")
    else:
        banks = list(comp.columns)
        bank = st.selectbox("App", banks)
        rows = [r for r in comp.index if not r.startswith("(")]
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Complaint themes")
            st.caption("% of 1-2 star reviews that mention each theme")
            st.altair_chart(hbar(comp.loc[rows, bank], "% of 1-2 star reviews"), use_container_width=True)
            st.caption(f"1-2 star reviews: {int(comp.loc['(1-2 star reviews)', bank])}. "
                       f"Matched at least one theme: {comp.loc['(any theme matched)', bank]}%")
        with c2:
            st.subheader("Praise themes")
            st.caption("% of 4-5 star reviews that mention each theme")
            st.altair_chart(hbar(praise.loc[[r for r in praise.index if not r.startswith("(")], bank],
                                 "% of 4-5 star reviews"), use_container_width=True)
            st.caption(f"4-5 star reviews: {int(praise.loc['(4-5 star reviews)', bank])}")
        st.dataframe(comp, use_container_width=True)
        st.caption("A review can mention several themes, so columns do not add to 100%. "
                   "Themes come from keyword rules.")

with t3:
    if monthly is None:
        st.info("No monthly.csv in this folder.")
    else:
        full = monthly[~monthly["partial_month"]]
        st.subheader("Average stars by full month")
        lo, hi = full.avg_stars.min() - 0.2, full.avg_stars.max() + 0.2
        line = (alt.Chart(full).mark_line(point=True)
                .encode(x=alt.X("month:N", title=None, axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("avg_stars:Q", title="Average stars",
                                scale=alt.Scale(domain=[lo, hi])),
                        color=alt.Color("bank:N", title=None),
                        tooltip=["bank", "month", "avg_stars", "margin_of_error", "reviews"])
                .properties(height=340))
        st.altair_chart(line, use_container_width=True)
        st.caption("The vertical axis does not start at zero, so small changes are visible. "
                   "Partial months (cut by the start or end date) are left out of the chart. "
                   "Compare each change with margin_of_error in the table below.")
        st.dataframe(monthly, use_container_width=True)

with t4:
    files = sorted(glob.glob("priority_*.csv"))
    if not files:
        st.info("No priority_*.csv yet. Run priority.py for an app first.")
    else:
        f = st.selectbox("Priority file", files)
        p = pd.read_csv(f)
        st.subheader("Which problem to fix first")
        st.altair_chart(hbar(p.set_index("theme")["priority"], "priority score"), use_container_width=True)
        st.dataframe(p, use_container_width=True)
        st.caption("Priority = reach x severity x (3 / effort). Effort defaults to 3 for every theme, "
                   "so the order comes from review data alone. Money columns, if present, are "
                   "illustrative and rest on assumptions you supplied.")

with t5:
    path = os.path.join(name, "samples.txt")
    if os.path.exists(path):
        st.caption("Real review text. Keep it on your computer; do not publish it.")
        st.text(open(path).read())
    else:
        st.info("No samples.txt in this folder.")
