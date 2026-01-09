import streamlit as st
import requests

st.set_page_config(page_title="Eitan Terminal V4", layout="wide")
st.title("🏛️ טרמינל איתן - בדיקת מערכת סופית")

# --- בדיקת "דופק" למפתח ---
if "FMP_API_KEY" in st.secrets:
    st.success("✅ המפתח זוהה ב-Secrets! המערכת מוכנה.")
    FMP_KEY = st.secrets["FMP_API_KEY"]
else:
    st.error("❌ המפתח עדיין לא מוגדר ב-Secrets של Streamlit.")
    st.stop()

def get_pypl_test():
    # בדיקה ספציפית לפייפאל
    url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/PYPL?apikey={FMP_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

# --- הצגת נתונים ---
st.subheader("ניתוח פייפאל (PYPL)")
data = get_pypl_test()

if data:
    m = data[0]
    col1, col2, col3 = st.columns(3)
    # כאן הנתונים יהיו "בכחול" (Metrics)
    col1.metric("מכפיל רווח (P/E)", round(m['peRatioTTM'], 1))
    col2.metric("ROIC", f"{round(m['roicTTM']*100, 1)}%")
    col3.metric("חוסן (Altman-Z)", round(m['altmanZScoreTTM'], 2))
    
    # אבחון פורנזי מהיר [cite: 2026-01-09]
    if m['roicTTM'] > 0.15 and m['peRatioTTM'] < 15:
        st.balloons()
        st.success("🟢 PYPL עומדת בקריטריונים של הפתק!")
    else:
        st.warning("🟡 PYPL דורשת חקירה נוספת - לא הכל ירוק.")
else:
    st.warning("⚠️ לא התקבלו נתונים מ-FMP. וודא שהמפתח תקין.")

