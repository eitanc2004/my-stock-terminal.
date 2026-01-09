import streamlit as st
import requests

st.set_page_config(page_title="Eitan Terminal V3", layout="wide")
st.title("🏛️ טרמינל איתן - גרסת אבחון פורנזי")

# --- בדיקת מפתח ---
if "FMP_API_KEY" not in st.secrets:
    st.error("❌ המפתח לא נמצא ב-Secrets של Streamlit!")
    st.stop()

FMP_KEY = st.secrets["FMP_API_KEY"]

def get_data(endpoint, ticker):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?apikey={FMP_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 403:
            st.error(f"🚫 שגיאת הרשאה ל-{ticker}: כנראה שהמפתח לא בתוקף או שהמניה לא במנוי שלך.")
            return None
        if r.status_code != 200:
            st.warning(f"⚠️ שגיאה {r.status_code} במניה {ticker}")
            return None
        data = r.json()
        return data if data else None
    except Exception as e:
        st.error(f"💥 שגיאת חיבור: {e}")
        return None

# --- לוגיקת המיון ---
def classify_stock(ticker):
    data = get_data("key-metrics-ttm", ticker)
    if not data: return "⚪ ללא נתונים"
    
    m = data[0]
    roic = m.get('roicTTM', 0) * 100
    pe = m.get('peRatioTTM', 999)
    z_score = m.get('altmanZScoreTTM', 0)
    
    # סינון קשיח (הפתק של איתן)
    if z_score < 1.8 or roic < 10: return "🔴 לא רלוונטי"
    if pe <= 15 and roic >= 15 and z_score >= 3: return "🟢 פוטנציאלית (BUY)"
    return "🟡 למעקב (Watchlist)"

# --- ממשק משתמש ---
tab1, tab2 = st.tabs(["🔍 בדיקת מניה בודדת", "📊 סריקה קבוצתית"])

with tab1:
    ticker = st.text_input("הזן סימול לבדיקה:", "PYPL").upper()
    if ticker:
        with st.expander("👁️ ראה נתונים גולמיים מה-API"):
            raw = get_data("key-metrics-ttm", ticker)
            st.write(raw) # כאן תראה אם ה-API בכלל מחזיר משהו
        
        status = classify_stock(ticker)
        st.subheader(f"סטטוס פורנזי: {status}")

with tab2:
    st.info("💡 הסריקה תתבצע ברגע שתזין רשימה ותלחץ מחוץ לתיבה")
    list_input = st.text_area("הדבק רשימת מניות (מופרדות בפסיקים):", "CROX, PYPL, NVDA, CALM")
    
    if list_input:
        tickers = [t.strip().upper() for t in list_input.split(",") if t.strip()]
        results = {"🟢 פוטנציאלית": [], "🟡 למעקב": [], "🔴 לא רלוונטי": [], "⚪ ללא נתונים": []}
        
        with st.spinner(f"סורק {len(tickers)} מניות..."):
            for t in tickers:
                cat = classify_stock(t)
                results[cat].append(t)
        
        # תצוגת תוצאות
        c1, c2, c3 = st.columns(3)
        c1.success("🟢 פוטנציאליות")
        for s in results["🟢 פוטנציאלית"]: c1.write(f"**{s}**")
        
        c2.warning("🟡 למעקב")
        for s in results["🟡 למעקב"]: c2.write(s)
        
        c3.error("🔴 לא רלוונטי")
        for s in results["🔴 לא רלוונטי"]: c3.write(s)
