import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from supabase import create_client, Client
from datetime import datetime, timedelta, date
import re
from google import genai
from google.genai import types

st.set_page_config(
    page_title="SpendSmart",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
#  SUPABASE
# ─────────────────────────────────────────
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Restore session if available
if "access_token" in st.session_state and "refresh_token" in st.session_state:
    try:
        supabase.auth.set_session(st.session_state["access_token"], st.session_state["refresh_token"])
    except: pass


# ─────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1rem 1rem 2rem!important;max-width:100%!important;}

/* AUTH */
.auth-brand{font-size:30px;font-weight:700;color:#6366f1;text-align:center;letter-spacing:-1px;}
.auth-brand span{color:#0f172a;}
.auth-sub{font-size:14px;color:#64748b;text-align:center;margin-bottom:1.6rem;}
.divider-or{display:flex;align-items:center;gap:10px;margin:1rem 0;}
.divider-or::before,.divider-or::after{content:'';flex:1;height:1px;background:#e2e8f0;}
.divider-or span{font-size:12px;color:#94a3b8;}
.google-btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:12px;border:1.5px solid #e2e8f0;border-radius:12px;background:#fff;font-size:14px;font-weight:500;color:#0f172a;text-decoration:none;margin-bottom:4px;}
.google-btn:hover{background:#f8fafc;}

/* BOXES */
.e-box{background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:10px 14px;color:#991b1b;font-size:13px;margin-bottom:10px;}
.s-box{background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:10px 14px;color:#166534;font-size:13px;margin-bottom:10px;}
.i-box{background:#eff6ff;border:1px solid #93c5fd;border-radius:10px;padding:10px 14px;color:#1e40af;font-size:13px;margin-bottom:10px;}
.w-box{background:#fff7ed;border:1px solid #fdba74;border-radius:10px;padding:10px 14px;color:#9a3412;font-size:13px;margin-bottom:8px;}

/* METRICS */
div[data-testid="metric-container"]{background:#fff;border:0.5px solid #e2e8f0;border-radius:14px;padding:12px 14px;box-shadow:0 1px 4px rgba(0,0,0,.05);}
div[data-testid="metric-container"] label{color:#64748b!important;font-size:11px!important;font-weight:500;}
div[data-testid="metric-container"] div[data-testid="stMetricValue"]{color:#0f172a!important;font-size:20px!important;font-weight:700;}

/* SECTION HEADERS */
.sh{font-size:14px;font-weight:600;color:#0f172a;border-left:3px solid #6366f1;padding-left:8px;margin:16px 0 10px;}

/* CARDS */
.cc{background:#fff;border:0.5px solid #e2e8f0;border-radius:14px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.04);margin-bottom:12px;}

/* BUDGET BAR */
.bw{background:#f1f5f9;border-radius:10px;padding:12px 14px;margin-bottom:8px;}
.bl{font-size:12px;color:#64748b;margin-bottom:6px;}
.bb{background:#e2e8f0;border-radius:99px;height:9px;}
.bf{height:9px;border-radius:99px;}

/* ALERTS */
.a1{background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:10px 14px;color:#166534;font-size:13px;margin-bottom:8px;}
.a2{background:#fff7ed;border:1px solid #fdba74;border-radius:10px;padding:10px 14px;color:#9a3412;font-size:13px;margin-bottom:8px;}
.a3{background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:10px 14px;color:#991b1b;font-size:13px;margin-bottom:8px;}

/* INSIGHT */
.ic{background:#f8fafc;border:0.5px solid #e2e8f0;border-radius:10px;padding:10px 12px;font-size:13px;color:#334155;line-height:1.6;margin-bottom:8px;}
.ic b{color:#0f172a;}

/* SMART ALERT CARD */
.alert-card{border-radius:14px;padding:14px 16px;margin-bottom:10px;display:flex;align-items:flex-start;gap:12px;}
.alert-icon{font-size:22px;line-height:1;flex-shrink:0;margin-top:2px;}
.alert-body{flex:1;}
.alert-title{font-size:14px;font-weight:600;margin-bottom:3px;}
.alert-msg{font-size:13px;line-height:1.5;}
.alert-red{background:#fef2f2;border:1px solid #fca5a5;}
.alert-red .alert-title{color:#991b1b;}
.alert-red .alert-msg{color:#b91c1c;}
.alert-orange{background:#fff7ed;border:1px solid #fdba74;}
.alert-orange .alert-title{color:#9a3412;}
.alert-orange .alert-msg{color:#b45309;}
.alert-green{background:#f0fdf4;border:1px solid #86efac;}
.alert-green .alert-title{color:#166534;}
.alert-green .alert-msg{color:#15803d;}
.alert-blue{background:#eff6ff;border:1px solid #93c5fd;}
.alert-blue .alert-title{color:#1e40af;}
.alert-blue .alert-msg{color:#1d4ed8;}

/* TODAY CARD */
.today-card{background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:16px;padding:1.4rem;color:#fff;margin-bottom:12px;}
.today-label{font-size:12px;opacity:.8;margin-bottom:4px;}
.today-amount{font-size:32px;font-weight:700;letter-spacing:-1px;margin-bottom:2px;}
.today-sub{font-size:12px;opacity:.75;}

/* STREAK */
.streak-card{background:#fff;border:0.5px solid #e2e8f0;border-radius:14px;padding:12px 14px;text-align:center;}
.streak-num{font-size:28px;font-weight:700;color:#f97316;}
.streak-label{font-size:12px;color:#64748b;margin-top:2px;}

/* WEEKLY COMPARE */
.week-bar{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.week-label{font-size:12px;color:#64748b;min-width:60px;}
.week-bg{flex:1;background:#f1f5f9;border-radius:99px;height:8px;}
.week-fill{height:8px;border-radius:99px;transition:width .4s;}
.week-val{font-size:12px;font-weight:500;color:#0f172a;min-width:55px;text-align:right;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{gap:6px;background:#f8fafc;border-radius:12px;padding:4px;}
.stTabs [data-baseweb="tab"]{border-radius:8px;padding:7px 14px;font-size:13px;font-weight:500;}
.stTabs [aria-selected="true"]{background:#6366f1!important;color:#fff!important;}

/* ADD FORM */
.add-card{background:#fff;border:0.5px solid #e2e8f0;border-radius:16px;padding:1.4rem;max-width:480px;margin:0 auto;}

@media(max-width:768px){
  .block-container{padding:.5rem .5rem 2rem!important;}
  div[data-testid="metric-container"] div[data-testid="stMetricValue"]{font-size:17px!important;}
  .today-amount{font-size:26px;}
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────
CAT_COLORS = {
    "Food": "#f97316", "Shopping": "#6366f1", "Bills": "#ef4444",
    "Transport": "#0ea5e9", "Grocery": "#22c55e", "Other": "#a855f7"
}
CAT_EMOJI = {
    "Food": "🍔", "Shopping": "🛍️", "Bills": "💡",
    "Transport": "🚌", "Grocery": "🛒", "Other": "📦"
}
CATEGORIES = list(CAT_COLORS.keys())

def cat_color(c): return CAT_COLORS.get(c, "#94a3b8")
def cat_emoji(c): return CAT_EMOJI.get(c, "📦")

# ─────────────────────────────────────────
#  SUPABASE HELPERS
# ─────────────────────────────────────────
def sign_up(email, password, name):
    try:
        r = supabase.auth.sign_up({"email": email, "password": password,
                                    "options": {"data": {"full_name": name}}})
        if r.session:
            st.session_state.access_token = r.session.access_token
            st.session_state.refresh_token = r.session.refresh_token
        return (True, "Account created! Check your email to confirm.") if r.user else (False, "Signup failed.")
    except Exception as e: return False, str(e)

def sign_in(email, password):
    try:
        r = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if r.session:
            st.session_state.access_token = r.session.access_token
            st.session_state.refresh_token = r.session.refresh_token
        return (True, r.user) if r.user else (False, "Invalid email or password.")
    except Exception as e:
        m = str(e)
        if "Invalid login" in m or "invalid_credentials" in m: return False, "Invalid email or password."
        if "Email not confirmed" in m: return False, "Please confirm your email first."
        return False, m

def google_url():
    try:
        r = supabase.auth.sign_in_with_oauth({"provider": "google", "options": {
            "redirect_to": "https://expenses-tracker-plgycyc5g72ujqrvfbchmv.streamlit.app/"}})
        return r.url
    except: return None

def reset_pw(email):
    try:
        supabase.auth.reset_password_email(email, options={
            "redirect_to": "https://expenses-tracker-plgycyc5g72ujqrvfbchmv.streamlit.app/"})
        return True, "Password reset email sent!"
    except Exception as e: return False, str(e)

def save_exp(uid, date_val, desc, amount, cat):
    try:
        supabase.table("expenses").insert({
            "user_id": uid, "date": str(date_val),
            "description": desc, "amount": float(amount), "category": cat
        }).execute()
        return True, ""
    except Exception as e: 
        return False, str(e)

def load_exp(uid):
    try:
        r = supabase.table("expenses").select("*").eq("user_id", uid).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except: return pd.DataFrame()

def delete_exp(exp_id):
    try:
        supabase.table("expenses").delete().eq("id", exp_id).execute()
        return True
    except: return False

def get_budget(uid):
    try:
        r = supabase.table("budgets").select("*").eq("user_id", uid).execute()
        return r.data[0]["amount"] if r.data else 5000
    except: return 5000

def save_budget(uid, amount):
    try:
        existing = supabase.table("budgets").select("*").eq("user_id", uid).execute()
        if existing.data:
            supabase.table("budgets").update({"amount": amount}).eq("user_id", uid).execute()
        else:
            supabase.table("budgets").insert({"user_id": uid, "amount": amount}).execute()
        return True
    except: return False

# ─────────────────────────────────────────
#  SMART ALERT ENGINE
# ─────────────────────────────────────────
def generate_alerts(df, budget):
    alerts = []
    if df.empty:
        return alerts

    today = date.today()
    df["date_only"] = df["date"].dt.date

    # Today's spending
    today_df = df[df["date_only"] == today]
    today_total = today_df["amount"].sum()

    # This week
    week_start = today - timedelta(days=today.weekday())
    this_week_df = df[df["date_only"] >= week_start]
    this_week_total = this_week_df["amount"].sum()

    # Last week
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    last_week_df = df[(df["date_only"] >= last_week_start) & (df["date_only"] <= last_week_end)]
    last_week_total = last_week_df["amount"].sum()

    # This month
    month_df = df[(df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)]
    month_total = month_df["amount"].sum()

    # Days left in month
    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)
    days_left = (next_month - today).days
    days_in_month = (next_month - date(today.year, today.month, 1)).days
    days_passed = days_in_month - days_left
    daily_avg = month_total / max(days_passed, 1)
    projected = daily_avg * days_in_month

    # Budget usage
    budget_pct = (month_total / budget * 100) if budget > 0 else 0

    # ── ALERT 1: Budget critical
    if budget_pct >= 100:
        alerts.append({
            "type": "red", "icon": "🚨",
            "title": "Budget Exceeded!",
            "msg": f"You have spent ₹{month_total:,.0f} — ₹{month_total-budget:,.0f} over your ₹{budget:,.0f} budget this month."
        })
    elif budget_pct >= 85:
        alerts.append({
            "type": "red", "icon": "⚠️",
            "title": "Critical: 85% budget used",
            "msg": f"Only ₹{budget-month_total:,.0f} left for the rest of the month. Avoid non-essential spending."
        })
    elif budget_pct >= 70:
        alerts.append({
            "type": "orange", "icon": "🟡",
            "title": "Budget Warning",
            "msg": f"{budget_pct:.0f}% of monthly budget used with {days_left} days remaining."
        })

    # ── ALERT 2: Weekly spike
    if last_week_total > 0:
        week_change = ((this_week_total - last_week_total) / last_week_total) * 100
        if week_change >= 50:
            alerts.append({
                "type": "red", "icon": "📈",
                "title": f"Spending up {week_change:.0f}% this week",
                "msg": f"This week: ₹{this_week_total:,.0f} vs last week: ₹{last_week_total:,.0f}. Major spike detected."
            })
        elif week_change >= 25:
            alerts.append({
                "type": "orange", "icon": "📊",
                "title": f"Spending up {week_change:.0f}% vs last week",
                "msg": f"This week: ₹{this_week_total:,.0f} vs last week: ₹{last_week_total:,.0f}."
            })
        elif week_change <= -20:
            alerts.append({
                "type": "green", "icon": "📉",
                "title": f"Spending down {abs(week_change):.0f}% this week",
                "msg": f"Great job! ₹{last_week_total - this_week_total:,.0f} less than last week."
            })

    # ── ALERT 3: Projected overspend
    if projected > budget * 1.1 and days_passed >= 5:
        alerts.append({
            "type": "orange", "icon": "🔮",
            "title": "Projected to overspend",
            "msg": f"At current pace you will spend ₹{projected:,.0f} this month — ₹{projected-budget:,.0f} over budget."
        })

    # ── ALERT 4: Category spike
    if not month_df.empty:
        by_cat = month_df.groupby("category")["amount"].sum()
        for cat, amt in by_cat.items():
            pct_of_total = amt / month_total * 100
            if pct_of_total > 60 and amt > 1000:
                alerts.append({
                    "type": "blue", "icon": cat_emoji(cat),
                    "title": f"{cat} is {pct_of_total:.0f}% of spending",
                    "msg": f"₹{amt:,.0f} spent on {cat} this month. Consider balancing your spending."
                })
                break

    # ── ALERT 5: Today high spend
    if today_total > (budget / 30) * 2 and today_total > 0:
        alerts.append({
            "type": "orange", "icon": "📅",
            "title": "High spending today",
            "msg": f"You spent ₹{today_total:,.0f} today — {today_total/(budget/30)*100:.0f}% of your daily average budget."
        })

    # ── POSITIVE: On track
    if budget_pct < 50 and days_passed >= 10:
        alerts.append({
            "type": "green", "icon": "🎯",
            "title": "You are on track!",
            "msg": f"Only {budget_pct:.0f}% of budget used with {days_passed} days passed. Keep it up!"
        })

    return alerts

def render_alert(alert):
    css = {"red": "alert-red", "orange": "alert-orange", "green": "alert-green", "blue": "alert-blue"}
    cls = css.get(alert["type"], "alert-blue")
    st.markdown(f"""
    <div class="alert-card {cls}">
        <div class="alert-icon">{alert["icon"]}</div>
        <div class="alert-body">
            <div class="alert-title">{alert["title"]}</div>
            <div class="alert-msg">{alert["msg"]}</div>
        </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  V3 ADDITIONS (NON-DESTRUCTIVE)
# ─────────────────────────────────────────

def generate_advice(df, budget):
    advice = []
    if df.empty:
        return advice
    today = date.today()
    month_df = df[(df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)]
    total_spend = month_df["amount"].sum()
    if total_spend == 0:
        return advice
    by_cat = month_df.groupby("category")["amount"].sum()
    top_cat = by_cat.idxmax()
    top_amt = by_cat.max()
    top_pct = (top_amt / total_spend) * 100
    remaining = budget - total_spend
    if top_pct > 40:
        advice.append(f"👉 You are spending {top_pct:.0f}% on {top_cat}. Try reducing it by 20% this week.")
    if remaining < 0:
        advice.append("🚨 You are over budget. Avoid non-essential spending for the next few days.")
    elif remaining < budget * 0.2:
        advice.append("⚠️ You are close to budget limit. Spend only on essentials.")
    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)
    days_total = (next_month - date(today.year, today.month, 1)).days
    days_passed = today.day
    remaining_days = max(days_total - days_passed, 1)
    daily_limit = remaining / remaining_days
    if daily_limit > 0:
        advice.append(f"💡 Try to spend less than ₹{daily_limit:.0f}/day to stay on track.")
    return advice

def get_spending_personality(df):
    if df.empty:
        return "No data yet"
    total = df["amount"].sum()
    if total == 0:
        return "No spending yet"
    by_cat = df.groupby("category")["amount"].sum()
    food_pct = by_cat.get("Food", 0) / total * 100
    shopping_pct = by_cat.get("Shopping", 0) / total * 100
    if food_pct > 40:
        return "🍔 Food Lover"
    elif shopping_pct > 40:
        return "🛍️ Shopaholic"
    elif total < 2000:
        return "💰 Saver"
    else:
        return "⚖️ Balanced Spender"

def get_prediction(df):
    if df.empty:
        return 0
    today = date.today()
    month_df = df[(df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)]
    total = month_df["amount"].sum()
    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)
    days_total = (next_month - date(today.year, today.month, 1)).days
    days_passed = today.day
    daily_avg = total / max(days_passed, 1)
    return daily_avg * days_total

# ─────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────
for k, v in {"user": None, "auth_mode": "login", "upload_data": None,
              "auth_msg": None, "auth_type": "info", "chat_history": [], "gemini_api_key": ""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── OAUTH CALLBACK ──
params = st.query_params
if "access_token" in params and st.session_state.user is None:
    try:
        r = supabase.auth.get_user(params["access_token"])
        if r.user:
            st.session_state.user = r.user
            st.session_state.access_token = params["access_token"]
            st.session_state.refresh_token = params.get("refresh_token", "")
            st.query_params.clear()
            st.rerun()
    except: pass

# ─────────────────────────────────────────
#  AUTH PAGE
# ─────────────────────────────────────────
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<div style='padding:2rem 0 .5rem'>", unsafe_allow_html=True)
        st.markdown('<div class="auth-brand">Spend<span>Smart</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Your intelligent expense analytics dashboard</div>', unsafe_allow_html=True)

        if st.session_state.auth_msg:
            t = st.session_state.auth_type
            css = "s-box" if t == "success" else "e-box" if t == "error" else "i-box"
            st.markdown(f'<div class="{css}">{st.session_state.auth_msg}</div>', unsafe_allow_html=True)

        gurl = google_url()
        if gurl:
            st.markdown(f"""<a href="{gurl}" class="google-btn" target="_self">
                <svg width="18" height="18" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>Continue with Google</a>""", unsafe_allow_html=True)

        st.markdown('<div class="divider-or"><span>or</span></div>', unsafe_allow_html=True)
        mode = st.session_state.auth_mode

        if mode == "login":
            st.markdown('<p style="font-size:18px;font-weight:600;color:#0f172a;text-align:center;margin-bottom:1rem;">Sign in</p>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@example.com", key="li_e")
            password = st.text_input("Password", type="password", placeholder="Your password", key="li_p")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Sign In", use_container_width=True, type="primary"):
                    if not email or not password:
                        st.session_state.auth_msg = "Enter email and password."
                        st.session_state.auth_type = "error"; st.rerun()
                    else:
                        ok, res = sign_in(email, password)
                        if ok:
                            st.session_state.user = res; st.session_state.auth_msg = None; st.rerun()
                        else:
                            st.session_state.auth_msg = res; st.session_state.auth_type = "error"; st.rerun()
            with c2:
                if st.button("Forgot password", use_container_width=True):
                    st.session_state.auth_mode = "forgot"; st.session_state.auth_msg = None; st.rerun()
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("Create new account →", use_container_width=True):
                st.session_state.auth_mode = "register"; st.session_state.auth_msg = None; st.rerun()

        elif mode == "register":
            st.markdown('<p style="font-size:18px;font-weight:600;color:#0f172a;text-align:center;margin-bottom:1rem;">Create account</p>', unsafe_allow_html=True)
            name = st.text_input("Full name", placeholder="Narasimha Reddy", key="rn")
            email = st.text_input("Email", placeholder="you@example.com", key="re")
            pw = st.text_input("Password", type="password", placeholder="Min 6 characters", key="rp")
            pw2 = st.text_input("Confirm password", type="password", placeholder="Repeat password", key="rp2")
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not all([name, email, pw, pw2]):
                    st.session_state.auth_msg = "Fill all fields."; st.session_state.auth_type = "error"; st.rerun()
                elif len(pw) < 6:
                    st.session_state.auth_msg = "Password must be 6+ characters."; st.session_state.auth_type = "error"; st.rerun()
                elif pw != pw2:
                    st.session_state.auth_msg = "Passwords do not match."; st.session_state.auth_type = "error"; st.rerun()
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    st.session_state.auth_msg = "Enter a valid email."; st.session_state.auth_type = "error"; st.rerun()
                else:
                    ok, msg = sign_up(email, pw, name)
                    st.session_state.auth_msg = msg
                    st.session_state.auth_type = "success" if ok else "error"
                    if ok: st.session_state.auth_mode = "login"
                    st.rerun()
            if st.button("Already have account → Sign in", use_container_width=True):
                st.session_state.auth_mode = "login"; st.session_state.auth_msg = None; st.rerun()

        elif mode == "forgot":
            st.markdown('<p style="font-size:18px;font-weight:600;color:#0f172a;text-align:center;margin-bottom:1rem;">Reset password</p>', unsafe_allow_html=True)
            st.markdown('<div class="i-box">Enter your email and we will send a reset link.</div>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@example.com", key="fp_e")
            if st.button("Send Reset Link", use_container_width=True, type="primary"):
                if not email:
                    st.session_state.auth_msg = "Enter your email."; st.session_state.auth_type = "error"; st.rerun()
                else:
                    ok, msg = reset_pw(email)
                    st.session_state.auth_msg = msg
                    st.session_state.auth_type = "success" if ok else "error"; st.rerun()
            if st.button("← Back to sign in", use_container_width=True):
                st.session_state.auth_mode = "login"; st.session_state.auth_msg = None; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────
#  LOGGED IN — SETUP
# ─────────────────────────────────────────
user = st.session_state.user
uid = user.id
uemail = user.email
try:
    uname = user.user_metadata.get("full_name") or user.user_metadata.get("name") or uemail.split("@")[0]
except:
    uname = uemail.split("@")[0] if uemail else "User"
first_name = uname.split()[0] if uname else "there"
initials = "".join([w[0].upper() for w in uname.split()[:2]]) if uname else "U"

# Load data
df_db = load_exp(uid)
if st.session_state.upload_data is not None:
    dup = st.session_state.upload_data.copy()
    dup.columns = [c.lower() for c in dup.columns]
    dup["user_id"] = uid
    df_all = pd.concat([dup, df_db], ignore_index=True)
else:
    df_all = df_db

# Clean
if not df_all.empty:
    df_all.columns = [c.lower() for c in df_all.columns]
    df_all["date"] = pd.to_datetime(df_all["date"], errors="coerce")
    df_all = df_all.dropna(subset=["date"])
    df_all["amount"] = pd.to_numeric(df_all["amount"], errors="coerce").fillna(0)
    df_all["category"] = df_all["category"].fillna("Other")
    df_all["date_only"] = df_all["date"].dt.date

budget = get_budget(uid)

# Date helpers
today = date.today()
week_start = today - timedelta(days=today.weekday())
last_week_start = week_start - timedelta(days=7)
last_week_end = week_start - timedelta(days=1)
month_start = date(today.year, today.month, 1)

# ── TOP NAV ──
n1, n2 = st.columns([3, 1])
with n1:
    st.markdown('<span style="font-size:22px;font-weight:700;color:#6366f1;">Spend</span><span style="font-size:22px;font-weight:700;color:#0f172a;">Smart</span>', unsafe_allow_html=True)
with n2:
    st.markdown(f'<div style="text-align:right;padding-top:4px;display:flex;align-items:center;justify-content:flex-end;gap:6px;"><div style="width:28px;height:28px;border-radius:50%;background:#6366f1;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff;">{initials}</div><span style="font-size:12px;color:#64748b;">{first_name}</span></div>', unsafe_allow_html=True)

# ── TABS ──
tab1, tab2, tab_ai, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📊 Analytics", "✨ AI", "➕ Add", "📂 Upload", "⚙️ Settings"])

# ─────────────────────────────────────────
#  TAB 1 — HOME (Today + Alerts + Weekly)
# ─────────────────────────────────────────
with tab1:
    if df_all.empty:
        st.markdown(f'<div class="i-box" style="margin-top:1rem;">Welcome, <b>{first_name}!</b> Go to <b>Add</b> tab to log your first expense.</div>', unsafe_allow_html=True)
    else:
        # ── TODAY CARD ──
        today_total = df_all[df_all["date_only"] == today]["amount"].sum()
        yesterday_total = df_all[df_all["date_only"] == today - timedelta(days=1)]["amount"].sum()
        today_txns = len(df_all[df_all["date_only"] == today])

        st.markdown(f"""
        <div class="today-card">
            <div class="today-label">Today — {today.strftime('%A, %d %b %Y')}</div>
            <div class="today-amount">₹{today_total:,.0f}</div>
            <div class="today-sub">{today_txns} transaction{'s' if today_txns != 1 else ''} today
            {'· ₹' + f'{yesterday_total:,.0f}' + ' yesterday' if yesterday_total > 0 else ''}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── SMART ALERTS ──
        alerts = generate_alerts(df_all, budget)
        if alerts:
            st.markdown('<div class="sh">Smart alerts</div>', unsafe_allow_html=True)
            for alert in alerts[:4]:
                render_alert(alert)

        # ── WEEKLY COMPARISON ──
        st.markdown('<div class="sh">Weekly comparison</div>', unsafe_allow_html=True)
        this_week_total = df_all[df_all["date_only"] >= week_start]["amount"].sum()
        last_week_total = df_all[(df_all["date_only"] >= last_week_start) & (df_all["date_only"] <= last_week_end)]["amount"].sum()
        month_total = df_all[df_all["date_only"] >= month_start]["amount"].sum()

        max_val = max(this_week_total, last_week_total, month_total / 4, 1)

        st.markdown(f"""
        <div class="cc">
            <div class="week-bar">
                <div class="week-label">This week</div>
                <div class="week-bg"><div class="week-fill" style="width:{min(this_week_total/max_val*100,100):.0f}%;background:#6366f1;"></div></div>
                <div class="week-val">₹{this_week_total:,.0f}</div>
            </div>
            <div class="week-bar">
                <div class="week-label">Last week</div>
                <div class="week-bg"><div class="week-fill" style="width:{min(last_week_total/max_val*100,100):.0f}%;background:#94a3b8;"></div></div>
                <div class="week-val">₹{last_week_total:,.0f}</div>
            </div>
            <div class="week-bar">
                <div class="week-label">This month</div>
                <div class="week-bg"><div class="week-fill" style="width:{min(month_total/max_val*100,100):.0f}%;background:#22c55e;"></div></div>
                <div class="week-val">₹{month_total:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── LAST 7 DAYS TREND ──
        st.markdown('<div class="sh">Last 7 days</div>', unsafe_allow_html=True)
        last7 = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        last7_amounts = [df_all[df_all["date_only"] == d]["amount"].sum() for d in last7]

        fig, ax = plt.subplots(figsize=(6, 2.8))
        colors_bar = ["#6366f1" if d == today else "#c7d2fe" for d in last7]
        ax.bar([d.strftime("%a") for d in last7], last7_amounts, color=colors_bar, width=0.6, edgecolor="white", linewidth=1)
        ax.set_facecolor("#f8fafc"); fig.patch.set_facecolor("#f8fafc")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#e2e8f0")
        ax.tick_params(axis="x", labelsize=10, colors="#334155")
        ax.tick_params(axis="y", labelsize=9, colors="#94a3b8")
        ax.yaxis.grid(True, linestyle="--", alpha=0.4, color="#e2e8f0")
        for i, (bar, val) in enumerate(zip(ax.patches, last7_amounts)):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(last7_amounts) * 0.02,
                        f"₹{val:,.0f}", ha="center", va="bottom", fontsize=7.5, color="#334155", fontweight="600")
        plt.tight_layout()
        st.markdown('<div class="cc">', unsafe_allow_html=True)
        st.pyplot(fig); plt.close()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── RECENT TRANSACTIONS ──
        st.markdown('<div class="sh">Recent transactions</div>', unsafe_allow_html=True)
        recent = df_all.sort_values("date", ascending=False).head(5)
        for _, row in recent.iterrows():
            emoji = cat_emoji(str(row.get("category", "Other")))
            color = cat_color(str(row.get("category", "Other")))
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:9px 12px;background:#fff;border:0.5px solid #e2e8f0;border-radius:10px;margin-bottom:6px;">
                <div style="width:34px;height:34px;border-radius:10px;background:{color}22;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">{emoji}</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:13px;font-weight:500;color:#0f172a;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{row.get('description','')}</div>
                    <div style="font-size:11px;color:#94a3b8;">{row['date'].strftime('%d %b') if pd.notna(row['date']) else ''} · {row.get('category','')}</div>
                </div>
                <div style="font-size:14px;font-weight:600;color:#0f172a;flex-shrink:0;">₹{row.get('amount',0):,.0f}</div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  TAB 2 — ANALYTICS
# ─────────────────────────────────────────
with tab2:
    if df_all.empty:
        st.markdown('<div class="i-box" style="margin-top:1rem;">No data yet. Add expenses to see analytics.</div>', unsafe_allow_html=True)
    else:
        df_all["month"] = df_all["date"].dt.to_period("M").astype(str)
        months = sorted(df_all["month"].unique(), reverse=True)
        sel = st.selectbox("Month", months, label_visibility="collapsed",
                           format_func=lambda m: datetime.strptime(m, "%Y-%m").strftime("%B %Y"))
        df_f = df_all[df_all["month"] == sel]

        total = df_f["amount"].sum()
        by_cat = df_f.groupby("category")["amount"].sum().sort_values(ascending=False)
        top_cat = by_cat.idxmax() if not by_cat.empty else "—"
        top_amt = by_cat.max() if not by_cat.empty else 0
        avg_txn = df_f["amount"].mean() if not df_f.empty else 0
        n_txn = len(df_f)
        remaining = budget - total
        pct = min(total / budget * 100, 100) if budget > 0 else 0

        # KPIs
        st.markdown('<div class="sh">Overview</div>', unsafe_allow_html=True)
        k1, k2 = st.columns(2)
        k3, k4 = st.columns(2)
        k1.metric("Total spent", f"₹{total:,.0f}", f"₹{remaining:,.0f} left" if remaining >= 0 else f"₹{abs(remaining):,.0f} over", delta_color="normal" if remaining >= 0 else "inverse")
        k2.metric("Transactions", n_txn)
        k3.metric("Avg per transaction", f"₹{avg_txn:,.0f}")
        k4.metric("Top category", top_cat, f"₹{top_amt:,.0f}")

        # Budget
        bc = "#ef4444" if pct >= 100 else "#f97316" if pct >= 75 else "#6366f1"
        al = f'<div class="a3">⚠️ Over budget by ₹{abs(remaining):,.0f}</div>' if remaining < 0 \
            else f'<div class="a2">🟡 {pct:.0f}% used</div>' if pct >= 75 \
            else f'<div class="a1">✅ On track — ₹{remaining:,.0f} left</div>'
        st.markdown(f'<div class="bw"><div class="bl">₹{total:,.0f} of ₹{budget:,.0f} ({pct:.0f}%)</div><div class="bb"><div class="bf" style="width:{pct}%;background:{bc};"></div></div></div>{al}', unsafe_allow_html=True)

        # Category breakdown
        if not by_cat.empty:
            st.markdown('<div class="sh">Category breakdown</div>', unsafe_allow_html=True)
            for cat, amt in by_cat.items():
                pct_cat = amt / total * 100
                color = cat_color(cat)
                emoji = cat_emoji(cat)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                    <div style="font-size:16px;width:24px;text-align:center;">{emoji}</div>
                    <div style="flex:1;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                            <span style="font-size:13px;font-weight:500;color:#0f172a;">{cat}</span>
                            <span style="font-size:13px;font-weight:600;color:#0f172a;">₹{amt:,.0f} <span style="font-weight:400;color:#94a3b8;font-size:11px;">({pct_cat:.0f}%)</span></span>
                        </div>
                        <div style="background:#f1f5f9;border-radius:99px;height:6px;">
                            <div style="width:{pct_cat}%;height:6px;border-radius:99px;background:{color};"></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

        # Charts
        st.markdown('<div class="sh">Charts</div>', unsafe_allow_html=True)
        if not by_cat.empty:
            fig, ax = plt.subplots(figsize=(6, 3.5))
            cols = [cat_color(c) for c in by_cat.index]
            bars = ax.bar(by_cat.index, by_cat.values, color=cols, edgecolor="white", linewidth=1.5, width=0.55)
            ax.set_facecolor("#f8fafc"); fig.patch.set_facecolor("#f8fafc")
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.spines["bottom"].set_color("#e2e8f0")
            ax.tick_params(axis="x", rotation=30, labelsize=10, colors="#334155")
            ax.tick_params(axis="y", labelsize=9, colors="#94a3b8")
            ax.yaxis.grid(True, linestyle="--", alpha=0.5, color="#e2e8f0")
            for bar, val in zip(bars, by_cat.values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                        f"₹{val:,.0f}", ha="center", va="bottom", fontsize=8, color="#334155", fontweight="600")
            ax.set_title("Spending by category", fontsize=12, fontweight="600", color="#0f172a", pad=10)
            plt.tight_layout()
            st.markdown('<div class="cc">', unsafe_allow_html=True)
            st.pyplot(fig); plt.close()
            st.markdown("</div>", unsafe_allow_html=True)

        # Daily trend
        st.markdown('<div class="sh">Daily trend</div>', unsafe_allow_html=True)
        daily = df_f.groupby(df_f["date"].dt.date)["amount"].sum().reset_index()
        daily.columns = ["date", "amount"]
        if not daily.empty:
            fig3, ax3 = plt.subplots(figsize=(6, 2.8))
            ax3.fill_between(daily["date"], daily["amount"], alpha=0.12, color="#6366f1")
            ax3.plot(daily["date"], daily["amount"], color="#6366f1", linewidth=2.5, marker="o", markersize=4)
            ax3.set_facecolor("#f8fafc"); fig3.patch.set_facecolor("#f8fafc")
            ax3.spines[["top", "right", "left"]].set_visible(False)
            ax3.spines["bottom"].set_color("#e2e8f0")
            ax3.tick_params(axis="x", labelsize=8, colors="#94a3b8", rotation=30)
            ax3.tick_params(axis="y", labelsize=8, colors="#94a3b8")
            ax3.yaxis.grid(True, linestyle="--", alpha=0.4, color="#e2e8f0")
            plt.tight_layout()
            st.markdown('<div class="cc">', unsafe_allow_html=True)
            st.pyplot(fig3); plt.close()
            st.markdown("</div>", unsafe_allow_html=True)

        # Transactions table
        st.markdown('<div class="sh">All transactions</div>', unsafe_allow_html=True)
        disp = df_f[["date", "description", "category", "amount"]].copy()
        disp.columns = ["Date", "Description", "Category", "Amount (₹)"]
        disp["Date"] = disp["Date"].dt.strftime("%d %b %Y")
        disp = disp.sort_values("Date", ascending=False)
        st.dataframe(disp, use_container_width=True, hide_index=True,
                     column_config={"Amount (₹)": st.column_config.NumberColumn(format="₹%.0f"),
                                    "Date": st.column_config.TextColumn(width="small"),
                                    "Category": st.column_config.TextColumn(width="small")})

        # Export
        d1, d2 = st.columns(2)
        report = f"SpendSmart Report\n{datetime.strptime(sel,'%Y-%m').strftime('%B %Y')}\nTotal: ₹{total:,.0f}\n\n{by_cat.to_string()}"
        with d1: st.download_button("📥 Report", report, f"report_{sel}.txt", use_container_width=True)
        with d2: st.download_button("📊 CSV", disp.to_csv(index=False), f"expenses_{sel}.csv", use_container_width=True)

# ─────────────────────────────────────────
#  TAB AI — ASSISTANT
# ─────────────────────────────────────────
with tab_ai:
    st.markdown('<div class="sh">✨ AI Financial Advisor</div>', unsafe_allow_html=True)
    
    api_key = st.secrets.get("GEMINI_API_KEY") or st.session_state.get("gemini_api_key")
    
    if not api_key:
        st.markdown('<div class="w-box">⚠️ Please configure your <b>Gemini API Key</b> in the Settings tab to use the AI Assistant.</div>', unsafe_allow_html=True)
    else:
        client = genai.Client(api_key=api_key)
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask about your expenses (e.g., 'How can I save money this month?'):"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                try:
                    # Construct context
                    context = f"User: {first_name}\nMonthly Budget: ₹{budget:,.0f}\n"
                    if not df_all.empty:
                        # Focus on this month for better context
                        today_d = date.today()
                        month_df = df_all[(df_all["date"].dt.month == today_d.month) & (df_all["date"].dt.year == today_d.year)]
                        
                        total_spent = month_df['amount'].sum()
                        by_cat = month_df.groupby('category')['amount'].sum()
                        context += f"Total Spent This Month: ₹{total_spent:,.0f}\nCategory Breakdown This Month:\n"
                        for cat, amt in by_cat.items():
                            context += f"- {cat}: ₹{amt:,.0f}\n"
                    else:
                        context += "The user has no expenses recorded yet.\n"
                    
                    sys_prompt = "You are a helpful, professional, and concise financial advisor for the SpendSmart app. Answer the user's questions based on their spending data provided below:\n\n" + context
                    
                    contents = []
                    for msg in st.session_state.chat_history[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
                    
                    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))
                    
                    # Automatic model fallback to prevent 404 or 429 quota limits
                    models_to_try = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-flash-latest", "gemini-3.1-flash-lite-preview", "gemini-flash-lite-latest"]
                    response = None
                    last_error = None
                    
                    for model_name in models_to_try:
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=contents,
                                config=types.GenerateContentConfig(
                                    system_instruction=sys_prompt,
                                )
                            )
                            break # Success!
                        except Exception as e:
                            last_error = e
                            continue
                    
                    if response is None:
                        # Fetch available models for debugging
                        available_models = []
                        try:
                            for m in client.models.list():
                                available_models.append(m.name)
                        except: pass
                        error_msg = str(last_error)
                        if available_models:
                            error_msg += f"\n\nAvailable models for your API key: {', '.join(available_models)}"
                        raise Exception(error_msg)
                    
                    message_placeholder.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    message_placeholder.markdown(f"❌ Error communicating with AI: {str(e)}")
                    st.session_state.chat_history.pop() # Remove failed user message

# ─────────────────────────────────────────
#  TAB 3 — ADD EXPENSE
# ─────────────────────────────────────────
with tab3:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.subheader("Add New Expense")

    with st.container(border=True):
        e_date = st.date_input("Date", value=datetime.today(), key="t3_date")
        e_desc = st.text_input("Description", placeholder="e.g. Swiggy, Amazon, Electricity bill", key="t3_desc")
        e_amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, key="t3_amt")
        e_cat = st.selectbox("Category", CATEGORIES, key="t3_cat")

        if st.button("Add Expense", use_container_width=True, type="primary", key="t3_add"):
            if not e_desc:
                st.error("Please enter a description.")
            elif e_amount <= 0:
                st.error("Please enter an amount greater than 0.")
            else:
                success, err_msg = save_exp(uid, e_date, e_desc, e_amount, e_cat)
                if success:
                    st.success("✅ Expense saved!")
                    st.balloons()
                else:
                    st.error(f"Failed to save: {err_msg}")

    # Quick category guide
    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sh">Quick categories</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for i, (cat, emoji) in enumerate(CAT_EMOJI.items()):
        col = [c1, c2, c3][i % 3]
        col.markdown(f'<div style="background:{cat_color(cat)}18;border:1px solid {cat_color(cat)}33;border-radius:10px;padding:8px;text-align:center;font-size:12px;font-weight:500;color:{cat_color(cat)};margin-bottom:6px;">{emoji} {cat}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
#  TAB 4 — UPLOAD CSV
# ─────────────────────────────────────────
with tab4:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="i-box">CSV must have columns: <b>Date, Description, Amount, Category</b></div>', unsafe_allow_html=True)
    uf = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed", key="t4_upload")
    if uf:
        try:
            df_up = pd.read_csv(uf)
            st.session_state.upload_data = df_up
            st.markdown(f'<div class="s-box">✅ Uploaded {len(df_up)} rows. Go to Analytics tab to see data.</div>', unsafe_allow_html=True)
            st.dataframe(df_up.head(5), use_container_width=True, hide_index=True)
        except Exception as e:
            st.markdown(f'<div class="e-box">Error: {str(e)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sh">Sample CSV format</div>', unsafe_allow_html=True)
    sample = pd.DataFrame({
        "Date": ["2026-04-01", "2026-04-02", "2026-04-03"],
        "Description": ["Swiggy", "Amazon", "Electricity"],
        "Amount": [250, 1200, 800],
        "Category": ["Food", "Shopping", "Bills"]
    })
    st.dataframe(sample, use_container_width=True, hide_index=True)
    st.download_button("📥 Download sample CSV", sample.to_csv(index=False), "sample_expenses.csv", use_container_width=True)

# ─────────────────────────────────────────
#  TAB 5 — SETTINGS
# ─────────────────────────────────────────
with tab5:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="sh">AI Settings</div>', unsafe_allow_html=True)
    api_key_input = st.text_input("Gemini API Key", type="password", value=st.session_state.gemini_api_key, placeholder="Enter your Google AI Studio API Key", help="Get your API key from Google AI Studio (aistudio.google.com)")
    if st.button("Save API Key", use_container_width=True, key="save_api_key"):
        st.session_state.gemini_api_key = api_key_input
        st.markdown('<div class="s-box">✅ API Key saved for this session!</div>', unsafe_allow_html=True)
        st.rerun()


    st.markdown('<div class="sh">Monthly budget</div>', unsafe_allow_html=True)
    new_budget = st.number_input("Set your monthly budget (₹)", min_value=0, value=int(budget), step=500, key="set_budget")
    if st.button("Save Budget", use_container_width=True, type="primary"):
        if save_budget(uid, new_budget):
            st.markdown('<div class="s-box">✅ Budget updated!</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.markdown('<div class="e-box">Failed to save. Check Supabase budgets table exists.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sh">Account</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cc"><div style="font-size:13px;color:#64748b;margin-bottom:3px;">Logged in as</div><div style="font-size:15px;font-weight:500;color:#0f172a;">{uname}</div><div style="font-size:12px;color:#94a3b8;">{uemail}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh">About</div>', unsafe_allow_html=True)
    st.markdown('<div class="cc"><div style="font-size:13px;color:#334155;line-height:1.8;"><b style="color:#0f172a;">SpendSmart v2.0</b> — Smart Expense Intelligence<br>Python · Streamlit · Supabase · Pandas<br>github.com/nreddie7702/expense-tracker</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        try: supabase.auth.sign_out()
        except: pass
        st.session_state.user = None
        st.session_state.upload_data = None
        st.session_state.auth_mode = "login"
        st.session_state.auth_msg = None
        st.rerun()

st.markdown("---")
st.caption(f"SpendSmart v2.0 · Smart Expense Intelligence · {uemail}")