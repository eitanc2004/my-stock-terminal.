import streamlit as st
import requests

st.set_page_config(page_title="Eitan Forensic Terminal", layout="wide")
st.title("🏛️ הטרמינל של איתן - ניתוח ערך ופורנזיקה")

# בדיקה שהמפתח קיים בכספת
if "FMP_API_KEY" not in st.secrets:
    st.error("❌ חסר מפתח ב-Secrets! ראה שלב 2 במדריך.")
    st.stop()

FMP_KEY = st.secrets["FMP_API_KEY"]

def get_data(ticker):
    url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data[0] if data else None
        return None
    except: return None

def classify_stock(ticker):
    m = get_data(ticker)
    if not m: return "⚪ ללא נתונים"
    
    pe = m.get('peRatioTTM', 999)
    roic = m.get('roicTTM', 0) * 100
    z = m.get('altmanZScoreTTM', 0)
    
    # אסטרטגיית הערך של איתן [cite: 2026-01-07, 2026-01-09]
    if z < 1.8 or roic < 10: return "🔴 לא רלוונטי"
    if pe <= 15 and roic >= 15 and z >= 3: return "🟢 פוטנציאלית (BUY)"
    return "🟡 למעקב (Watchlist)"

tab1, tab2 = st.tabs(["🔍 חקירה פרטנית", "📊 סורק קבוצתי"])

with tab1:
    ticker = st.text_input("הזן סימול לבדיקה:", "PYPL").upper()
    if ticker:
        res = classify_stock(ticker)
        st.subheader(f"סטטוס: {res}")
        m = get_data(ticker)
        if m:
            col1, col2, col3 = st.columns(3)
            col1.metric("P/E", round(m.get('peRatioTTM', 0), 1))
            col2.metric("ROIC", f"{round(m.get('roicTTM', 0)*100, 1)}%")
            col3.metric("Altman-Z", round(m.get('altmanZScoreTTM', 0), 2))

with tab2:
    st.info("💡 הסריקה תתבצע אוטומטית כשתשנה את הרשימה ותלחץ מחוץ לתיבה")
    user_list = st.text_area("הדבק רשימת מניות (פסיקים):", "CROX, PYPL, NVDA, CALM, ADM")
    
    if user_list:
        tickers = [t.strip().upper() for t in user_list.split(",") if t.strip()]
        buckets = {"🟢 פוטנציאלית": [], "🟡 למעקב": [], "🔴 לא רלוונטי": []}
        
        for t in tickers:
            cat = classify_stock(t)
            if "🟢" in cat: buckets["🟢 פוטנציאלית"].append(t)
            elif "🟡" in cat: buckets["🟡 למעקב"].append(t)
            else: buckets["🔴 לא רלוונטי"].append(t)
        
        c1, c2, c3 = st.columns(3)
        c1.success("🟢 פוטנציאליות")
        for x in buckets["🟢 פוטנציאלית"]: c1.write(x)
        c2.warning("🟡 למעקב")
        for x in buckets["🟡 למעקב"]: c2.write(x)
        c3.error("🔴 לא רלוונטי")
        for x in buckets["🔴 לא רלוונטי"]: c3.write(x)

