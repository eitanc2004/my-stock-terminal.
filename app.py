import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Forensic Value Terminal", layout="wide")
st.title("🏛️ Forensic Value Terminal 2026")

ticker_input = st.sidebar.text_area("הכנס מניות (מופרד בפסיק):", value="PLTR, PYPL, GOOGL, CROX")

def analyze(ticker):
    try:
        s = yf.Ticker(ticker.strip().upper())
        i = s.info
        price = i.get('currentPrice', 1)
        eps = i.get('trailingEps', 0)
        fair_v = eps * (8.5 + 2 * 5) # חישוב שמרני
        margin = ((fair_v - price) / fair_v) * 100 if fair_v > 0 else 0
        return {"מניה": ticker.upper(), "מחיר": price, "שווי הוגן": round(fair_v, 2), "מרווח %": round(margin, 1)}
    except: return None

if st.sidebar.button("הרץ סריקה"):
    tickers = ticker_input.split(',')
    results = [analyze(t) for t in tickers if analyze(t)]
    st.table(pd.DataFrame(results))