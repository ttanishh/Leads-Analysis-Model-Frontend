import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import requests, io

# ───────────────────────────────────────────────────────────
API_URL = "https://leads-analysis-model-2-production.up.railway.app/predict"
# ───────────────────────────────────────────────────────────

st.set_page_config(page_title="Lead Scoring Dashboard", page_icon="🎯", layout="wide")

st.title("🎯 Lead Scoring Dashboard")
st.caption("Upload an Excel file • Explore the data • Score leads with the ML API")

uploaded_file = st.file_uploader("📂  Upload Excel (.xlsx)", type=["xlsx"])

# ----------------------------------------------------------
# Helper to colour categories in dataframe display
def color_category(val):
    colors = {
        "High": "background-color:#d4f7d4;",
        "Medium": "background-color:#fff5cc;",
        "Low": "background-color:#ffd6d6;"
    }
    return colors.get(val, "")

# ----------------------------------------------------------
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"Loaded {df.shape[0]} rows • {df.shape[1]} columns")

        page = st.sidebar.radio("Navigation", ["EDA", "Score Leads", "Export"])

        # ─────────────── 1. EDA ───────────────
        if page == "EDA":
            st.header("🔍 Exploratory Data Analysis")

            with st.expander("Preview (first 5 rows)", expanded=True):
                st.dataframe(df.head(), use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rows", df.shape[0])
                st.metric("Columns", df.shape[1])
            with col2:
                st.write("Missing values:")
                st.dataframe(df.isnull().sum(), height=200)

            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if num_cols:
                st.subheader("📊 Numeric Distributions")
                chosen = st.multiselect("Select numeric columns", num_cols, default=num_cols[:2])
                for c in chosen:
                    fig = px.histogram(df, x=c, nbins=30, title=f"{c} distribution")
                    st.plotly_chart(fig, use_container_width=True)

                if len(num_cols) >= 2:
                    st.subheader("📈 Correlation Heat‑map")
                    fig, ax = plt.subplots(figsize=(8, 4))
                    sns.heatmap(df[num_cols].corr(), cmap="coolwarm", annot=True, fmt=".2f", ax=ax)
                    st.pyplot(fig)
            else:
                st.info("No numeric columns detected.")

        # ─────────────── 2. Score Leads ───────────────
        elif page == "Score Leads":
            st.header("🤖 Batch Scoring via ML API")

            with st.spinner("Calling API…"):
                df_clean = df.replace([np.inf, -np.inf], np.nan).dropna()

                try:
                    res = requests.post(API_URL, json=df_clean.to_dict(orient="records"), timeout=30)
                    res.raise_for_status()
                    pred_json = res.json()
                except Exception as e:
                    st.error(f"API error: {e}")
                    st.stop()

                preds = pd.DataFrame(pred_json)
                scored_df = pd.concat([df_clean.reset_index(drop=True), preds], axis=1)
                scored_df.sort_values("lead_score_percent", ascending=False, inplace=True)
                st.session_state["scored_df"] = scored_df

            # Quick metrics
            st.subheader("⚡ Quick Metrics")
            top10 = scored_df.head(10)
            cat_counts = scored_df["lead_category"].value_counts()
            col1, col2, col3 = st.columns(3)
            col1.metric("Top‑10 Avg %", f"{top10['lead_score_percent'].mean():.2f}")
            col2.metric("High", int(cat_counts.get("High", 0)))
            col3.metric("Medium", int(cat_counts.get("Medium", 0)))

            # Display table with colour styling
            st.subheader("📄 Scored Leads")
            search = st.text_input("Search text")
            table_df = scored_df.copy()
            if search:
                table_df = table_df[table_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

            st.dataframe(table_df.style.applymap(color_category, subset=["lead_category"]), use_container_width=True)

        # ─────────────── 3. Export ───────────────
        elif page == "Export":
            st.header("📤 Export Scored Results")
            if "scored_df" not in st.session_state:
                st.warning("Score leads first.")
                st.stop()

            scored_df = st.session_state["scored_df"]
            c1, c2 = st.columns(2)
            with c1:
                csv = scored_df.to_csv(index=False)
                st.download_button("⬇️ Download CSV", csv, file_name="scored_leads.csv", mime="text/csv")
            with c2:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
                    scored_df.to_excel(w, index=False)
                buf.seek(0)
                st.download_button(
                    "⬇️ Download Excel",
                    buf,
                    file_name="scored_leads.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as err:
        st.error(f"❌ Failed to process file: {err}")
else:
    st.info("📌 Upload a valid Excel file to begin.")
