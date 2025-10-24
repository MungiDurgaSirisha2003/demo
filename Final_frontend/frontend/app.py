import streamlit as st
import pandas as pd
import plotly.io as pio
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="🎫 Ticket Analytics Dashboard", layout="wide")

# -------------------- CUSTOM STYLING --------------------
st.markdown("""
<style>
/* Page background & font */
body {
    background: linear-gradient(to bottom right, #e3f2fd, #ffffff);
    font-family: "Poppins", sans-serif;
    color: #222;
}

/* Title and headers */
h1, h2, h3 {
    font-family: "Poppins", sans-serif;
    font-weight: 600;
    color: #1e3a8a;
}

/* Card style */
.card {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #4a90e2, #007aff);
    color: white;
    border-radius: 25px;
    padding: 0.6rem 1.5rem;
    border: none;
    font-weight: 500;
    box-shadow: 0 4px 10px rgba(0,122,255,0.3);
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #007aff, #4a90e2);
    transform: translateY(-2px);
}

/* Chat Section */
.chat-container {
    background: white;
    border-radius: 15px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
    padding: 15px;
    height: 400px;
    overflow-y: auto;
    scroll-behavior: smooth;
    border: 1px solid #e0e0e0;
}

/* Chat bubbles */
.user-msg {
    background: #dbeafe;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;
    max-width: 90%;
    color: #1e40af;
}
.ai-msg {
    background: #f0f9ff;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;
    color: #1e3a8a;
    border-left: 4px solid #3b82f6;
    max-width: 90%;
}

/* KPI metrics */
[data-testid="stMetricValue"] {
    color: #1d4ed8 !important;
    font-weight: 600 !important;
    font-size: 22px !important;
}
[data-testid="stMetricLabel"] {
    color: #334155 !important;
}

/* Scrollbar customization */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #93c5fd;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# -------------------- PAGE HEADER --------------------
st.title("🎫 Ticket Analytics Dashboard")
st.markdown("<p style='color:#475569;font-size:18px;'>Upload a dataset and let AI uncover insights, patterns, and trends from your ticket data.</p>", unsafe_allow_html=True)

# -------------------- FILE UPLOAD SECTION --------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    uploaded_file = st.file_uploader("📂 Upload your dataset (CSV or Excel)", type=["csv", "xlsx", "xls"])
    analyze_btn = st.button("🚀 Analyze Data")

# -------------------- STATE VARIABLES --------------------
for key in ["df","summary","date_col","cat_col","res_col","ticket_col","dataset_sample_csv","kpis","figs"]:
    if key not in st.session_state:
        st.session_state[key] = None

# -------------------- FILE HANDLING --------------------
if uploaded_file and analyze_btn:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    with st.spinner("🔍 Uploading and analyzing your data..."):
        resp = requests.post(f"{BACKEND_URL}/analyze", files=files)
    if resp.status_code != 200:
        st.error(f"❌ Analysis failed: {resp.text}")
    else:
        data = resp.json()
        st.session_state.date_col = data.get("date_col")
        st.session_state.cat_col = data.get("cat_col")
        st.session_state.res_col = data.get("res_col")
        st.session_state.ticket_col = data.get("ticket_col")
        st.session_state.summary = data.get("summary")
        st.session_state.kpis = data.get("kpis")
        st.session_state.dataset_sample_csv = data.get("dataset_sample_csv")
        st.session_state.figs = data.get("figs")

        # Load dataset for interaction
        uploaded_file.seek(0)
        suffix = uploaded_file.name.lower().split('.')[-1]
        if suffix == "csv":
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state.df = df
        st.success("✅ Analysis completed successfully!")

# -------------------- DASHBOARD DISPLAY --------------------
if st.session_state.df is not None:
    df = st.session_state.df
    date_col = st.session_state.date_col
    cat_col = st.session_state.cat_col
    res_col = st.session_state.res_col
    ticket_col = st.session_state.ticket_col
    summary = st.session_state.summary
    figs = st.session_state.figs

    # --- KPI CARDS ---
    st.markdown("### 📈 Key Insights")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Tickets", df.shape[0])
    if res_col:
        kpi2.metric("Avg Resolution Time", round(pd.to_numeric(df[res_col], errors='coerce').mean(),2))
    else:
        kpi2.metric("Avg Resolution Time", "N/A")
    if cat_col:
        try:
            top_cat = df[cat_col].value_counts().idxmax()
        except Exception:
            top_cat = "N/A"
        kpi3.metric("Peak Category", top_cat)
    else:
        kpi3.metric("Peak Category", "N/A")

    st.markdown("---")

    # --- VISUALIZATIONS + SUMMARY SIDE BY SIDE ---
    left_col, right_col = st.columns([2,1])

    with left_col:
        st.subheader("📊 Data Visualizations")
        if figs:
            if "tickets_per_day" in figs:
                fig = pio.from_json(figs["tickets_per_day"])
                st.plotly_chart(fig, use_container_width=True)
            if "tickets_by_category" in figs:
                fig = pio.from_json(figs["tickets_by_category"])
                st.plotly_chart(fig, use_container_width=True)
            if "resolution_trend" in figs:
                fig = pio.from_json(figs["resolution_trend"])
                st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("🧠 AI Summary")
        if summary:
            st.markdown(f"<div class='card'>{summary}</div>", unsafe_allow_html=True)

        # --- Chatbot Section ---
        st.subheader("💬 Chat with Your Dataset")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_q = st.text_input("💭 Ask a question (e.g., 'What was the busiest day?')")

        if user_q:
            with st.spinner("🤔 Thinking..."):
                resp = requests.post(f"{BACKEND_URL}/chat", json={
                    "question": user_q,
                    "dataset_sample_csv": st.session_state.dataset_sample_csv
                })
                if resp.status_code == 200:
                    ans = resp.json().get("answer")
                else:
                    ans = f"⚠️ Chat error: {resp.text}"
                st.session_state.chat_history.append({"user": user_q, "ai": ans})

        # Scrollable Chat Container
        chat_html = "<div class='chat-container'>"
        for chat in st.session_state.chat_history:
            chat_html += f"<div class='user-msg'>🧑 <b>You:</b> {chat['user']}</div>"
            chat_html += f"<div class='ai-msg'>🤖 <b>AI:</b> {chat['ai']}</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # Optional clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
