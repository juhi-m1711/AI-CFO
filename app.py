import streamlit as st

st.set_page_config(
    page_title="AI CFO",
    page_icon="🔥",
    layout="wide"
)

# Sidebar
st.sidebar.title("🔥 AI CFO")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📊 Dashboard",
    "🧾 GST Tracker",
    "🚨 Fraud Detection",
    "📈 Cash Forecast",
    "🤖 AI Assistant"
])

st.sidebar.markdown("---")
st.sidebar.caption("Fireblaze Tech League 2025")

# Page routing
if page == "🏠 Home":
    st.title("🔥 Welcome to AI CFO")
    st.subheader("Your Intelligent Finance Partner")
    st.write("Navigate using the sidebar to explore features.")

elif page == "📊 Dashboard":
    from modules.dashboard import show
    show()

elif page == "🧾 GST Tracker":
    from modules.gst_tracker import show
    show()

elif page == "🚨 Fraud Detection":
    from modules.fraud_detection import show
    show()

elif page == "📈 Cash Forecast":
    from modules.cash_forecast import show
    show()

elif page == "🤖 AI Assistant":
    from modules.ai_assistant import show
    show()