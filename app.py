import streamlit as st
import requests

st.set_page_config(page_title="Eitan Forensic Terminal V-Ultimate", layout="wide")
st.title("🏛️ Eitan Forensic Terminal - הגרסה הסופית")

if "FMP_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

FMP_KEY = st.secrets["FMP_API_KEY"]

def get_data(endpoint, ticker, params=""):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?apikey={FMP_KEY}{params}"
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def deep_audit(ticker):
    # משיכת נתונים מ-4 מקורות שונים לסנכרון מלא
    m = get_data("key-metrics-ttm", ticker)
    g = get_fmp_growth = get_data("financial-growth", ticker)
    r = get_data("ratios-ttm", ticker)
    bs = get_data("balance-sheet-statement", ticker, "&limit=2")
    cf = get_data("cash-flow-statement", ticker, "&limit=1")
    
    if not m or not g or not r or not bs or not cf: return "⚪ חסר נתונים", {}

    m, g, r, bs_curr, cf = m[0], g[0], r[0], bs[0], cf[0]
    bs_prev = bs[1] if len(bs) > 1 else bs[0]

    # --- 🟢 הפתק של איתן (הבסיס) ---
    pe = m.get('peRatioTTM', 999)
    roic = m.get('roicTTM', 0) * 100
    z_score = m.get('altmanZScoreTTM', 0)
    is_green = (pe <= 15 and roic >= 15 and z_score >= 3)

    # --- 🔵 מדדי התייעלות (המסלול הכחול) ---
    margin_expansion = g.get('operatingIncomeGrowth', 0) > g.get('revenueGrowth', 0)
    buybacks = g.get('weightedAverageSharesGrowth', 0) < -0.02
    fcf_quality = m.get('freeCashFlowYieldTTM', 0) > (1/pe if pe > 0 else 0)
    blue_score = sum([margin_expansion, buybacks, fcf_quality])

    # --- 🔴 דגלים אדומים פורנזיים (ההגנה שלך) ---
    flags = []
    
    # 1. מניפולציית רווח (Accruals Flag)
    net_income = cf.get('netIncome', 1)
    ocf = cf.get('operatingCashFlow', 0)
    if ocf < net_income * 0.8:
        flags.append("❌ אזהרת מזומן: הרווח גבוה מהמזומן (Accruals high)")

    # 2. ניפוח מלאי (Inventory Bloat)
    inv_growth = (bs_curr.get('inventory', 0) / bs_prev.get('inventory', 1)) - 1
    rev_growth = g.get('revenueGrowth', 0)
    if inv_growth > rev_growth + 0.1:
        flags.append("⚠️ ניפוח מלאי: המלאי צומח מהר מהמכירות")

    # 3. מוניטין רעיל (Goodwill Bomb)
    if bs_curr.get('goodwill', 0) / bs_curr.get('totalAssets', 1) > 0.3:
        flags.append("⚠️ פצצת מוניטין: יותר מדי Goodwill במאזן")

    # --- סיווג ---
    status = "🔴 אדומה"
    if is_green: status = "🟢 ירוקה (ערך)"
    elif blue_score >= 2 and z_score > 1.8: status = "🔵 כחולה (התייעלות)"
    elif roic > 10: status = "🟡 צהובה (מעקב)"

    return status, {
        "P/E": round(pe, 1),
        "ROIC": f"{round(roic, 1)}%",
        "Z-Score": round(z_score, 2),
        "Buybacks": "✅" if buybacks else "❌

