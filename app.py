import streamlit as st
import requests

st.set_page_config(page_title="Eitan Terminal", layout="wide")
st.title("🏛️ טרמינל איתן - ניתוח ערך ופורנזיקה")

# משיכת המפתח מהכספת
if "FMP_API_KEY" not in st.secrets:
    st.error("❌ המפתח לא מוגדר ב-Secrets!")
    st.stop()

FMP_KEY = st.secrets["FMP_API_KEY"]

def get_data(ticker):
    # שימוש ב-Key Metrics לטובת ROIC ומכפיל רווח [cite: 2026-01-09]
    url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except: return None

def classify(ticker):
    data = get_data(ticker)
    if not data: return "⚪ ללא נתונים"
    m = data[0]
    # הקריטריונים של איתן: P/E נמוך, ROIC גבוה, Altman-Z חזק [cite: 2026-01-07, 2026-01-09]
    pe = m.get('peRatioTTM', 999)
    roic = m.get('roicTTM', 0) * 100
    z = m.get('altmanZScoreTTM', 0)
    
    if z < 1.8 or roic < 10: return "🔴 לא רלוונטי"
    if pe <= 15 and roic >= 15 and z >= 3: return "🟢 פוטנציאלית (BUY)"
    return "🟡 למעקב (Watchlist)"

# --- ממשק משתמש ---
tab1, tab2 = st.tabs(["🔍 בדיקה בודדת", "📊 סורק מהיר"])

with tab1:
    t = st.text_input("הזן סימול:", "PYPL").upper()
    if t:
        st.write(f"סטטוס עבור {t}: **{classify(t)}**")

with tab2:
    st.info("💡 הסורק ירוץ ברגע שתעדכן את הרשימה ותלחץ Enter")
    raw_list = st.text_area("רשימת מניות (פסיקים):", "CROX, PYPL, NVDA, CALM, ADM")
    if raw_list:
        tickers = [x.strip().upper() for x in raw_list.split(",") if x.strip()]
        res = {"🟢 פוטנציאליות": [], "🟡 למעקב": [], "🔴 לא רלוונטי": []}
        
        for ticker in tickers:
            cat = classify(ticker).split(" ")[0] # לוקח רק את האימוג'י והמילה הראשונה
            if "🟢" in cat: res["🟢 פוטנציאליות"].append(ticker)
            elif "🟡" in cat: res["🟡 למעקב"].append(ticker)
            else: res["🔴 לא רלוונטי"].append(ticker)
            
        c1, c2, c3 = st.columns(3)
        c1.success("🟢 פוטנציאליות")
        for x in res["🟢 פוטנציאליות"]: c1.write(x)
        c2.warning("🟡 למעקב")
        for x in res["🟡 למעקב"]: c2.write(x)
        c3.error("🔴 לא רלוונטי")
        for x in res["🔴 לא רלוונטי"]: c3.write(x)
