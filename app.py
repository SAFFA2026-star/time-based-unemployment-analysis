import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Time-Based Unemployment Analysis", page_icon="📊", layout="wide")

st.title("📊 Time-Based Unemployment Data Analysis & Visualization")
st.write("Explore unemployment trends over time using an interactive Streamlit dashboard.")

@st.cache_data
def load_data():
    path = "data/unemployment.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

# Expected columns: Date/Year and Unemployment Rate.
# If your dataset uses different names, rename them here.
date_col = next((c for c in df.columns if c.lower() in ["date", "year", "time", "period"]), df.columns[0])
rate_col = next((c for c in df.columns if "unemployment" in c.lower() and "rate" in c.lower()), None)

if rate_col is None:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        st.error("No numeric unemployment-rate column was found. Please check data/unemployment.csv.")
        st.stop()
    rate_col = numeric_cols[-1]

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
if df[date_col].isna().all():
    df[date_col] = pd.to_numeric(df[date_col], errors="coerce")

df[rate_col] = pd.to_numeric(df[rate_col], errors="coerce")
df = df.dropna(subset=[date_col, rate_col]).sort_values(date_col)

st.sidebar.header("Filters")
min_rate, max_rate = float(df[rate_col].min()), float(df[rate_col].max())
rate_range = st.sidebar.slider("Unemployment rate range", min_rate, max_rate, (min_rate, max_rate))
filtered = df[df[rate_col].between(rate_range[0], rate_range[1])]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Records", f"{len(filtered):,}")
c2.metric("Average rate", f"{filtered[rate_col].mean():.2f}")
c3.metric("Minimum rate", f"{filtered[rate_col].min():.2f}")
c4.metric("Maximum rate", f"{filtered[rate_col].max():.2f}")

st.subheader("Unemployment Rate Over Time")
fig = px.line(filtered, x=date_col, y=rate_col, markers=True,
              labels={date_col: "Time", rate_col: "Unemployment Rate"},
              title="Unemployment Trend")
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Distribution")
    fig_hist = px.histogram(filtered, x=rate_col, nbins=15,
                            labels={rate_col: "Unemployment Rate"})
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("Summary Statistics")
    st.dataframe(filtered[rate_col].describe().round(2).to_frame("Value"),
                 use_container_width=True)

st.subheader("Data")
st.dataframe(filtered, use_container_width=True)

st.download_button(
    "⬇️ Download filtered data",
    filtered.to_csv(index=False).encode("utf-8"),
    "filtered_unemployment.csv",
    "text/csv"
)
