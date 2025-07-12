import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import io
import requests

# Page config
st.set_page_config(page_title="Lead Scoring Dashboard", layout="wide")

st.title("📊 Lead Scoring Dashboard")
st.markdown("Upload your Excel file, explore it, and score leads using your ML model via API.")

# Upload Excel
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"✅ Loaded {df.shape[0]} rows and {df.shape[1]} columns")

        # Navigation
        section = st.sidebar.radio("🔍 Navigation", ["EDA", "Score Leads", "Export"])

        # --------------------------
        # 🧠 EDA Section
        # --------------------------
        if section == "EDA":
            st.header("🔍 Exploratory Data Analysis")

            st.subheader("📋 Data Preview")
            st.dataframe(df.head())

            st.subheader("🧱 Data Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.write("Shape:", df.shape)
                st.write("Columns:", df.columns.tolist())
            with col2:
                st.write("Missing Values:")
                st.dataframe(df.isnull().sum())

            st.subheader("📊 Numerical Distributions")
            numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()
            selected = st.multiselect("Select numeric columns", numeric_cols, default=numeric_cols[:2])
            for col in selected:
                fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}")
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("📈 Correlation Heatmap")
            if len(numeric_cols) >= 2:
                fig = sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm")
                st.pyplot()

        # --------------------------
        # 🤖 Lead Scoring Section (Batch)
        # --------------------------
        elif section == "Score Leads":
            st.header("🎯 Scoring Leads using ML API (Batch)")

            with st.spinner("Scoring leads in batch..."):
                try:
                    # Clean invalid float values
                    df_cleaned = df.replace([float("inf"), float("-inf")], pd.NA).dropna()

                    response = requests.post(
                        "http://127.0.0.1:5000/predict",
                        json=df_cleaned.to_dict(orient="records")
                    )
                    result = response.json()

                    if "error" in result:
                        st.error(f"❌ API Error: {result['error']}")
                        st.stop()

                    scores_df = pd.DataFrame(result)
                    scored_df = pd.concat([df_cleaned.reset_index(drop=True), scores_df], axis=1)
                    scored_df = scored_df.sort_values(by="lead_score_percent", ascending=False)
                    st.session_state["scored_df"] = scored_df

                    st.success("✅ Batch scoring complete!")

                    st.subheader("📊 Scored Leads")
                    search = st.text_input("🔍 Search rows:")
                    if search:
                        filtered = scored_df[
                            scored_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                        ]
                    else:
                        filtered = scored_df

                    st.dataframe(filtered)

                except Exception as e:
                    st.error(f"❌ Failed to score leads: {e}")


        # --------------------------
        # 📤 Export Section
        # --------------------------
        elif section == "Export":
            st.header("📤 Export Scored Data")
            if "scored_df" not in st.session_state:
                st.warning("⚠️ Score leads first to enable export.")
            else:
                scored_df = st.session_state["scored_df"]

                col1, col2 = st.columns(2)

                with col1:
                    csv = scored_df.to_csv(index=False)
                    st.download_button("⬇️ Download CSV", csv, "scored_leads.csv", "text/csv")

                with col2:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        scored_df.to_excel(writer, index=False)
                    buffer.seek(0)
                    st.download_button(
                        "⬇️ Download Excel",
                        buffer,
                        "scored_leads.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    except Exception as e:
        st.error(f"❌ Failed to process file: {e}")
