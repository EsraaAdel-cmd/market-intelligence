import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

st.set_page_config(page_title="Market Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: #08080f; }
section[data-testid="stSidebar"] { background: #0c0c14 !important; border-right: 1px solid #161622; min-width: 210px !important; max-width: 210px !important; }
.sidebar-brand { padding: 20px 0 18px; border-bottom: 1px solid #161622; margin-bottom: 22px; }
.sidebar-brand-title { font-size: 13px; font-weight: 700; color: #f1f5f9; }
.sidebar-brand-sub { font-size: 10px; color: #374151; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.12em; }
.section-label { font-size: 9px; color: #374151; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 8px; }
.stButton > button { background: transparent !important; border: 1px solid #161622 !important; border-radius: 6px !important; color: #4b5563 !important; font-size: 12px !important; font-weight: 500 !important; padding: 8px 14px !important; width: 100% !important; text-align: left !important; margin-bottom: 2px !important; }
.stButton > button:hover { background: #161622 !important; color: #e2e8f0 !important; }
.filter-label { font-size: 9px; color: #374151; text-transform: uppercase; letter-spacing: 0.14em; margin: 18px 0 5px; }
.kpi { background: #0c0c14; border: 1px solid #161622; border-radius: 12px; padding: 20px 22px; position: relative; overflow: hidden; }
.kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1.5px; background: linear-gradient(90deg, #f97316, #fb923c, #fdba74, transparent); }
.kpi-label { font-size: 9px; color: #374151; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 10px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.03em; line-height: 1; }
.kpi-sub { font-size: 10px; color: #f97316; margin-top: 6px; }
.page-title { font-size: 18px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.02em; display: inline; }
.page-sub { font-size: 11px; color: #374151; margin-top: 4px; margin-bottom: 20px; }
.live-dot { display: inline-block; width: 6px; height: 6px; background: #f97316; border-radius: 50%; margin-left: 8px; vertical-align: middle; box-shadow: 0 0 6px #f97316; }
.chart-card { background: #0c0c14; border: 1px solid #161622; border-radius: 12px; padding: 18px 20px 14px; margin-bottom: 14px; }
.chart-title { font-size: 10px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #161622; }
.chat-user { background: #161622; border: 1px solid #1e1e30; border-radius: 10px 10px 3px 10px; padding: 12px 16px; margin: 8px 0; color: #e2e8f0; font-size: 13px; line-height: 1.6; }
.chat-ai { background: #0c0c14; border: 1px solid #161622; border-left: 2px solid #f97316; border-radius: 3px 10px 10px 10px; padding: 12px 16px; margin: 8px 0; color: #cbd5e1; font-size: 13px; line-height: 1.6; white-space: pre-wrap; }
.chat-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 5px; margin-top: 10px; }
.stDownloadButton > button { background: linear-gradient(135deg, #f97316, #fb923c) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stTextInput input { background: #0c0c14 !important; border: 1px solid #161622 !important; border-radius: 8px !important; color: #f1f5f9 !important; font-size: 13px !important; }
.stSelectbox > div > div { background: #0c0c14 !important; border: 1px solid #161622 !important; color: #f1f5f9 !important; border-radius: 8px !important; }
.stMultiSelect > div > div { background: #0c0c14 !important; border: 1px solid #161622 !important; border-radius: 8px !important; }
.stMultiSelect span[data-baseweb="tag"] { background: #f9731620 !important; color: #fb923c !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
GROQ_KEY = "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"
# ══════════════════════════════════════════════

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("books_dataset.csv")
        rating_map = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
        df["rating"] = df["rating"].map(rating_map)
        df["price"] = df["price"].astype(float)
        df.drop_duplicates(inplace=True)
        return df
    except FileNotFoundError:
        st.error("books_dataset.csv not found")
        st.stop()

df = load_data()

THEME = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0c0c14", font=dict(family="Inter",color="#374151",size=11), xaxis=dict(gridcolor="#161622",linecolor="#161622",tickfont=dict(color="#4b5563"),zeroline=False), yaxis=dict(gridcolor="#161622",linecolor="#161622",tickfont=dict(color="#4b5563"),zeroline=False), margin=dict(l=0,r=0,t=4,b=0))
ORANGE = ["#0c0c14","#431407","#9a3412","#f97316","#fdba74"]

# ══════════════════════════════════════════════
#   AI ANALYST FUNCTIONS
# ══════════════════════════════════════════════

def build_full_context(df):
    total      = len(df)
    cats       = df["category"].nunique()
    avg_price  = df["price"].mean()
    min_price  = df["price"].min()
    max_price  = df["price"].max()
    avg_rating = df["rating"].mean()
    five_star  = len(df[df["rating"] == 5])
    most_exp   = df.loc[df["price"].idxmax(), "title"]
    cheapest   = df.loc[df["price"].idxmin(), "title"]
    rating_dist = df["rating"].value_counts().sort_index().to_dict()

    stats = []
    for cat in df["category"].unique():
        sub = df[df["category"] == cat]
        stats.append({
            "Category"  : cat,
            "Count"     : len(sub),
            "Avg_Price" : round(sub["price"].mean(), 2),
            "Avg_Rating": round(sub["rating"].mean(), 2),
            "Min_Price" : round(sub["price"].min(), 2),
            "Max_Price" : round(sub["price"].max(), 2),
        })

    top10 = df.nlargest(10, "price")[["title","category","price","rating"]].to_dict(orient="records")

    df2 = df.copy()
    df2["value_score"] = df2["rating"] / df2["price"]
    best_value = df2.nlargest(5, "value_score")[["title","category","price","rating"]].to_dict(orient="records")

    return f"""
إجمالي الكتب: {total:,}
عدد الكاتيجوريز: {cats}
متوسط السعر: £{avg_price:.2f}
أغلى سعر: £{max_price:.2f} — "{most_exp}"
أرخص سعر: £{min_price:.2f} — "{cheapest}"
متوسط الريتينج: {avg_rating:.2f} / 5
عدد الكتب 5 نجوم: {five_star:,}
توزيع الريتينج: {rating_dist}

إحصائيات كل كاتيجوري:
{json.dumps(stats, ensure_ascii=False, indent=2)}

أغلى 10 كتب:
{json.dumps(top10, ensure_ascii=False, indent=2)}

أحسن 5 كتب value for money:
{json.dumps(best_value, ensure_ascii=False, indent=2)}
"""

def ask_groq(question, history, context):
    system = f"""أنت محلل بيانات محترف متخصص في سوق الكتب.
عندك بيانات كاملة عن داتاسيت كتب من موقع books.toscrape.com.

البيانات:
{context}

قواعد:
- أجب بدقة واستخدم الأرقام الحقيقية من البيانات
- استخدم bullet points لتنظيم الإجابة
- اجعل إجاباتك مختصرة وواضحة
- أجب بنفس لغة السؤال (عربي أو إنجليزي)
- استخدم الإيموجي لتجميل الإجابات
- لو السؤال مش عن الكتب، قل بأدب إنك متخصص في الكتب فقط
"""
    messages = [{"role": "system", "content": system}]
    for h in history[-6:]:
        messages.append({"role": "user",      "content": h["user"]})
        messages.append({"role": "assistant", "content": h["bot"]})
    messages.append({"role": "user", "content": question})

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {
        "model"      : "llama-3.3-70b-versatile",
        "messages"   : messages,
        "temperature": 0.7,
        "max_tokens" : 600,
    }
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {e}"

QUICK_PROMPTS = {
    "📊 ملخص السوق"   : "اعطيني ملخص تنفيذي عن سوق الكتب.",
    "💰 أعلى أسعار"   : "أي الكاتيجوريز عندها أعلى متوسط سعر؟",
    "⭐ Best Value"    : "ما هي أحسن كتب value for money؟",
    "📈 Rating Trends" : "ما الأنماط الموجودة في توزيع الريتينج؟",
}

# ══════════════════════════════════════════════
#   SIDEBAR
# ══════════════════════════════════════════════

with st.sidebar:
    st.markdown("<div class='sidebar-brand'><div class='sidebar-brand-title'>Market Intel</div><div class='sidebar-brand-sub'>Books Analytics</div></div>", unsafe_allow_html=True)
    if "page" not in st.session_state:
        st.session_state.page = "Overview"
    st.markdown("<div class='section-label'>Pages</div>", unsafe_allow_html=True)
    for name in ["Overview","Analytics","AI Analyst","Explorer"]:
        if st.button(name, key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name
    st.markdown("<div class='filter-label'>Categories</div>", unsafe_allow_html=True)
    all_cats = sorted(df["category"].unique().tolist())
    selected_cats = st.multiselect("", all_cats, default=all_cats, label_visibility="collapsed")
    st.markdown("<div class='filter-label'>Price Range</div>", unsafe_allow_html=True)
    price_range = st.slider("", float(df["price"].min()), float(df["price"].max()), (float(df["price"].min()), float(df["price"].max())), label_visibility="collapsed")
    st.markdown("<div class='filter-label'>Rating</div>", unsafe_allow_html=True)
    rating_filter = st.multiselect("", [1,2,3,4,5], default=[1,2,3,4,5], label_visibility="collapsed")
    total = len(df)
    cats  = df["category"].nunique()
    st.markdown(f"<div style='margin-top:20px;padding:14px;background:#08080f;border-radius:8px;border:1px solid #161622;'><div style='font-size:9px;color:#374151;text-transform:uppercase;'>Dataset</div><div style='font-size:20px;font-weight:700;color:#f97316;margin:5px 0 2px;'>{total:,}</div><div style='font-size:10px;color:#374151;'>{cats} categories</div></div>", unsafe_allow_html=True)

filtered = df[(df["category"].isin(selected_cats if selected_cats else all_cats)) & (df["price"] >= price_range[0]) & (df["price"] <= price_range[1]) & (df["rating"].isin(rating_filter))].copy()
page = st.session_state.page

# ══════════════════════════════════════════════
#   OVERVIEW
# ══════════════════════════════════════════════

if page == "Overview":
    st.markdown("<div style='margin-bottom:24px;'><span class='page-title'>Market Overview</span><span class='live-dot'></span><div class='page-sub'>Key performance indicators across the books market</div></div>", unsafe_allow_html=True)
    k1,k2,k3,k4,k5 = st.columns(5)
    five_star = len(filtered[filtered["rating"]==5])
    total_f   = len(filtered)
    avg_p     = filtered["price"].mean()
    max_p     = filtered["price"].max()
    avg_r     = filtered["rating"].mean()
    cats_f    = filtered["category"].nunique()
    pct       = five_star/max(total_f,1)*100
    for col,label,val,sub in [
        (k1,"Total Books",f"{total_f:,}",f"of {len(df):,} total"),
        (k2,"Avg Price",f"£{avg_p:.2f}",f"max £{max_p:.0f}"),
        (k3,"Avg Rating",f"{avg_r:.1f} ★","out of 5.0"),
        (k4,"Categories",str(cats_f),"selected"),
        (k5,"5-Star",f"{five_star:,}",f"{pct:.0f}% of total"),
    ]:
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card"><div class="chart-title">Top Categories by Volume</div>', unsafe_allow_html=True)
        d = filtered["category"].value_counts().head(10).reset_index(); d.columns=["category","count"]
        fig = px.bar(d,x="count",y="category",orientation="h",color="count",color_continuous_scale=ORANGE)
        fig.update_layout(**THEME,showlegend=False,coloraxis_showscale=False,height=300); fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card"><div class="chart-title">Average Price by Category</div>', unsafe_allow_html=True)
        d2 = filtered.groupby("category")["price"].mean().sort_values(ascending=False).head(10).reset_index(); d2.columns=["category","avg_price"]
        fig2 = px.bar(d2,x="avg_price",y="category",orientation="h",color="avg_price",color_continuous_scale=ORANGE)
        fig2.update_layout(**THEME,showlegend=False,coloraxis_showscale=False,height=300); fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    col3,col4 = st.columns(2)
    with col3:
        st.markdown('<div class="chart-card"><div class="chart-title">Category Share</div>', unsafe_allow_html=True)
        tc = filtered["category"].value_counts().head(7)
        fig3 = px.pie(values=tc.values,names=tc.index,hole=0.65,color_discrete_sequence=["#f97316","#fb923c","#fdba74","#ea580c","#c2410c","#9a3412","#fed7aa"])
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#0c0c14",font=dict(family="Inter",color="#374151",size=10),showlegend=True,legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#4b5563",size=10)),margin=dict(l=0,r=0,t=4,b=0),height=280)
        fig3.update_traces(textfont_color="#f1f5f9",textfont_size=11)
        st.plotly_chart(fig3,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="chart-card"><div class="chart-title">Rating Distribution</div>', unsafe_allow_html=True)
        rc = filtered["rating"].value_counts().sort_index().reset_index(); rc.columns=["rating","count"]; rc["stars"]=rc["rating"].apply(lambda x:"★"*int(x))
        fig4 = px.bar(rc,x="stars",y="count",color="count",color_continuous_scale=ORANGE)
        fig4.update_layout(**THEME,showlegend=False,coloraxis_showscale=False,height=280); fig4.update_traces(marker_line_width=0)
        st.plotly_chart(fig4,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
#   ANALYTICS
# ══════════════════════════════════════════════

elif page == "Analytics":
    st.markdown("<div style='margin-bottom:24px;'><span class='page-title'>Deep Analytics</span><div class='page-sub'>Distribution patterns, correlations and pricing insights</div></div>", unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card"><div class="chart-title">Price Distribution</div>', unsafe_allow_html=True)
        fig = px.histogram(filtered,x="price",nbins=30,color_discrete_sequence=["#f97316"])
        fig.update_layout(**THEME,showlegend=False,height=250); fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card"><div class="chart-title">Avg Rating per Category</div>', unsafe_allow_html=True)
        ar = filtered.groupby("category")["rating"].mean().sort_values(ascending=False).head(10).reset_index(); ar.columns=["category","avg_rating"]
        fig2 = px.bar(ar,x="avg_rating",y="category",orientation="h",color="avg_rating",color_continuous_scale=ORANGE)
        fig2.update_layout(**THEME,showlegend=False,coloraxis_showscale=False,height=250); fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card"><div class="chart-title">Price vs Rating</div>', unsafe_allow_html=True)
    fig3 = px.scatter(filtered,x="rating",y="price",color="category",opacity=0.7,hover_data=["title","category"])
    fig3.update_layout(**THEME,height=360,showlegend=True,legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#4b5563",size=10))); fig3.update_traces(marker=dict(size=6))
    st.plotly_chart(fig3,use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    col3,col4 = st.columns(2)
    with col3:
        st.markdown('<div class="chart-card"><div class="chart-title">Price Spread by Category</div>', unsafe_allow_html=True)
        top6 = filtered["category"].value_counts().head(6).index.tolist()
        fig4 = px.box(filtered[filtered["category"].isin(top6)],x="category",y="price",color="category",color_discrete_sequence=["#f97316","#fb923c","#fdba74","#ea580c","#c2410c","#fed7aa"])
        fig4.update_layout(**THEME,showlegend=False,height=290)
        st.plotly_chart(fig4,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Most Expensive Books</div>', unsafe_allow_html=True)
        t10 = filtered.nlargest(10,"price")[["title","category","price","rating"]].copy()
        t10["price"] = t10["price"].apply(lambda x: f"£{x:.2f}"); t10["rating"] = t10["rating"].apply(lambda x: "★"*int(x))
        st.dataframe(t10,use_container_width=True,hide_index=True,height=290)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
#   AI ANALYST
# ══════════════════════════════════════════════

elif page == "AI Analyst":
    st.markdown("<div style='margin-bottom:24px;'><span class='page-title'>AI Analyst</span><span class='live-dot'></span><div class='page-sub'>اسأل أي سؤال عن البيانات بالعربي أو الإنجليزي</div></div>", unsafe_allow_html=True)

    if "ai_context" not in st.session_state:
        with st.spinner("جاري تحليل الداتا كاملة..."):
            st.session_state.ai_context = build_full_context(df)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "quick_input" not in st.session_state:
        st.session_state.quick_input = ""

    st.markdown('<div class="chart-card"><div class="chart-title">Quick Prompts</div>', unsafe_allow_html=True)
    cols = st.columns(len(QUICK_PROMPTS))
    for col,(label,prompt) in zip(cols, QUICK_PROMPTS.items()):
        with col:
            if st.button(label, key=f"qp_{label}", use_container_width=True):
                st.session_state.quick_input = prompt
    st.markdown('</div>', unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-label" style="color:#374151;">You</div><div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-label" style="color:#f97316;">AI Analyst</div><div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    col_in, col_btn = st.columns([5,1])
    with col_in:
        user_input = st.text_input("", value=st.session_state.quick_input, placeholder="اسأل أي حاجة عن البيانات...", label_visibility="collapsed", key="chat_input")
    with col_btn:
        send = st.button("Send ➤", use_container_width=True)

    if send and user_input.strip():
        st.session_state.quick_input = ""
        history_pairs = []
        msgs = st.session_state.chat_history
        for i in range(0, len(msgs)-1, 2):
            if msgs[i]["role"] == "user" and msgs[i+1]["role"] == "assistant":
                history_pairs.append({"user": msgs[i]["content"], "bot": msgs[i+1]["content"]})
        with st.spinner("جاري التحليل..."):
            reply = ask_groq(user_input, history_pairs, st.session_state.ai_context)
        st.session_state.chat_history.append({"role":"user",      "content": user_input})
        st.session_state.chat_history.append({"role":"assistant", "content": reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

# ══════════════════════════════════════════════
#   EXPLORER
# ══════════════════════════════════════════════

elif page == "Explorer":
    st.markdown("<div style='margin-bottom:24px;'><span class='page-title'>Data Explorer</span><div class='page-sub'>Search, filter and export the full dataset</div></div>", unsafe_allow_html=True)
    col1,col2 = st.columns([3,1])
    with col1:
        search = st.text_input("",placeholder="Search by book title...",label_visibility="collapsed")
    with col2:
        sort_by = st.selectbox("",["Price ↓","Price ↑","Rating ↓","Title A–Z"],label_visibility="collapsed")
    results = filtered.copy()
    if search:
        results = results[results["title"].str.contains(search,case=False,na=False)]
    col_s,asc_s = {"Price ↓":("price",False),"Price ↑":("price",True),"Rating ↓":("rating",False),"Title A–Z":("title",True)}[sort_by]
    results = results.sort_values(col_s,ascending=asc_s)
    st.markdown("<br>", unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)
    total_r = len(results)
    avg_pr  = results["price"].mean() if total_r else 0
    cats_r  = results["category"].nunique()
    five_r  = len(results[results["rating"]==5])
    for col,label,val,sub in [
        (s1,"Results",f"{total_r:,}","books found"),
        (s2,"Avg Price",f"£{avg_pr:.2f}" if total_r else "—","in selection"),
        (s3,"Categories",str(cats_r),"represented"),
        (s4,"5-Star",str(five_r),"top rated"),
    ]:
        with col:
            st.markdown(f'<div class="kpi" style="margin-bottom:16px;"><div class="kpi-label">{label}</div><div class="kpi-value" style="font-size:20px;">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)
    display = results[["title","category","price","rating"]].copy()
    display["price"]  = display["price"].apply(lambda x: f"£{x:.2f}")
    display["rating"] = display["rating"].apply(lambda x: "★"*int(x))
    st.dataframe(display,use_container_width=True,hide_index=True,height=420)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("Export Filtered Data",data=results.to_csv(index=False).encode("utf-8"),file_name="market_data.csv",mime="text/csv")
