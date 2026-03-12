import streamlit as st
import requests
import json
import pandas as pd
import sqlite3
import os

st.set_page_config(layout="wide", page_title="Hybrid Knowledge Search")

# Constants
API_URL = "http://127.0.0.1:8000"
DB_PATH = os.path.join("data", "metrics", "observability.db")

def search_page():
    st.title("Search Knowledge Base")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Enter your query:", key="search_query")
        
    with col2:
        alpha = st.slider("Alpha (0.0 = Vector, 1.0 = BM25)", 0.0, 1.0, 0.5, 0.1)
        
    if st.button("Search") or query:
        if query:
            try:
                response = requests.post(f"{API_URL}/search", json={
                    "query": query,
                    "top_k": 10,
                    "alpha": alpha
                })
                
                if response.status_code == 200:
                    data = response.json()
                    st.write(f"Latency: {data['latency_ms']:.2f} ms")
                    
                    results = data["results"]
                    if not results:
                        st.warning("No results found.")
                        
                    for res in results:
                        st.subheader(res["title"])
                        st.write(res["snippet"])
                        
                        scores_str = f"BM25: {res['bm25_score']:.4f} | Vector: {res['vector_score']:.4f} | Hybrid: {res['hybrid_score']:.4f}"
                        st.caption(scores_str)
                        st.divider()
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {e}")

def kpi_page():
    st.title("Key Performance Indicators")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df_logs = pd.read_sql_query("SELECT * FROM search_logs", conn)
        conn.close()
        
        if df_logs.empty:
            st.warning("No logs available.")
            return
            
        col1, col2, col3 = st.columns(3)
        
        p50_latency = df_logs["latency_ms"].quantile(0.5)
        p95_latency = df_logs["latency_ms"].quantile(0.95)
        zero_results_count = (df_logs["result_count"] == 0).sum()
        
        with col1:
            st.metric("P50 Latency (ms)", f"{p50_latency:.2f}")
        with col2:
            st.metric("P95 Latency (ms)", f"{p95_latency:.2f}")
        with col3:
            st.metric("Zero-Result Queries", f"{zero_results_count}")
            
        st.subheader("Query Volume Over Time")
        df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])
        df_logs.set_index("timestamp", inplace=True)
        volume = df_logs.resample("1Min").size()
        st.line_chart(volume)
        
        st.subheader("Top Queries")
        top_queries = df_logs["query"].value_counts().head(10).reset_index()
        st.table(top_queries)
        
    except Exception as e:
        st.error(f"Failed to load metrics connecting to SQLite DB: {e}")

def eval_page():
    st.title("Evaluation Results")
    try:
        df = pd.read_csv("data/metrics/experiments.csv")
        st.dataframe(df)
        
        st.subheader("nDCG@10 Trend")
        st.line_chart(df.set_index("alpha")["ndcg_at_10"])
        
    except FileNotFoundError:
        st.warning("No evaluation results found. Please run the evaluation script.")

def logs_page():
    st.title("Observability / Debug Logs")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM search_logs ORDER BY timestamp DESC", conn)
        conn.close()
        
        st.subheader("Filter Logs")
        col1, col2 = st.columns(2)
        with col1:
            severity = st.selectbox("Severity", ["All", "INFO", "ERROR"])
        with col2:
            time_range = st.selectbox("Time Range", ["All Time", "Last Hour", "Last 24 Hours"])
            
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # Using current local time
            now = pd.Timestamp.now()
            
            if time_range == "Last Hour":
                df = df[df["timestamp"] >= now - pd.Timedelta(hours=1)]
            elif time_range == "Last 24 Hours":
                df = df[df["timestamp"] >= now - pd.Timedelta(days=1)]
                
            df["error"] = df["error"].fillna("")
            
            if severity == "ERROR":
                df = df[df["error"] != ""]
            elif severity == "INFO":
                df = df[df["error"] == ""]
                
        st.dataframe(df)
    except Exception as e:
        st.error(f"Failed to load SQLite DB: {e}")

# Navigation
pages = {
    "Search": search_page,
    "KPI Dashboard": kpi_page,
    "Evaluation": eval_page,
    "Logs": logs_page
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))
page = pages[selection]
page()
