import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set(style="whitegrid")

# Set Streamlit page config
st.set_page_config(page_title="Tavily Usage Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Tavily Data Analysis Home Test - BI.csv")
    df.columns = df.columns.str.upper()
    return df

df = load_data()

# Drop high-null columns and parse time
df = df.loc[:, df.isnull().mean() < 0.4]
df = df.dropna(subset=["CREATED"])
df["CREATED"] = pd.to_datetime(df["CREATED"])
df["DATE"] = df["CREATED"].dt.date
df["WEEK"] = df["CREATED"].dt.to_period("W").apply(lambda r: r.start_time)
df["MONTH"] = df["CREATED"].dt.to_period("M").apply(lambda r: r.start_time)

# --- KPI and Metrics SECTION ---
st.title("📊 Tavily User Behavior Dashboard")
st.markdown("### Key Performance Indicators")

total_records = len(df)
success_rate = (df["STATUS"] == "done").mean()
failure_rate = (df["STATUS"] == "failed").mean()
url_rate = df[df["SUCCESSFUL_URLS"]>0]["SUCCESSFUL_URLS"].mean()
avg_EXTRACT_TIME = df["EXTRACT_TIME"].mean()

col1, col2, col3,col4 = st.columns(4)
col1.metric("Success Rate", f"{success_rate:.2%}")
col2.metric("Failure Rate", f"{failure_rate:.2%}")
col3.metric(" average successful url count", f"{url_rate:.1f}")
col4.metric(" Avg extract time(seconds)", f"{avg_EXTRACT_TIME:.1f}")



st.markdown("### Additional KPIs")

# Compute averages
avg_total_credits = df["TOTAL_CREDITS"].mean()
avg_mapping_time = df["MAPPING_TIME"].mean()
avg_response_time = df["RESPONSE_TIME"].mean()
avg_llm_calls = df["TOTAL_LLM_CALLS"].mean()

col5, col6, col7, col8 = st.columns(4)
col5.metric("Avg Total Credits Used", f"{avg_total_credits:.1f}")
col6.metric("Avg Mapping Time (s)", f"{avg_mapping_time:.2f}")
col7.metric("Avg Response Time (s)", f"{avg_response_time:.2f}")
col8.metric("Avg LLM Calls", f"{avg_llm_calls:.1f}")




st.markdown("---")

# --- TIME SERIES PLOTS ---
st.subheader("⏱️ Time Series Analysis of  crawl request")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Daily Activity**")
    st.line_chart(df.groupby("DATE").size())

with col2:
    st.markdown("**Weekly Activity**")
    st.line_chart(df.groupby("WEEK").size())

with col3:
    st.markdown("**Monthly Activity**")
    st.line_chart(df.groupby("MONTH").size())

st.markdown("---")

# --- BREAKDOWN PLOTS ---
st.subheader("🔍 Breakdown Analysis")

# Row 1: Pie chart and Extract Depth Distribution
col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    status_counts = df["STATUS"].value_counts()
    ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.set_title("Status Distribution")
    fig1.tight_layout()
    st.pyplot(fig1, use_container_width=True)

    st.divider()  

with col2:
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.countplot(data=df, x="EXTRACT_DEPTH", order=df["EXTRACT_DEPTH"].value_counts().index, ax=ax2, palette="Set2")
    ax2.set_title("Extract Depth Distribution")
    ax2.set_ylabel("Count")
    ax2.set_xlabel("Extract Depth")
    plt.xticks(rotation=45)
    fig2.tight_layout()
    st.pyplot(fig2, use_container_width=True)
    st.divider()  

# Row 2: Avg LLM calls & Avg Response Time
col3, col4 = st.columns(2)

with col3:
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    depth_pages = df.groupby("EXTRACT_DEPTH")["TOTAL_LLM_CALLS"].mean().sort_values()
    sns.barplot(x=depth_pages.index, y=depth_pages.values, ax=ax3, palette="Set2")
    ax3.set_title("Avg LLM Calls by Extract Depth")
    ax3.set_ylabel("Avg LLM Calls")
    ax3.set_xlabel("Extract Depth")
    fig3.tight_layout()
    st.pyplot(fig3, use_container_width=True)
    st.divider()  

with col4:
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    response_by_status = df.groupby("STATUS")["RESPONSE_TIME"].mean().sort_values()
    sns.barplot(x=response_by_status.index, y=response_by_status.values, ax=ax4, palette="Set2")
    ax4.set_title("Avg Response Time by Status")
    ax4.set_ylabel("Avg Seconds")
    ax4.set_xlabel("Status")
    fig4.tight_layout()
    st.pyplot(fig4, use_container_width=True)

st.markdown("---")
st.markdown("✅ Dashboard built with Streamlit | © Tavily Analytics")
