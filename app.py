import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client, Client
from datetime import datetime
import re

st.set_page_config(page_title="SpendSmart", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1rem!important;padding-bottom:2rem;padding-left:1rem!important;padding-right:1rem!important;}

/* ── AUTH ── */
.auth-brand{font-size:30px;font-weight:700;color:#6366f1;text-align:center;margin-bottom:4px;letter-spacing:-1px;}
.auth-brand span{color:#0f172a;}
.auth-sub{font-size:14px;color:#64748b;text-align:center;margin-bottom:1.6rem;}
.auth-title{font-size:18px;font-weight:600;color:#0f172a;text-align:center;margin-bottom:1.2rem;}
.divider-or{display:flex;align-items:center;gap:10px;margin:1rem 0;}
.divider-or::before,.divider-or::after{content:'';flex:1;height:1px;background:#e2e8f0;}
.divider-or span{font-size:12px;color:#94a3b8;}
.google-btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:12px 16px;border:1.5px solid #e2e8f0;border-radius:12px;background:#fff;cursor:pointer;font-size:14px;font-weight:500;color:#0f172a;transition:all .2s;text-decoration:none;margin-bottom:4px;}
.google-btn:hover{background:#f8fafc;border-color:#cbd5e1;}
.e-box{background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:10px 14px;color:#991b1b;font-size:13px;margin-bottom:10px;}
.s-box{background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:10px 14px;color:#166534;font-size:13px;margin-bottom:10px;}
.i-box{background:#eff6ff;border:1px solid #93c5fd;border-radius:10px;padding:10px 14px;color:#1e40af;font-size:13px;margin-bottom:10px;}

/* ── METRICS ── */
div[data-testid="metric-container"]{background:#fff;border:0.5px solid #e2e8f0;border-radius:14px;padding:12px 14px;box-shadow:0 1px 4px rgba(0,0,0,.05);}
div[data-testid="metric-container"] label{color:#64748b!important;font-size:11px!important;font-weight:500;}
div[data-testid="metric-container"] div[data-testid="stMetricValue"]{color:#0f172a!important;font-size:20px!important;font-weight:700;}

/* ── SECTION HEADERS ── */
.sh{font-size:14px;font-weight:600;color:#0f172a;border-left:3px solid #6366f1;padding-left:8px;margin:16px 0 10px;}

/* ── CARDS ── */
.cc{background:#fff;border:0.5px solid #e2e8f0;border-radius:14px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.04);margin-bottom:12px;}

/* ── BUDGET BAR ── */
.bw{background:#f1f5f9;border-radius:10px;padding:12px 14px;margin-bottom:8px;}
.bl{font-size:12px;color:#64748b;margin-bottom:6px;}
.bb{background:#e2e8f0;border-radius:99px;height:9px;}
.bf{height:9px;border-radius:99px;}

/* ── ALERTS ── */
.a1{background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:9px 12px;color:#166534;font-size:13px;margin-top:6px;}
.a2{background:#fff7ed;border:1px solid #fdba74;border-radius:8px;padding:9px 12px;color:#9a3412;font-size:13px;margin-top:6px;}
.a3{background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:9px 12px;color:#991b1b;font-size:13px;margin-top:6px;}

/* ── INSIGHT CARDS ── */
.ic{background:#f8fafc;border:0.5px solid #e2e8f0;border-radius:10px;padding:10px 12px;font-size:13px;color:#334155;line-height:1.55;margin-bottom:8px;}
.ic b{color:#0f172a;}

/* ── ADD EXPENSE CARD ── */
.add-card{background:#fff;border:0.5px solid #e2e8f0;border-radius:16px;padding:1.4rem;box-shadow:0 2px 8px rgba(0,0,0,.06);max-width:500px;margin:0 auto;}
.add-title{font-size:18px;font-weight:600;color:#0f172a;margin-bottom:1.2rem;text-align:center;}

/* ── TOP NAV ── */
.top-nav{display:flex;justify-content:space-between;align-items:center;padding:8px 0 12px;border-bottom:1px solid #e2e8f0;margin-bottom:12px;}
.nav-brand{font-size:20px;font-weight:700;}
.nav-brand span:first-child{color:#6366f1;}
.nav-brand span:last-child{color:#0f172a;}
.nav-user{font-size:12px;color:#64748b;}

/* ── TAB STYLING ── */
.stTabs [data-baseweb="tab-list"]{gap:8px;background:#f8fafc;border-radius:12px;padding:4px;}
.stTabs [data-baseweb="tab"]{border-radius:8px;padding:8px 16px;font-size:13px;font-weight:500;}
.stTabs [aria-selected="true"]{background:#6366f1!important;color:#fff!important;}

/* ── UPLOAD ZONE ── */
.upload-zone{background:#f8fafc;border:2px dashed #cbd5e1;border-radius:12px;padding:1.5rem;text-align:center;color:#64748b;font-size:13px;margin-bottom:12px;}

/* ── MOBILE OPTIMISE ── */
@media(max-width:768px){
  .block-container{padding-left:.5rem!important;padding-right:.5rem!important;}
  div[data-testid="metric-container"] div[data-testid="stMetricValue"]{font-size:17px!important;}
  .add-card{padding:1rem;}
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for k,v in {"user":None,"auth_mode":"login","upload_data":None,"auth_msg":None,"auth_type":"info","access_token":None}.items():
    if k not in st.session_state:
        st.session_state[k]=v

CAT_COLORS={"Food":"#f97316","Shopping":"#6366f1","Bills":"#ef4444","Transport":"#0ea5e9","Grocery":"#22c55e","Other":"#a855f7"}
CATEGORIES=list(CAT_COLORS.keys())

def cat_color(c): return CAT_COLORS.get(c,"#94a3b8")

# ── SUPABASE HELPERS ──
def sign_up(email,password,name):
    try:
        r=supabase.auth.sign_up({"email":email,"password":password,"options":{"data":{"full_name":name}}})
        return (True,"Account created! Check your email to confirm.") if r.user else (False,"Signup failed.")
    except Exception as e: return False,str(e)

def sign_in(email,password):
    try:
        r=supabase.auth.sign_in_with_password({"email":email,"password":password})
        if r.user:
            if r.session: st.session_state.access_token=r.session.access_token
            return True,r.user
        return False,"Invalid email or password."
    except Exception as e:
        m=str(e)
        if "Invalid login" in m or "invalid_credentials" in m: return False,"Invalid email or password."
        if "Email not confirmed" in m: return False,"Please confirm your email first."
        return False,m

def google_url():
    try:
        r=supabase.auth.sign_in_with_oauth({"provider":"google","options":{"redirect_to":"https://expenses-tracker-plgycyc5g72ujqrvfbchmv.streamlit.app/"}})
        return r.url
    except: return None

def reset_pw(email):
    try:
        supabase.auth.reset_password_email(email,options={"redirect_to":"https://expenses-tracker-plgycyc5g72ujqrvfbchmv.streamlit.app/"})
        return True,"Password reset email sent!"
    except Exception as e: return False,str(e)

def _set_token():
    tok=st.session_state.get("access_token")
    if tok: supabase.postgrest.auth(tok)

def save_exp(uid,date,desc,amount,cat):
    try:
        _set_token()
        supabase.table("expenses").insert({"user_id":uid,"date":str(date),"description":desc,"amount":float(amount),"category":cat}).execute()
        return True
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

def load_exp(uid):
    try:
        _set_token()
        r=supabase.table("expenses").select("*").eq("user_id",uid).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Load error: {e}")
        return pd.DataFrame()

# ── OAUTH CALLBACK ──
params=st.query_params
if "access_token" in params and st.session_state.user is None:
    try:
        tok=params["access_token"]
        r=supabase.auth.get_user(tok)
        if r.user:
            st.session_state.user=r.user
            st.session_state.access_token=tok
            st.query_params.clear()
            st.rerun()
    except: pass

# ────────────────────────────────────────
#  AUTH PAGE
# ────────────────────────────────────────
if st.session_state.user is None:
    _,col,_=st.columns([1,1.4,1])
    with col:
        st.markdown("<div style='padding:1.5rem 0 .5rem'>",unsafe_allow_html=True)
        st.markdown('<div class="auth-brand">Spend<span>Smart</span></div>',unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Your intelligent expense analytics dashboard</div>',unsafe_allow_html=True)

        if st.session_state.auth_msg:
            t=st.session_state.auth_type
            css="s-box" if t=="success" else "e-box" if t=="error" else "i-box"
            st.markdown(f'<div class="{css}">{st.session_state.auth_msg}</div>',unsafe_allow_html=True)

        gurl=google_url()
        if gurl:
            st.markdown(f"""<a href="{gurl}" class="google-btn" target="_self">
                <svg width="18" height="18" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>Continue with Google</a>""",unsafe_allow_html=True)

        st.markdown('<div class="divider-or"><span>or</span></div>',unsafe_allow_html=True)
        mode=st.session_state.auth_mode

        if mode=="login":
            st.markdown('<div class="auth-title">Sign in</div>',unsafe_allow_html=True)
            email=st.text_input("Email",placeholder="you@example.com",key="li_e")
            password=st.text_input("Password",type="password",placeholder="Your password",key="li_p")
            c1,c2=st.columns(2)
            with c1:
                if st.button("Sign In",use_container_width=True,type="primary"):
                    if not email or not password:
                        st.session_state.auth_msg="Enter email and password.";st.session_state.auth_type="error";st.rerun()
                    else:
                        ok,res=sign_in(email,password)
                        if ok:
                            st.session_state.user=res;st.session_state.auth_msg=None;st.rerun()
                        else:
                            st.session_state.auth_msg=res;st.session_state.auth_type="error";st.rerun()
            with c2:
                if st.button("Forgot password",use_container_width=True):
                    st.session_state.auth_mode="forgot";st.session_state.auth_msg=None;st.rerun()
            st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
            if st.button("Create new account →",use_container_width=True):
                st.session_state.auth_mode="register";st.session_state.auth_msg=None;st.rerun()

        elif mode=="register":
            st.markdown('<div class="auth-title">Create account</div>',unsafe_allow_html=True)
            name=st.text_input("Full name",placeholder="Narasimha Reddy",key="rn")
            email=st.text_input("Email",placeholder="you@example.com",key="re")
            pw=st.text_input("Password",type="password",placeholder="Min 6 characters",key="rp")
            pw2=st.text_input("Confirm password",type="password",placeholder="Repeat password",key="rp2")
            if st.button("Create Account",use_container_width=True,type="primary"):
                if not all([name,email,pw,pw2]):
                    st.session_state.auth_msg="Fill all fields.";st.session_state.auth_type="error";st.rerun()
                elif len(pw)<6:
                    st.session_state.auth_msg="Password must be 6+ characters.";st.session_state.auth_type="error";st.rerun()
                elif pw!=pw2:
                    st.session_state.auth_msg="Passwords do not match.";st.session_state.auth_type="error";st.rerun()
                elif not re.match(r"[^@]+@[^@]+\.[^@]+",email):
                    st.session_state.auth_msg="Enter a valid email.";st.session_state.auth_type="error";st.rerun()
                else:
                    ok,msg=sign_up(email,pw,name)
                    st.session_state.auth_msg=msg;st.session_state.auth_type="success" if ok else "error"
                    if ok: st.session_state.auth_mode="login"
                    st.rerun()
            if st.button("Already have account → Sign in",use_container_width=True):
                st.session_state.auth_mode="login";st.session_state.auth_msg=None;st.rerun()

        elif mode=="forgot":
            st.markdown('<div class="auth-title">Reset password</div>',unsafe_allow_html=True)
            st.markdown('<div class="i-box">Enter your email and we will send a reset link.</div>',unsafe_allow_html=True)
            email=st.text_input("Email",placeholder="you@example.com",key="fp_e")
            if st.button("Send Reset Link",use_container_width=True,type="primary"):
                if not email:
                    st.session_state.auth_msg="Enter your email.";st.session_state.auth_type="error";st.rerun()
                else:
                    ok,msg=reset_pw(email)
                    st.session_state.auth_msg=msg;st.session_state.auth_type="success" if ok else "error";st.rerun()
            if st.button("← Back to sign in",use_container_width=True):
                st.session_state.auth_mode="login";st.session_state.auth_msg=None;st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    st.stop()

# ────────────────────────────────────────
#  DASHBOARD
# ────────────────────────────────────────
user=st.session_state.user
uid=user.id
uemail=user.email
try: uname=user.user_metadata.get("full_name") or user.user_metadata.get("name") or uemail.split("@")[0]
except: uname=uemail.split("@")[0] if uemail else "User"
initials="".join([w[0].upper() for w in uname.split()[:2]]) if uname else "U"

# ── TOP NAV ──
n1,n2=st.columns([3,1])
with n1:
    st.markdown('<span style="font-size:22px;font-weight:700;color:#6366f1;">Spend</span><span style="font-size:22px;font-weight:700;color:#0f172a;">Smart</span>',unsafe_allow_html=True)
with n2:
    st.markdown(f'<div style="text-align:right;padding-top:4px;"><div style="display:inline-flex;align-items:center;gap:6px;"><div style="width:28px;height:28px;border-radius:50%;background:#6366f1;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff;">{initials}</div><span style="font-size:12px;color:#64748b;">{uname.split()[0]}</span></div></div>',unsafe_allow_html=True)

st.markdown("<div style='height:4px'></div>",unsafe_allow_html=True)

# ── MAIN TABS ──
tab1,tab2,tab3,tab4=st.tabs(["📊 Dashboard","➕ Add Expense","📂 Upload CSV","⚙️ Settings"])

# ────────────────────────────────────────
#  TAB 1 — DASHBOARD
# ────────────────────────────────────────
with tab1:
    df_db=load_exp(uid)
    if st.session_state.upload_data is not None:
        dup=st.session_state.upload_data.copy()
        dup.columns=[c.lower() for c in dup.columns]
        dup["user_id"]=uid
        df=pd.concat([dup,df_db],ignore_index=True)
    else:
        df=df_db

    if df.empty:
        st.markdown('<div class="i-box" style="margin-top:1rem;">No expenses yet. Go to <b>Add Expense</b> tab to add your first expense, or <b>Upload CSV</b> to import data.</div>',unsafe_allow_html=True)
        st.stop()

    df.columns=[c.lower() for c in df.columns]
    df["date"]=pd.to_datetime(df["date"],errors="coerce")
    df=df.dropna(subset=["date"])
    df["amount"]=pd.to_numeric(df["amount"],errors="coerce").fillna(0)
    df["month"]=df["date"].dt.to_period("M").astype(str)
    df["category"]=df["category"].fillna("Other")

    months=sorted(df["month"].unique(),reverse=True)
    sel=st.selectbox("Month",months,label_visibility="collapsed",
                     format_func=lambda m:datetime.strptime(m,"%Y-%m").strftime("%B %Y"))
    df_f=df[df["month"]==sel]

    total=df_f["amount"].sum()
    by_cat=df_f.groupby("category")["amount"].sum()
    top_cat=by_cat.idxmax() if not by_cat.empty else "—"
    top_amt=by_cat.max() if not by_cat.empty else 0
    avg_txn=df_f["amount"].mean() if not df_f.empty else 0
    n_txn=len(df_f)
    budget=5000
    remaining=budget-total
    pct=min(total/budget*100,100) if budget>0 else 0

    st.markdown('<div class="sh">Overview</div>',unsafe_allow_html=True)
    k1,k2=st.columns(2)
    k3,k4=st.columns(2)
    k1.metric("Total spent",f"₹{total:,.0f}",f"₹{remaining:,.0f} left" if remaining>=0 else f"₹{abs(remaining):,.0f} over",delta_color="normal" if remaining>=0 else "inverse")
    k2.metric("Transactions",n_txn)
    k3.metric("Avg per transaction",f"₹{avg_txn:,.0f}")
    k4.metric("Top category",top_cat,f"₹{top_amt:,.0f}")

    st.markdown('<div class="sh">Budget</div>',unsafe_allow_html=True)
    bc="#ef4444" if pct>=100 else "#f97316" if pct>=75 else "#6366f1"
    al=f'<div class="a3">⚠️ Over budget by ₹{abs(remaining):,.0f}</div>' if remaining<0 else f'<div class="a2">🟡 {pct:.0f}% used — watch spending</div>' if pct>=75 else f'<div class="a1">✅ On track — ₹{remaining:,.0f} left</div>'
    st.markdown(f'<div class="bw"><div class="bl">₹{total:,.0f} of ₹{budget:,.0f} ({pct:.0f}%)</div><div class="bb"><div class="bf" style="width:{pct}%;background:{bc};"></div></div></div>{al}',unsafe_allow_html=True)

    if not by_cat.empty:
        st.markdown('<div class="sh">Charts</div>',unsafe_allow_html=True)
        fig,ax=plt.subplots(figsize=(6,3.5))
        cols=[cat_color(c) for c in by_cat.index]
        bars=ax.bar(by_cat.index,by_cat.values,color=cols,edgecolor="white",linewidth=1.5,width=0.55)
        ax.set_facecolor("#f8fafc");fig.patch.set_facecolor("#f8fafc")
        ax.spines[["top","right","left"]].set_visible(False);ax.spines["bottom"].set_color("#e2e8f0")
        ax.tick_params(axis="x",rotation=30,labelsize=10,colors="#334155")
        ax.tick_params(axis="y",labelsize=9,colors="#94a3b8")
        ax.yaxis.grid(True,linestyle="--",alpha=0.5,color="#e2e8f0")
        for bar,val in zip(bars,by_cat.values):
            ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+20,f"₹{val:,.0f}",ha="center",va="bottom",fontsize=8,color="#334155",fontweight="600")
        ax.set_title("Spending by category",fontsize=12,fontweight="600",color="#0f172a",pad=10)
        plt.tight_layout()
        st.markdown('<div class="cc">',unsafe_allow_html=True)
        st.pyplot(fig);plt.close()
        st.markdown("</div>",unsafe_allow_html=True)

        fig2,ax2=plt.subplots(figsize=(6,3.5))
        cols2=[cat_color(c) for c in by_cat.index]
        wedges,_,autotexts=ax2.pie(by_cat.values,labels=None,autopct="%1.1f%%",colors=cols2,startangle=140,wedgeprops=dict(edgecolor="white",linewidth=2),pctdistance=0.75)
        for at in autotexts: at.set_fontsize(9);at.set_color("white");at.set_fontweight("bold")
        ax2.legend(wedges,by_cat.index,loc="lower center",bbox_to_anchor=(0.5,-0.15),ncol=3,fontsize=9,frameon=False)
        ax2.add_patch(plt.Circle((0,0),0.55,color="#f8fafc"))
        ax2.text(0,0.1,"Total",ha="center",fontsize=9,color="#94a3b8")
        ax2.text(0,-0.15,f"₹{total:,.0f}",ha="center",fontsize=13,fontweight="700",color="#0f172a")
        fig2.patch.set_facecolor("#f8fafc");ax2.set_facecolor("#f8fafc")
        ax2.set_title("Category breakdown",fontsize=12,fontweight="600",color="#0f172a",pad=10)
        plt.tight_layout()
        st.markdown('<div class="cc">',unsafe_allow_html=True)
        st.pyplot(fig2);plt.close()
        st.markdown("</div>",unsafe_allow_html=True)

    st.markdown('<div class="sh">Smart insights</div>',unsafe_allow_html=True)
    ins=[]
    if not by_cat.empty:
        ins.append(f'<div class="ic">📊 Highest: <b>{top_cat}</b> at <b>₹{top_amt:,.0f}</b> — {top_amt/total*100:.0f}% of spend.</div>')
    if pct>=90: ins.append(f'<div class="ic">🔴 <b>{pct:.0f}%</b> of budget used. Reduce spending now.</div>')
    elif pct>=70: ins.append(f'<div class="ic">🟡 At <b>{pct:.0f}%</b> of budget. Watch Food and Shopping.</div>')
    else: ins.append(f'<div class="ic">🟢 Only <b>{pct:.0f}%</b> of budget used. Great job!</div>')
    food_amt=by_cat.get("Food",0)
    if food_amt and food_amt/total>0.3:
        ins.append(f'<div class="ic">🍔 Food is <b>₹{food_amt:,.0f}</b> ({food_amt/total*100:.0f}%). Cook at home to save ~₹{food_amt*0.3:,.0f}/mo.</div>')
    ins.append(f'<div class="ic">📅 <b>{n_txn} transactions</b> this month. Average: <b>₹{avg_txn:,.0f}</b>.</div>')
    for i in ins: st.markdown(i,unsafe_allow_html=True)

    st.markdown('<div class="sh">Transactions</div>',unsafe_allow_html=True)
    disp=df_f[["date","description","category","amount"]].copy()
    disp.columns=["Date","Description","Category","Amount (₹)"]
    disp["Date"]=disp["Date"].dt.strftime("%d %b %Y")
    disp=disp.sort_values("Date",ascending=False)
    st.dataframe(disp,use_container_width=True,hide_index=True,
                 column_config={"Amount (₹)":st.column_config.NumberColumn(format="₹%.0f"),
                                "Date":st.column_config.TextColumn(width="small"),
                                "Category":st.column_config.TextColumn(width="small")})

    d1,d2=st.columns(2)
    report=f"SpendSmart Report\n{datetime.strptime(sel,'%Y-%m').strftime('%B %Y')}\nTotal: ₹{total:,.0f}\n\n{by_cat.to_string()}"
    with d1: st.download_button("📥 Report",report,f"report_{sel}.txt",use_container_width=True)
    with d2: st.download_button("📊 CSV",disp.to_csv(index=False),f"expenses_{sel}.csv",use_container_width=True)

# ────────────────────────────────────────
#  TAB 2 — ADD EXPENSE (mobile friendly)
# ────────────────────────────────────────
with tab2:
    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
    st.markdown('<div class="add-card">',unsafe_allow_html=True)
    st.markdown('<div class="add-title">Add New Expense</div>',unsafe_allow_html=True)

    e_date=st.date_input("Date",value=datetime.today(),key="t2_date")
    e_desc=st.text_input("Description",placeholder="e.g. Swiggy, Amazon, Electricity bill",key="t2_desc")
    e_amount=st.number_input("Amount (₹)",min_value=0.0,step=10.0,key="t2_amt")
    e_cat=st.selectbox("Category",CATEGORIES,key="t2_cat")

    if st.button("Add Expense",use_container_width=True,type="primary",key="t2_add"):
        if not e_desc:
            st.markdown('<div class="e-box">Please enter a description.</div>',unsafe_allow_html=True)
        elif e_amount<=0:
            st.markdown('<div class="e-box">Please enter an amount greater than 0.</div>',unsafe_allow_html=True)
        else:
            if save_exp(uid,e_date,e_desc,e_amount,e_cat):
                st.markdown('<div class="s-box">✅ Expense saved successfully!</div>',unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown('<div class="e-box">Failed to save. Please try again.</div>',unsafe_allow_html=True)

    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>",unsafe_allow_html=True)
    st.markdown('<div class="sh">Quick categories</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    cat_emojis={"Food":"🍔","Shopping":"🛍️","Bills":"💡","Transport":"🚌","Grocery":"🛒","Other":"📦"}
    for i,(cat,emoji) in enumerate(cat_emojis.items()):
        col=[c1,c2,c3][i%3]
        col.markdown(f'<div style="background:{cat_color(cat)}22;border:1px solid {cat_color(cat)}44;border-radius:10px;padding:8px;text-align:center;font-size:12px;font-weight:500;color:{cat_color(cat)};margin-bottom:6px;">{emoji} {cat}</div>',unsafe_allow_html=True)

# ────────────────────────────────────────
#  TAB 3 — UPLOAD CSV
# ────────────────────────────────────────
with tab3:
    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
    st.markdown('<div class="i-box">CSV must have columns: <b>Date, Description, Amount, Category</b></div>',unsafe_allow_html=True)

    uf=st.file_uploader("Upload CSV",type=["csv"],label_visibility="collapsed",key="t3_upload")
    if uf:
        try:
            df_up=pd.read_csv(uf)
            st.session_state.upload_data=df_up
            st.markdown(f'<div class="s-box">✅ Loaded {len(df_up)} rows. Preview below — click Save to store them.</div>',unsafe_allow_html=True)
            st.dataframe(df_up.head(5),use_container_width=True,hide_index=True)
            if st.button("💾 Save all to Database",use_container_width=True,type="primary",key="t3_save"):
                ok_cnt=0;err_cnt=0
                for _,row in df_up.iterrows():
                    try:
                        cols={c.lower():v for c,v in row.items()}
                        saved=save_exp(uid,cols.get("date"),str(cols.get("description","")),cols.get("amount",0),str(cols.get("category","Other")))
                        if saved: ok_cnt+=1
                        else: err_cnt+=1
                    except: err_cnt+=1
                if ok_cnt>0:
                    st.markdown(f'<div class="s-box">✅ Saved {ok_cnt} expenses! Go to Dashboard to view them.</div>',unsafe_allow_html=True)
                    st.session_state.upload_data=None
                if err_cnt>0:
                    st.markdown(f'<div class="e-box">⚠️ {err_cnt} rows failed. Check date format (YYYY-MM-DD) and try again.</div>',unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="e-box">Error reading file: {str(e)}</div>',unsafe_allow_html=True)

    st.markdown('<div class="sh">Sample CSV format</div>',unsafe_allow_html=True)
    sample=pd.DataFrame({"Date":["2026-04-01","2026-04-02","2026-04-03"],"Description":["Swiggy","Amazon","Electricity"],"Amount":[250,1200,800],"Category":["Food","Shopping","Bills"]})
    st.dataframe(sample,use_container_width=True,hide_index=True)
    st.download_button("📥 Download sample CSV",sample.to_csv(index=False),"sample_expenses.csv",use_container_width=True)

# ────────────────────────────────────────
#  TAB 4 — SETTINGS
# ────────────────────────────────────────
with tab4:
    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)

    st.markdown('<div class="sh">Account</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="cc"><div style="font-size:13px;color:#64748b;margin-bottom:4px;">Logged in as</div><div style="font-size:15px;font-weight:500;color:#0f172a;">{uname}</div><div style="font-size:13px;color:#94a3b8;">{uemail}</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="sh">About</div>',unsafe_allow_html=True)
    st.markdown('<div class="cc"><div style="font-size:13px;color:#334155;line-height:1.7;"><b style="color:#0f172a;">SpendSmart</b> — AI-powered expense analytics.<br>Built with Python · Streamlit · Supabase · Pandas<br><br>github.com/nreddie7702/expense-tracker</div></div>',unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
    if st.button("Sign Out",use_container_width=True):
        try: supabase.auth.sign_out()
        except: pass
        st.session_state.user=None;st.session_state.upload_data=None
        st.session_state.auth_mode="login";st.session_state.auth_msg=None;st.rerun()

st.markdown("---")
st.caption(f"SpendSmart · github.com/nreddie7702 · {uemail}")