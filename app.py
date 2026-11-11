import streamlit as st
import pandas as pd
import numpy as np
import re
import string
import os
import io
from collections import Counter
from scipy.stats import kruskal
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

st.set_page_config(layout="wide", page_title="TEDx Engagement Analysis",
                   page_icon="🎙️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&display=swap');

:root{
    --bg-0:#12171d;
    --bg-1:#171d24;
    --surface:#222a33;
    --surface-2:#2b3540;
    --border:#38434f;
    --text:#e2e8ee;
    --muted:#93a4b3;
    --ember:#d2691e;
    --ember-2:#f5883a;
    --brass:#c9a227;
    --steel:#5b7f9e;
    --steel-2:#8ab4d6;
}

html, body, [class*="css"]{ font-family:'Barlow', sans-serif; }

.stApp{
    background:
        radial-gradient(1000px 520px at 10% -8%, rgba(210,105,30,.16), transparent 62%),
        radial-gradient(900px 480px at 95% 0%, rgba(91,127,158,.20), transparent 60%),
        linear-gradient(180deg, var(--bg-1) 0%, var(--bg-0) 100%);
    color: var(--text);
}

header[data-testid="stHeader"]{
    background: rgba(18,23,29,.55);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(56,67,79,.55);
}

.block-container{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1500px; }

h1,h2,h3,h4,h5,h6{
    font-family:'Barlow Condensed', sans-serif;
    text-transform: uppercase;
    letter-spacing: 1.6px;
    color: var(--text);
    margin-bottom: .4rem;
}
h2{
    font-size: 1.85rem;
    border-left: 5px solid var(--ember);
    padding-left: 14px;
    color: #fff;
}
h3{
    font-size: 1.25rem;
    color: var(--steel-2);
    border-bottom: 1px solid rgba(56,67,79,.9);
    padding-bottom: 6px;
}
p, li, label, span{ color: var(--text); }

.hero{
    position: relative;
    padding: 28px 34px 26px;
    border-radius: 16px;
    border: 1px solid var(--border);
    background:
        linear-gradient(120deg, rgba(210,105,30,.22) 0%, rgba(91,127,158,.16) 48%, rgba(34,42,51,.85) 100%);
    box-shadow: 0 18px 44px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.05);
    overflow: hidden;
    margin-bottom: 6px;
}
.hero::after{
    content:"";
    position:absolute; inset:0;
    background: repeating-linear-gradient(135deg, rgba(255,255,255,.035) 0 2px, transparent 2px 14px);
    pointer-events:none;
}
.hero-tag{
    display:inline-block;
    font-family:'Barlow Condensed', sans-serif;
    font-size:.82rem; letter-spacing:3px; font-weight:700;
    color:#14181d;
    background: linear-gradient(180deg, var(--ember-2), var(--ember));
    padding: 4px 12px; border-radius: 4px;
    margin-bottom: 12px;
}
.hero-title{
    font-family:'Bebas Neue', sans-serif;
    font-size: 3.4rem;
    line-height: 1;
    letter-spacing: 3px;
    margin: 0 0 8px 0;
    background: linear-gradient(90deg, #ffffff 0%, var(--ember-2) 55%, var(--brass) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub{
    color: var(--muted);
    font-size: 1.02rem;
    letter-spacing: .6px;
    margin: 0;
}
.hero-bar{
    margin-top: 18px;
    height: 4px; width: 130px; border-radius: 3px;
    background: linear-gradient(90deg, var(--ember), var(--brass), var(--steel));
    animation: pulseBar 2.6s ease-in-out infinite;
}
@keyframes pulseBar{
    0%,100%{ width:130px; opacity:1; }
    50%    { width:240px; opacity:.65; }
}

section[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #1b222a 0%, #131920 100%);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{ color: var(--ember-2); border:none; padding-left:0; }

.side-head{
    font-family:'Barlow Condensed', sans-serif;
    font-size: .85rem;
    letter-spacing: 3px;
    font-weight: 700;
    color: var(--steel-2);
    padding: 14px 0 6px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
}

section[data-testid="stFileUploaderDropzone"]{
    background: var(--surface) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 12px;
    transition: border-color .2s ease, box-shadow .2s ease;
}
section[data-testid="stFileUploaderDropzone"]:hover{
    border-color: var(--ember) !important;
    box-shadow: 0 0 0 3px rgba(210,105,30,.12);
}
div[data-baseweb="select"] > div{
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    transition: border-color .2s ease;
}
div[data-baseweb="select"] > div:hover{ border-color: var(--ember) !important; }
span[data-baseweb="tag"]{
    background: linear-gradient(180deg, var(--ember-2), var(--ember)) !important;
    color: #14181d !important;
    font-weight: 600;
}

div[data-testid="stTabs"] div[data-baseweb="tab-list"]{
    gap: 4px;
    border-bottom: 2px solid var(--border);
}
button[data-baseweb="tab"]{
    font-family:'Barlow Condensed', sans-serif;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 600;
    font-size: 1rem;
    color: var(--muted);
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
    transition: all .18s ease;
}
button[data-baseweb="tab"]:hover{
    color: var(--text);
    background: rgba(210,105,30,.10);
    border-color: rgba(210,105,30,.28);
}
button[data-baseweb="tab"][aria-selected="true"]{
    color: #14181d;
    background: linear-gradient(180deg, var(--ember-2), var(--ember));
    border-color: var(--ember);
    box-shadow: 0 -2px 20px rgba(210,105,30,.40);
}
div[data-baseweb="tab-highlight"]{ display:none; }
div[data-baseweb="tab-border"]{ background: var(--border); }

div[data-testid="stTabs"] div[role="tabpanel"]{ animation: fadeUp .35s ease both; }
@keyframes fadeUp{ from{opacity:0; transform:translateY(10px);} to{opacity:1; transform:none;} }

div[data-testid="stMetric"]{
    position: relative;
    background: linear-gradient(160deg, var(--surface-2) 0%, var(--surface) 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px 16px;
    overflow: hidden;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
div[data-testid="stMetric"]::before{
    content:"";
    position:absolute; left:0; top:0; height:3px; width:38%;
    background: linear-gradient(90deg, var(--ember), var(--brass));
    transition: width .32s ease;
}
div[data-testid="stMetric"]:hover{
    transform: translateY(-4px);
    border-color: rgba(210,105,30,.55);
    box-shadow: 0 14px 30px rgba(0,0,0,.50);
}
div[data-testid="stMetric"]:hover::before{ width:100%; }
div[data-testid="stMetricLabel"] p{
    font-family:'Barlow Condensed', sans-serif;
    font-size: .95rem !important;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: var(--muted) !important;
}
div[data-testid="stMetricValue"]{
    font-family:'Bebas Neue', sans-serif;
    font-size: 2.3rem;
    letter-spacing: 1.5px;
    color: #fff;
}

div[data-testid="stDataFrame"]{
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    transition: border-color .2s ease, box-shadow .2s ease;
}
div[data-testid="stDataFrame"]:hover{
    border-color: rgba(91,127,158,.75);
    box-shadow: 0 0 0 1px rgba(91,127,158,.20), 0 12px 26px rgba(0,0,0,.40);
}

div[data-testid="stExpander"]{
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    background: linear-gradient(160deg, rgba(43,53,64,.75), rgba(34,42,51,.75));
    overflow: hidden;
    transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
    margin-bottom: 8px;
}
div[data-testid="stExpander"]:hover{
    border-color: rgba(210,105,30,.60) !important;
    box-shadow: 0 10px 24px rgba(0,0,0,.42);
    transform: translateX(3px);
}
div[data-testid="stExpander"] summary{
    font-family:'Barlow Condensed', sans-serif;
    letter-spacing: 1px;
    font-weight: 600;
    color: var(--text);
    transition: color .2s ease;
}
div[data-testid="stExpander"] summary:hover{ color: var(--ember-2); }

div[data-testid="stVegaLiteChart"],
div[data-testid="stArrowVegaLiteChart"]{
    background: linear-gradient(160deg, rgba(43,53,64,.55), rgba(34,42,51,.55));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 14px;
    transition: border-color .2s ease, box-shadow .2s ease;
}
div[data-testid="stVegaLiteChart"]:hover{
    border-color: rgba(210,105,30,.45);
    box-shadow: 0 10px 26px rgba(0,0,0,.40);
}

div[data-testid="stAlert"]{
    border-radius: 12px;
    border-left: 4px solid var(--ember);
    background: rgba(210,105,30,.10);
}

::-webkit-scrollbar{ width: 11px; height: 11px; }
::-webkit-scrollbar-track{ background: #10151a; }
::-webkit-scrollbar-thumb{
    background: linear-gradient(180deg, #3d4a57, #2b343f);
    border-radius: 6px;
    border: 2px solid #10151a;
}
::-webkit-scrollbar-thumb:hover{ background: linear-gradient(180deg, var(--ember-2), var(--ember)); }
</style>
""", unsafe_allow_html=True)

# --- REMOVED format_number helper so we can use raw full numbers ---

@st.cache_data
def load_example_data():
    df = pd.DataFrame({
        'Speaker': ['Jessica Dere', 'Nadine Burke Harris', 'Guy Winch', 'John Rigg', 'Dr. Jeffrey Lieberman', 'Judson Brewer'],
        'Keyword': ['Challenges and rewards of a culturally informed approach to mental health', 'How childhood trauma affects health across a lifetime', 'How to practice emotional first aid', 'The effect of trauma on the brain and how it affects behaviors', 'Imagine there was no stigma to mental illness', 'A simple way to break a bad habit'],
        'Date Released': pd.to_datetime(['2015-04-21', '2015-02-18', '2015-02-17', '2015-03-21', '2016-01-12', '2016-02-25']),
        'Views': [465557, 8300874, 5467141, 2760468, 609769, 16882137],
        'Likes': [3000, 197000, 201000, 33000, 9000, 328000],
        'Comments': [45, 9237, 3391, 2319, 643, 5667],
        'Theme': ['Mental Health', 'Mental Health', 'Mental Health', 'Mental Health', 'Mental Health', 'Mental Health'],
        'Transcript': [
            "thank you it's truly an honor to be here I would like to start my talk today with a little exercise introducing you to a person named Pat", 
            "In the mid-90s the CDC and Kaiser Permanente discovered an exposure that dramatically increased the risk", 
            "I grew up with my identical twin who was an incredibly loving brother", 
            "I want to ask you to think back to some occasion in your life", 
            "Personal Question I know we're only just meeting for the first time", 
            "When I was first learning to meditate the instruction was to simply pay attention to my breath"
        ]
    })
    return df


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    try:
        stop_words = set(stopwords.words('english'))
    except LookupError:
        nltk.download('stopwords')
        stop_words = set(stopwords.words('english'))

    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)

    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    return ' '.join(tokens)


def process_data(df):
    df = df.copy()

    # 1. Map 'Topic' to 'Theme' if it exists, otherwise use Column H
    if 'Topic' in df.columns:
        df.rename(columns={'Topic': 'Theme'}, inplace=True)
    elif len(df.columns) >= 8 and 'Theme' not in df.columns:
        df.rename(columns={df.columns[7]: 'Theme'}, inplace=True)

    # 2. Helper function to clean "3K" or "1.5M" strings into numbers
    def clean_numeric(value):
        if pd.isna(value) or value == "":
            return 0
        if isinstance(value, (int, float)):
            return value
        val_str = str(value).upper().strip().replace(',', '')
        try:
            if 'K' in val_str:
                return float(val_str.replace('K', '')) * 1_000
            if 'M' in val_str:
                return float(val_str.replace('M', '')) * 1_000_000
            return float(val_str)
        except ValueError:
            return 0

    numeric_cols = ['Views', 'Likes', 'Comments']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)

    # 3. RELAXED FILTERING TO KEEP ALL ROWS
    df['Transcript'] = df['Transcript'].fillna("Empty Transcript")
    
    if 'Theme' in df.columns:
        df['Theme'] = df['Theme'].fillna("Uncategorized")

    df['Date Released'] = pd.to_datetime(df['Date Released'], errors='coerce')
    df.dropna(subset=['Date Released'], inplace=True)
    
    df = df[(df['Date Released'].dt.year >= 2015) & (df['Date Released'].dt.year <= 2025)]
    df['year'] = df['Date Released'].dt.year
    
    bins = [2014, 2019, 2025]
    labels = ['2015-2019', '2020-2025']
    df['period'] = pd.cut(df['year'], bins=bins, labels=labels, right=True, include_lowest=True)
    df.dropna(subset=['period'], inplace=True)

    # Ensure numeric columns exist before math
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0

    df['engagement_score'] = df['Views'] + df['Likes'] + df['Comments']
    df['clean_transcript'] = df['Transcript'].apply(clean_text)
    return df


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="side-head">DATA SOURCE</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Dataset", type=['csv', 'xlsx'],
                                         label_visibility="collapsed")
        use_example = st.checkbox("Use example dataset (if no upload)", value=False)

        data = None
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                else:
                    data = pd.read_excel(uploaded_file)
            except Exception as e:
                st.error(f"Error loading file: {e}")
        elif use_example:
            data = load_example_data()

        if data is None:
            st.info("Awaiting data. Upload a file or tick the example dataset box.")
            st.stop()

        return data


def render_filters(df):
    with st.sidebar:
        st.markdown('<div class="side-head">FILTERS</div>', unsafe_allow_html=True)

        all_periods = list(df['period'].cat.categories)
        selected_periods = st.multiselect(
            "Period", all_periods, default=all_periods,
            help="Restrict every tab to the selected five-year windows."
        )
        if not selected_periods:
            selected_periods = all_periods

    out = df[df['period'].isin(selected_periods)]

    if out.empty:
        st.warning("No talks match the current filters. Loosen them in the sidebar.")
        st.stop()
    return out


def main():
    st.markdown("""
    <div class="hero">
        <div class="hero-tag">TEDX DATA INTELLIGENCE</div>
        <div class="hero-title">TEDx Talk Engagement Analysis</div>
        <p class="hero-sub">Audience engagement, language patterns and topic clusters · 2015 – 2025</p>
        <div class="hero-bar"></div>
    </div>
    """, unsafe_allow_html=True)

    raw_df = render_sidebar()

    required_cols = ['Keyword', 'Speaker', 'Date Released', 'Views', 'Likes', 'Comments', 'Transcript']
    if not all(c in raw_df.columns for c in required_cols):
        st.error(f"Dataset is missing one or more required columns: {required_cols}")
        st.stop()

    df = process_data(raw_df)
    if df.empty:
        st.error("No data available after filtering.")
        st.stop()

    df = render_filters(df)

    peak_period = df.groupby('period', observed=True)['engagement_score'].sum().idxmax()
    k1, k2, k3, k4 = st.columns(4)
    
    # Changed to use f"{val:,.0f}" to format with commas and no decimals
    k1.metric("Talks Analysed", f"{len(df):,.0f}")
    k2.metric("Total Engagement", f"{df['engagement_score'].sum():,.0f}")
    k3.metric("Avg per Talk", f"{df['engagement_score'].mean():,.0f}")
    k4.metric("Peak Period", str(peak_period))
    st.write("")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "① Engagement by Period",
        "② Keyword & Theme Patterns",
        "③ Theme Clusters", 
        "④ Trends & Variations",
        "⑤ Top Performers"
    ])

    with tab1:
        st.header("Audience Engagement Analysis")
        st.write("Aggregate audience engagement metrics for each five-year period.")

        period_agg = df.groupby('period', observed=True).agg(
            Videos=('Keyword', 'count'),
            Views=('Views', 'sum'),
            Likes=('Likes', 'sum'),
            Comments=('Comments', 'sum'),
            Avg_Engagement=('engagement_score', 'mean'),
            Total_Engagement=('engagement_score', 'sum')
        ).reset_index()

        # Using Pandas Styler to format numbers with commas directly in the dataframe
        styled_df = period_agg.style.format({
            'Views': '{:,.0f}',
            'Likes': '{:,.0f}',
            'Comments': '{:,.0f}',
            'Avg_Engagement': '{:,.0f}',
            'Total_Engagement': '{:,.0f}'
        })
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        st.subheader("Total Engagement Score by Period")
        st.bar_chart(period_agg.set_index('period')['Total_Engagement'], use_container_width=True)

        st.subheader("Average Engagement Score per Video")
        st.bar_chart(period_agg.set_index('period')['Avg_Engagement'], use_container_width=True)

    with tab2:
        st.header("Theme & Title Engagement Analysis")
        st.write("This section breaks down the most engaging Themes and Keywords (Titles) for each period.")

        for period in df['period'].unique():
            st.markdown(f"### Period: {period}")
            
            p_df = df[df['period'] == period]

            # 1. TOP 6 MOST ENGAGING TOPICS (THEMES)
            st.markdown("#### Top 6 Most Engaging Topics (Themes)")
            if 'Theme' in p_df.columns:
                theme_agg = p_df.groupby('Theme')['engagement_score'].sum().reset_index()
                theme_agg = theme_agg.sort_values('engagement_score', ascending=False).head(6)
                
                styled_theme_agg = theme_agg.style.format({'engagement_score': '{:,.0f}'})
                st.dataframe(styled_theme_agg, use_container_width=True, hide_index=True)
                st.bar_chart(theme_agg.set_index('Theme')['engagement_score'], use_container_width=True)
            else:
                st.info("Theme column not found in the dataset.")

            # 2. MOST ENGAGING KEYWORDS IN EVERY THEME
            st.markdown("#### Most Engaging Keywords (Titles) in Every Theme")
            if 'Theme' in p_df.columns:
                for theme in p_df['Theme'].unique():
                    # Get top 3 titles for this theme
                    theme_titles = p_df[p_df['Theme'] == theme].sort_values('engagement_score', ascending=False).head(3)
                    
                    # Only display if there are titles
                    if not theme_titles.empty:
                        with st.expander(f"Theme: {theme} (Top 3 Titles)"):
                            display_df = theme_titles[['Keyword', 'engagement_score']].copy()
                            display_df.columns = ['Talk Title (Keyword)', 'Engagement Score']
                            
                            styled_display = display_df.style.format({'Engagement Score': '{:,.0f}'})
                            st.dataframe(styled_display, use_container_width=True, hide_index=True)

            # 3. MOST ENGAGING KEYWORDS OVERALL
            st.markdown("#### Most Engaging Keywords (Titles) Overall")
            top_titles = p_df.sort_values('engagement_score', ascending=False).head(5)
            display_top = top_titles[['Keyword', 'engagement_score']].copy()
            display_top.columns = ['Talk Title (Keyword)', 'Engagement Score']
            
            styled_top = display_top.style.format({'Engagement Score': '{:,.0f}'})
            st.dataframe(styled_top, use_container_width=True, hide_index=True)
            st.markdown("---")

    with tab3:
        st.header("Engagement Metrics by Theme")
        st.write("This section compares the actual Themes assigned in the dataset, showing total and average engagement.")

        if 'Theme' in df.columns:
            theme_agg = df.groupby('Theme').agg(
                Videos=('Keyword', 'count'),
                Total_Engagement=('engagement_score', 'sum'),
                Avg_Engagement=('engagement_score', 'mean')
            ).reset_index().sort_values('Total_Engagement', ascending=False)

            styled_theme = theme_agg.style.format({
                'Total_Engagement': '{:,.0f}',
                'Avg_Engagement': '{:,.0f}'
            })
            st.dataframe(styled_theme, use_container_width=True, hide_index=True)

            st.subheader("Average Engagement Score by Theme")
            st.bar_chart(theme_agg.set_index('Theme')['Avg_Engagement'], use_container_width=True)
            
            st.subheader("Statistical Comparison of Theme Engagement")
            if df['Theme'].nunique() > 1:
                groups = [g['engagement_score'].values for _, g in df.groupby('Theme')]
                if all(len(g) > 0 for g in groups):
                    try:
                        stat, p_value = kruskal(*groups)
                        st.metric("Kruskal-Wallis H-test p-value", f"{p_value:.4f}")
                        if p_value < 0.05:
                            st.write("✅ Engagement differs significantly across themes (p < 0.05).")
                        else:
                            st.write("No statistically significant difference across themes (p ≥ 0.05).")
                    except ValueError:
                        st.warning("Unable to run Kruskal-Wallis: each group needs ≥ 1 sample.")
                else:
                    st.warning("Insufficient data for the statistical test.")
        else:
            st.info("Theme column not found in the dataset.")

    with tab4:
        st.header("Trend Analysis Across Periods")
        st.write("Period-over-period movement in aggregate engagement and topic mix.")

        pivot_engagement = df.pivot_table(
            index='period', values=['Views', 'Likes', 'Comments', 'engagement_score'],
            aggfunc='sum', observed=True
        )
        st.subheader("Aggregate Metrics Over Time")
        
        styled_pivot = pivot_engagement.style.format({
            'Views': '{:,.0f}',
            'Likes': '{:,.0f}',
            'Comments': '{:,.0f}',
            'engagement_score': '{:,.0f}'
        })
        st.dataframe(styled_pivot, use_container_width=True, hide_index=True)

        st.subheader("Growth in Engagement Score")
        if len(pivot_engagement) > 1:
            growth = pivot_engagement['engagement_score'].pct_change() * 100
            
            growth_list = []
            for i, (idx, val) in enumerate(growth.items()):
                if pd.isna(val):
                    growth_list.append("Baseline")
                else:
                    growth_list.append(f"{val:,.1f}%")
            
            growth_df = pd.DataFrame({'Period': growth.index, 'Growth': growth_list})
            st.dataframe(growth_df, use_container_width=True, hide_index=True)
            
            chart_growth = growth.dropna()
            if not chart_growth.empty:
                st.bar_chart(chart_growth, use_container_width=True)
        else:
            st.info("At least two periods are required to compute growth.")

        st.subheader("Theme Share Over Time")
        if 'Theme' in df.columns:
            theme_share = df.groupby(['period', 'Theme'], observed=True).size().unstack(fill_value=0)
            theme_share_pct = theme_share.div(theme_share.sum(axis=1), axis=0) * 100
            st.dataframe(theme_share_pct.style.format('{:.1f}%'), use_container_width=True, hide_index=True)
            st.bar_chart(theme_share_pct, use_container_width=True)
        else:
            st.info("Theme column not found.")

    with tab5:
        st.header("Top Performing Content")
        st.write("The three highest-engagement talks inside each period.")

        top_videos = (df.sort_values('engagement_score', ascending=False)
                        .groupby('period', observed=True).head(3))

        for period in df['period'].unique():
            st.subheader(f"Period: {period}")
            period_top = top_videos[top_videos['period'] == period]
            for _, row in period_top.iterrows():
                with st.expander(f"{row['Keyword']} — {row['Speaker']}"):
                    c1, c2, c3, c4 = st.columns(4)
                    # Using f"{val:,.0f}" here so the Streamlit Metrics show full numbers
                    c1.metric("Views", f"{row['Views']:,.0f}")
                    c2.metric("Likes", f"{row['Likes']:,.0f}")
                    c3.metric("Comments", f"{row['Comments']:,.0f}")
                    c4.metric("Engagement", f"{row['engagement_score']:,.0f}")

if __name__ == "__main__":
    main()
