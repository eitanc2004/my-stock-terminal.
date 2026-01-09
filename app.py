import streamlit as st
import requests

# הגדרות דף
st.set_page_config(page_title="Eitan Forensic Terminal V5", layout="wide")
st.title("🏛️ טרמינל איתן - גרסה סופית ויציבה")

# בדיקת מפתח ב-Secrets
if "FMP_API_KEY" not in st.secrets:
    st.error("❌ המפתח לא נמצא ב-Secrets של Streamlit!")
    st.stop()

FMP_KEY = st.secrets["FMP_API_KEY"]

def get_fmp_data(ticker):
    # שימוש ב-Key Metrics עבור ROIC, P/E ו-Altman Z [cite: 2026-01-07, 2026-01-09]
    url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 403:
            return "ERROR_403"
        data = r.json()
        return data[0] if data and isinstance(data, list) else None
    except:
        return None

def classify_stock(ticker):
    m = get_fmp_data(ticker)
    if m == "ERROR_403": return "🚫 שגיאת הרשאה (API)"
    if not m: return "⚪ אין נתונים"
    
    pe = m.get('peRatioTTM', 999)
    roic = m.get('roicTTM', 0) * 100
    z = m.get('altmanZScoreTTM', 0)
    
    # אסטרטגיית הערך של איתן [cite: 2026-01-07, 2026-01-09]
    if z < 1.8 or roic < 10:
        return "🔴 לא רלוונטי"
    elif pe <= 15 and roic >= 15 and z >= 3:
        return "🟢 פוטנציאלית (BUY)"
    else:
        return "🟡 למעקב (Watchlist)"

# --- ממשק משתמש ---
tab1, tab2 = st.tabs(["🔍 חקירה פרטנית", "📊 סורק אוטומטי"])

with tab1:
    ticker = st.text_input("הזן סימול (למשל PYPL):", "PYPL").upper()
    if ticker:
        res = classify_stock(ticker)
        st.subheader(f"אבחנה עבור {ticker}: {res}")
        m = get_fmp_data(ticker)
        if isinstance(m, dict):
            c1, c2, c3 = st.columns(3)
            c1.metric("P/E (TTM)", round(m.get('peRatioTTM', 0), 1))
            c2.metric("ROIC (%)", f"{round(m.get('roicTTM', 0)*100, 1)}%")
            c3.metric("Altman Z-Score", round(m.get('altmanZScoreTTM', 0), 2))

with tab2:
    st.info("💡 הסריקה רצה אוטומטית ברגע שמעדכנים את הרשימה")
    # רשימת המניות מהמעקב שלך [cite: 2025-12-08, 2025-12-14]
    default_list = "CROX, PYPL, NVDA, SFM, DECK, GOOGL"
    user_list = st.text_area("הדבק רשימת מניות (פסיקים):", default_list)
    
    if user_list:
        tickers = [t.strip().upper() for t in user_list.split(",") if t.strip()]
        buckets = {"🟢 פוטנציאלית": [], "🟡 למעקב": [], "🔴 לא רלוונטי": [], "🚫 שגיאה": []}
        
        with st.spinner("סורק נתונים..."):
            for t in tickers:
                cat = classify_stock(t)
                if "🟢" in cat: buckets["🟢 פוטנציאלית"].append(t)
                elif "🟡" in cat: buckets["🟡 למעקב"].append(t)
                elif "🚫" in cat: buckets["🚫 שגיאה"].append(t)
                else: buckets["🔴 לא רלוונטי"].append(t)
        
        col1, col2, col3 = st.columns(3)
        col1.success("🟢 פוטנציאליות")
        for x in buckets["🟢 פוטנציאלית"]: col1.write(f"**{x}**")
        
        col2.warning("🟡 למעקב")
        for x in buckets["🟡 למעקב"]: col2.write(x)
        
        col3.error("🔴 לא רלוונטי")
        for x in buckets["🔴 לא רלוונטי"]: col3.write(x)
        
        if buckets["🚫 שגיאה"]:
            st.divider()
            st.error(f"שגיאת הרשאה (API) עבור: {', '.join(buckets['🚫 שגיאה'])}. וודא שהמפתח תקין ותומך במניות אלו.")

