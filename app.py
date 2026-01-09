import streamlit as st
import requests

# --- הגדרות טרמינל איתן ---
st.set_page_config(page_title="Eitan Forensic Terminal", layout="wide")
st.title("🏛️ הטרמינל של איתן - ניתוח ערך ופורנזיקה")

# בדיקה שהמפתח קיים בכספת
if "FMP_API_KEY" not in st.secrets:
    st.error("❌ חסר מפתח בכספת! עקוב אחר שלב 2 במדריך.")
    st.stop()

FMP_KEY = st.secrets["9Scnmo1coPSy2BxvqJUt4j6V15avI81x"]
BASE_URL = "https://financialmodelingprep.com/api/v3/"

def get_data(endpoint, ticker):
    try:
        url = f"{BASE_URL}{endpoint}/{ticker}?apikey={FMP_KEY}"
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 and r.json() else None
    except: return None

def classify_stock(ticker):
    m = get_data("key-metrics-ttm", ticker)
    if not m: return "⚪ אין נתונים"
    m = m[0]
    pe = m.get('peRatioTTM', 999)
    roic = m.get('roicTTM', 0) * 100
    z_score = m.get('altmanZScoreTTM', 0)
    
    # סינון לפי 'הפתק' של איתן
    if z_score < 1.8 or roic < 10:
        return "🔴 לא רלוונטי"
    elif pe <= 15 and roic >= 15 and z_score >= 3:
        return "🟢 פוטנציאלית (BUY)"
    else:
        return "🟡 למעקב (Watchlist)"

# --- ממשק ---
tab1, tab2 = st.tabs(["🔍 חקירה פרטנית", "📊 סורק 3 אופציות"])

with tab1:
    ticker = st.text_input("הכנס סימול (למשל CROX):", "PYPL").upper()
    if ticker:
        res = classify_stock(ticker)
        st.subheader(f"סטטוס: {res}")
        data = get_data("key-metrics-ttm", ticker)
        if data:
            st.write(f"מכפיל רווח: {round(data[0]['peRatioTTM'], 1)}")
            st.write(f"ROIC: {round(data[0]['roicTTM']*100, 1)}%")

with tab2:
    st.subheader("סינון רוחבי")
    list_in = st.text_area("רשימת מניות (פסיקים):", "CROX, PYPL, NVDA, SFM, DECK")
    if st.button("הפעל סריקה"):
        tickers = [t.strip().upper() for t in list_in.split(",")]
        results = {"🟢 פוטנציאלית (BUY)": [], "🟡 למעקב (Watchlist)": [], "🔴 לא רלוונטי": []}
        for t in tickers:
            cat = classify_stock(t)
            if cat in results: results[cat].append(t)
        st.columns(3)[0].success("🟢 פוטנציאליות")
        for s in results["🟢 פוטנציאלית (BUY)"]: st.write(s)
        st.columns(3)[1].warning("🟡 למעקב")
        for s in results["🟡 למעקב (Watchlist)"]: st.write(s)
        st.columns(3)[2].error("🔴 לא רלוונטי")
        for s in results["🔴 לא רלוונטי"]: st.write(s)
