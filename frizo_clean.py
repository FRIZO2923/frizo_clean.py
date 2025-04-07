import streamlit as st
import datetime
import pytz
import pandas as pd
import matplotlib.pyplot as plt
import random

# Set page config
st.set_page_config(page_title="Frizo Predictor", layout="centered")

# Title
st.markdown("<h1 style='text-align: center;'>🎯 FRIZO PREDICTOR 😈</h1>", unsafe_allow_html=True)

# Show referral
if "show_referral" not in st.session_state:
    st.session_state.show_referral = True

if st.session_state.show_referral_popup:
    st.markdown(
        """
        <div style="border: 3px dashed #FF7F50; padding: 20px; border-radius: 15px;
                    background-color: #fff8f0; text-align: center; font-size: 18px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 20px; animation: pulse 2s infinite;">
            🤑 <strong style="font-size: 22px;">Get ₹100 Cashback</strong> on ₹300 Recharge!<br><br>
            👉 Create a new account using our referral link to unlock secret prediction benefits.<br><br>
            🔗 <a href="https://www.bigdaddygame.net//#/register?invitationCode=Narn6464148"
                 target="_blank" style="text-decoration: none; color: #FF4500; font-weight: bold;">
                 🔥 Click Here to Register Now
            </a>
        </div>

        <style>
        @keyframes pulse {
            0% {transform: scale(1);}
            50% {transform: scale(1.03);}
            100% {transform: scale(1);}
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    if st.button("❌ Close Message"):
        st.session_state.show_referral_popup = False
        st.session_state.popup_last_closed = datetime.datetime.now()


# Show time
ist = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(ist)
st.subheader(f"🕒 IST Time: `{now.strftime('%H:%M:%S')}`")
st.subheader(f"⏳ Next Round In: `{60 - now.second}` seconds")

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "current_period" not in st.session_state:
    st.session_state.current_period = None
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "stats" not in st.session_state:
    st.session_state.stats = {"correct": 0, "total": 0}
if "wrong_streak" not in st.session_state:
    st.session_state.wrong_streak = 0

# Period input
with st.expander("🧮 Enter Current Period (last 3 digits)"):
    period = st.text_input("Enter digits", max_chars=3)
    if period.isdigit():
        st.session_state.current_period = int(period)

if st.session_state.current_period:
    st.markdown(f"### Period: `{st.session_state.current_period}`")

def add_result(result):
    if st.session_state.current_period:
        st.session_state.history.append({"period": st.session_state.current_period, "result": result})
        pred = st.session_state.last_prediction
        if pred and pred["value"] == result:
            st.session_state.stats["correct"] += 1
            st.session_state.wrong_streak = 0
        elif pred:
            st.session_state.wrong_streak += 1
        st.session_state.stats["total"] += 1
        st.session_state.current_period -= 1
        st.session_state.last_prediction = None

def predict(history):
    values = [h["result"] for h in history]
    if len(values) < 5:
        return None, 0
    recent = values[-5:]
    counts = {"Big": 0, "Small": 0}
    for i in range(len(values) - 5):
        if values[i:i+5] == recent:
            counts[values[i+5]] += 1
    total = sum(counts.values())
    if total == 0:
        return None, 0
    best = max(counts, key=counts.get)
    confidence = int((counts[best] / total) * 100)
    return best, confidence

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🔴 BIG"):
        add_result("Big")
with col2:
    if st.button("🔵 SMALL"):
        add_result("Small")
with col3:
    if st.button("🧹 Reset All"):
        st.session_state.history = []
        st.session_state.current_period = None
        st.session_state.last_prediction = None
        st.session_state.stats = {"correct": 0, "total": 0}
        st.session_state.wrong_streak = 0

# Predict
count = len(st.session_state.history)
st.info(f"✅ Entries: `{count}` / 50")

if count >= 50:
    st.markdown("## 🔮 Prediction Mode")
    pred, conf = predict(st.session_state.history)
    if pred:
        if st.session_state.wrong_streak >= 3:
            pred = "Small" if pred == "Big" else "Big"
            st.warning("🔄 Reversal Detected")
        st.success(f"🎯 Prediction: `{pred}` with `{conf}%` confidence")
        st.session_state.last_prediction = {"value": pred, "confidence": conf}
    else:
        st.warning("⚠️ Not enough pattern match")

    s = st.session_state.stats
    if s["total"] > 0:
        acc = int((s["correct"] / s["total"]) * 100)
        st.info(f"📊 Accuracy: `{s['correct']}` / `{s['total']}` = **{acc}%**")

# History
if st.session_state.history:
    df = pd.DataFrame(reversed(st.session_state.history))
    df.index = range(1, len(df)+1)
    df.index.name = "Sr"
    st.dataframe(df.rename(columns={"period": "Period", "result": "Result"}), use_container_width=True)

    res = [r["result"] for r in st.session_state.history]
    fig, ax = plt.subplots()
    ax.pie([res.count("Big"), res.count("Small")],
           labels=["Big", "Small"], autopct="%1.1f%%", colors=["red", "blue"], startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
