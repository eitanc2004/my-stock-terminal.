import streamlit as st
import pandas as pd
import requests

# --- הגדרות מערכת ---
st.set_page_config(page_title="Eitan Quantitative Terminal", layout="wide")
st.title("🏛️ Eitan Quantitative Terminal - גרסה יציבה")

# וידוא קיום מפתח API
if "FMP_API_KEY" not in st.secrets:
    st.error("Missing FMP_API_KEY in Streamlit Secrets!")
    st.stop()

FMP_KEY = st.secrets["FMP_API_KEY"]
BASE_URL = "https://financialmodelingprep.com/api/v3/"

def get_fmp(endpoint, ticker):
    try:
        url = f"{BASE_URL}{endpoint}/{ticker}?apikey={FMP_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if r.status_code == 200 and isinstance(data, list) and len(data) > 0:
            return data
        return None
    except Exception as e:
        return None

def classify_stock(ticker):
    m_list = get_fmp("key-metrics-ttm", ticker)
    r_list = get_fmp("ratios-ttm", ticker)
    
    if not m_list or not r_list: 
        return "⚪ ללא נתונים"
    
    m, r = m_list[0], r_list[0]
    pe = m.get('peRatioTTM', 999)
    roic = m.get('roicTTM', 0) * 100
    z_score = m.get('altmanZScoreTTM', 0)
    
    if z_score < 1.8 or roic < 10:
        return "🔴 לא רלוונטי"
    elif pe <= 15 and roic >= 15 and z_score >= 3:
        return "🟢 פוטנציאלית (BUY)"
    else:
        return "🟡 למעקב (Watchlist)"

# --- ממשק משתמש ---
tab1, tab2 = st.tabs(["🔍 חקירה כמותית", "📊 סורק רוחבי"])

with tab1:
    ticker = st.text_input("הזן סימול:", "PYPL").upper()
    if ticker:
        with st.spinner("מושך נתונים..."):
            p_data = get_fmp("profile", ticker)
            m_data = get_fmp("key-metrics-ttm", ticker)
            
            if p_data and m_data:
                p, m = p_data[0], m_data[0]
                st.header(f"דו\"ח: {p.get('companyName', ticker)}")
                st.metric("P/E", round(m.get('peRatioTTM', 0), 1))
                st.metric("ROIC", f"{round(m.get('roicTTM', 0)*100, 1)}%")
            else:
                st.error(f"לא נמצאו נתונים עבור {ticker}. בדוק את הסימול.")

with tab2:
    st.subheader("סריקה קבוצתית")
    user_list = st.text_area("רשימת מניות (פסיקים):", "CROX, PYPL, NVDA")
    if st.button("הפעל סריקה"):
        tickers = [t.strip().upper() for t in user_list.split(",") if t.strip()]
        results = {"🟢 פוטנציאלית (BUY)": [], "🟡 למעקב (Watchlist)": [], "🔴 לא רלוונטי": [], "⚪ ללא נתונים": []}
        
        for t in tickers:
            cat = classify_stock(t)
            if cat: results[cat].append(t)
        
        st.write(results)
