import streamlit as st
import hmac

# Password protection
def check_password():
    """Returns True if the user has the correct password."""
    
    def password_entered():
        """Checks whether the password entered is correct."""
        if hmac.compare_digest(
            st.session_state["password"], 
            st.secrets["PASSWORD"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False
    
    # Return True if the password is already validated
    if st.session_state.get("password_correct", False):
        return True
    
    # Show password input
    st.text_input(
        "🔐 Enter Password to Access Dashboard",
        type="password",
        on_change=password_entered,
        key="password"
    )
    
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect. Please try again.")
    
    return False

# Check password before showing anything else
if not check_password():
    st.stop()  # Stop execution if password is wrong
    

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import os
import warnings
warnings.filterwarnings('ignore')

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="COT Analysis Dashboard - Dual Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and better visibility
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    
    /* Base text color - WHITE for all default text */
    .stMarkdown, .stText, .stMetric, .stDataFrame, .stTable, .stAlert, .stSuccess, .stInfo,
    p, div, span, label, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1kyxreq {
        color: #ffffff !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #00ff88 !important;
    }
    
    /* Success message text */
    .stSuccess p, .stSuccess div {
        color: #ffffff !important;
    }
    
    /* Info box text */
    .stInfo p, .stInfo div {
        color: #ffffff !important;
    }
    
    /* Date info box styling */
    .date-info {
        background: linear-gradient(135deg, #1a1a2e, #2a2a3e);
        border-left: 4px solid #00ff88;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0 20px 0;
    }
    
    .date-info p {
        color: #ffffff !important;
    }
    
    /* Stylish Table Styling */
    .stylish-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin: 20px 0;
    }
    
    .stylish-table thead tr {
        background: linear-gradient(135deg, #00ff88, #00b4d8);
        color: #0a0a0a;
        font-weight: bold;
    }
    
    .stylish-table th {
        padding: 15px;
        text-align: center;
        font-size: 14px;
        letter-spacing: 1px;
        border-right: 1px solid rgba(255,255,255,0.2);
        color: #0a0a0a !important;
    }
    
    .stylish-table td {
        padding: 12px;
        text-align: center;
        background: #1e1e2f;
        border-bottom: 1px solid #3a3a4e;
        transition: all 0.3s ease;
    }
    
    .stylish-table tbody tr:hover td {
        background: linear-gradient(135deg, #2a2a3e, #3a3a4e);
        transform: scale(1.01);
        box-shadow: inset 0 0 10px rgba(0,255,136,0.1);
    }
    
    /* Positive/Negative colors in tables - GREEN for bullish, RED for bearish */
    .positive-cell {
        color: #00ff88 !important;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0,255,136,0.3);
    }
    
    .negative-cell {
        color: #ff4444 !important;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(255,68,68,0.3);
    }
    
    .neutral-cell {
        color: #ffaa00 !important;
    }
    
    /* Default cell text - WHITE */
    .stylish-table td:not(.positive-cell):not(.negative-cell):not(.neutral-cell) {
        color: #ffffff !important;
    }
    
    /* Sidebar text */
    .css-1d391kg, .css-1d391kg .stMarkdown, .css-1d391kg .stText,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    
    /* Headers - gradient text */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(135deg, #00ff88, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: bold;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a3e 100%);
        border-radius: 10px;
        color: #00ff88 !important;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #00ff88, #00b4d8);
        color: #0a0a0a;
        font-weight: bold;
        border: none;
        border-radius: 20px;
        padding: 8px 20px;
        transition: transform 0.3s;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(0,255,136,0.3);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #1e1e2f;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00ff88, #00b4d8);
        border-radius: 10px;
    }
    
    /* Section dividers */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, #00ff88, #00b4d8, #00ff88);
        margin: 30px 0;
        border-radius: 2px;
    }
    
    /* Column text in metrics */
    div[data-testid="column"] p {
        color: #ffffff !important;
    }
    
    /* Market selector buttons styling */
    .market-selector-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin: 20px 0;
        padding: 15px;
        background: rgba(30,30,47,0.6);
        border-radius: 16px;
        backdrop-filter: blur(5px);
    }
    .market-btn {
        background: linear-gradient(135deg, #2a2a3e, #1e1e2f);
        border: 1px solid #3a3a4e;
        padding: 10px 24px;
        border-radius: 40px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #e0e0e0;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
    }
    .market-btn:hover {
        background: linear-gradient(135deg, #3a3a4e, #2a2a3e);
        transform: translateY(-2px);
        border-color: #00ff88;
    }
    .market-btn.active {
        background: linear-gradient(135deg, #00ff88, #00b4d8);
        color: #0a0a0a;
        border-color: #00ff88;
        box-shadow: 0 0 15px rgba(0,255,136,0.3);
    }
    
    /* Dataframe styling for detailed table */
    .stDataFrame {
        background: #1e1e2f;
        border-radius: 12px;
        overflow: hidden;
    }
    .stDataFrame table {
        font-family: monospace;
        font-size: 13px;
    }
    .stDataFrame thead tr th {
        background: linear-gradient(135deg, #00ff88, #00b4d8);
        color: #0a0a0a;
        font-weight: bold;
    }
    .stDataFrame tbody td {
        color: #ffffff !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e1e2f;
        border-radius: 12px;
        padding: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #2a2a3e, #1e1e2f);
        border-radius: 40px;
        padding: 8px 24px;
        font-weight: 600;
        color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ff88, #00b4d8);
        color: #0a0a0a;
    }
    
    /* Code blocks */
    code, pre {
        color: #00ff88 !important;
    }
    
    /* Headers in sidebar */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        -webkit-text-fill-color: #00ff88;
        background: none;
    }
    
    /* Alert boxes */
    .stAlert div, .stAlert p {
        color: #ffffff !important;
    }
    
    /* Success boxes */
    .stSuccess div, .stSuccess p {
        color: #ffffff !important;
    }
    
    /* Info boxes */
    .stInfo div, .stInfo p {
        color: #ffffff !important;
    }
    
    /* Warning boxes */
    .stWarning div, .stWarning p {
        color: #ffffff !important;
    }
    
    /* Error boxes */
    .stError div, .stError p {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Base directory
#base_directory = r'C:\Users\gitau\OneDrive\Institutions'
import os
base_directory = os.path.dirname(os.path.abspath(__file__))

# Leveraged Funds file
leverage_file = os.path.join(base_directory, 'FinFutYY.xls')

# Non-Commercial file
noncommercial_file = os.path.join(base_directory, 'annual.xls')

# Markets for Leveraged Funds
leverage_markets = {
    'CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE': 'CAD',
    'SWISS FRANC - CHICAGO MERCANTILE EXCHANGE': 'CHF',
    'BRITISH POUND - CHICAGO MERCANTILE EXCHANGE': 'GBP',
    'JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE': 'JPY',
    'EURO FX - CHICAGO MERCANTILE EXCHANGE': 'EUR',
    'AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE': 'AUD',
    'NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE': 'NZD',
    'S&P 500 Consolidated - CHICAGO MERCANTILE EXCHANGE': 'SP500',
    'NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE': 'NAS100',
    'DJIA Consolidated - CHICAGO BOARD OF TRADE': 'DJIA',
    'GOLD - COMMODITY EXCHANGE INC.': 'XAU',
    'SILVER - COMMODITY EXCHANGE INC.': 'XAG',
    'BITCOIN - CHICAGO MERCANTILE EXCHANGE': 'BITCOIN',
    'USD INDEX - ICE FUTURES U.S.': 'USD'
}

# Markets for Non-Commercial
noncommercial_markets = {
    'USD INDEX - ICE FUTURES U.S.': 'USD',
    'SWISS FRANC - CHICAGO MERCANTILE EXCHANGE': 'CHF',
    'SILVER - COMMODITY EXCHANGE INC.': 'XAG',
    'NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE': 'NZD',
    'NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE': 'NAS100',
    'JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE': 'JPY',
    'GOLD - COMMODITY EXCHANGE INC.': 'XAU',
    'EURO FX - CHICAGO MERCANTILE EXCHANGE': 'EUR',
    'CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE': 'CAD',
    'BRITISH POUND - CHICAGO MERCANTILE EXCHANGE': 'GBP',
    'BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE': 'BRENT',
    'AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE': 'AUD',
    'S&P 500 Consolidated - CHICAGO MERCANTILE EXCHANGE': 'SP500',
    'BITCOIN - CHICAGO MERCANTILE EXCHANGE': 'BITCOIN'
}

# All possible currency pairs and index pairs
currency_pairs = [
    'AUDUSD', 'AUDJPY', 'AUDCAD', 'AUDCHF', 'AUDNZD',
    'GBPUSD', 'GBPJPY', 'GBPCAD', 'GBPCHF', 'GBPNZD',
    'EURUSD', 'EURJPY', 'EURCAD', 'EURCHF', 'EURNZD', 'EURGBP', 'EURAUD',
    'USDJPY', 'USDCAD', 'USDCHF',
    'CADJPY', 'CADCHF',
    'NZDUSD', 'NZDJPY', 'NZDCAD', 'NZDCHF',
    'CHFJPY',
    'XAUUSD', 'XAGUSD', 'SP500USD', 'NAS100USD', 'DJIAUSD', 'BTCUSD'
]

# Alert thresholds
ALERT_THRESHOLDS = {
    'strong_bullish': 1.5,
    'strong_bearish': -1.5,
    'reversal_trigger': 0.5,
    'momentum_trigger': 0.5,
    'accumulate_threshold': 0.3,
    'distribute_threshold': -0.3,
    'high_conviction_flow': 1.0,
    'high_conviction_oi': 2.0
}

# ============================================================================
# HELPER FUNCTIONS (Shared)
# ============================================================================

def calculate_percentile(data, value):
    """Calculate the percentile rank of value within data"""
    if not data:
        return 50
    return (sum(1 for x in data if x <= value) / len(data)) * 100

def get_date_info(report_date):
    """Calculate key dates based on CFTC report date"""
    report_date = pd.to_datetime(report_date)
    
    days_until_friday = (4 - report_date.weekday()) % 7
    if days_until_friday == 0:
        days_until_friday = 7
    data_available = report_date + timedelta(days=days_until_friday)
    
    days_until_monday = (0 - data_available.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    trading_start = data_available + timedelta(days=days_until_monday)
    
    return {
        'report_date': report_date,
        'data_available': data_available,
        'trading_start': trading_start
    }

def display_date_info(date_info):
    """Display formatted date information"""
    st.markdown(f"""
    <div class="date-info">
        <p style="margin: 5px 0;">📅 <strong>CFTC REPORT DATE (Tuesday):</strong> {date_info['report_date'].strftime('%A, %B %d, %Y')}</p>
        <p style="margin: 5px 0;">📂 <strong>DATA AVAILABLE (Friday):</strong> {date_info['data_available'].strftime('%A, %B %d, %Y')}</p>
        <p style="margin: 5px 0;">🎯 <strong>NEXT TRADING WEEK START (Monday):</strong> {date_info['trading_start'].strftime('%A, %B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

def create_stylish_table(df, title=None):
    """Create a stylish HTML table from DataFrame with color coding for bullish/bearish"""
    if df.empty:
        return "<p>No data available</p>"
    
    html = '<table class="stylish-table">'
    
    if title:
        html += f'<caption style="caption-side: top; text-align: center; padding: 10px; font-size: 16px; font-weight: bold; color: #00ff88;">{title}</caption>'
    
    html += '<thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead>'
    
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            value = row[col]
            value_str = str(value)
            
            # Check for bullish indicators
            is_bullish = (
                ('BUY' in value_str) or
                ('🟢' in value_str) or
                ('ACCUMULATING' in value_str) or
                ('BULLISH' in value_str) or
                (isinstance(value, (int, float)) and value > 0 and ('Flow' in col or 'Differential' in col or 'Strength' in col)) or
                (isinstance(value, str) and value.startswith('+') and '%' in value)
            )
            
            # Check for bearish indicators
            is_bearish = (
                ('SELL' in value_str) or
                ('🔴' in value_str) or
                ('DISTRIBUTING' in value_str) or
                ('BEARISH' in value_str) or
                (isinstance(value, (int, float)) and value < 0 and ('Flow' in col or 'Differential' in col or 'Strength' in col)) or
                (isinstance(value, str) and value.startswith('-') and '%' in value)
            )
            
            if is_bullish:
                html += f'<td class="positive-cell">{value}</td>'
            elif is_bearish:
                html += f'<td class="negative-cell">{value}</td>'
            else:
                html += f'<td style="color: #ffffff;">{value}</td>'
        html += '</tr>'
    html += '</tbody>'
    html += '</table>'
    
    return html

def create_asset_strength_chart(asset_strength, title="Asset Strength by Weighted Flow"):
    """Create a bar chart for asset strength"""
    df = pd.DataFrame([
        {'Asset': k, 'Strength': v} for k, v in asset_strength.items()
        if k not in ['BRENT']
    ])
    df = df.sort_values('Strength', ascending=False)
    
    colors = ['#00ff88' if x > 0 else '#ff4444' for x in df['Strength']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['Asset'],
            y=df['Strength'],
            marker_color=colors,
            text=df['Strength'].apply(lambda x: f"{x:+.2f}%"),
            textposition='outside',
            textfont=dict(color='white'),
            hovertemplate='<b>%{x}</b><br>Strength: %{y:+.2f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(text=title, font=dict(color='white')),
        xaxis_title=dict(text="Asset", font=dict(color='white')),
        yaxis_title=dict(text="Weighted Flow %", font=dict(color='white')),
        plot_bgcolor='rgba(30,30,47,0.8)',
        paper_bgcolor='rgba(30,30,47,0)',
        font_color='#e0e0e0',
        height=500,
        showlegend=False,
        hovermode='closest'
    )
    
    fig.update_xaxes(gridcolor='#3a3a4e', gridwidth=0.5, tickfont=dict(color='white'))
    fig.update_yaxes(gridcolor='#3a3a4e', gridwidth=0.5, tickfont=dict(color='white'))
    
    return fig

def get_asset_strength(weekly_flow):
    """Extract weighted flow for all assets"""
    asset_strength = {}
    for market, data in weekly_flow.items():
        asset = data['currency']
        if asset:
            asset_strength[asset] = data['weighted_flow']
    return asset_strength

def calculate_pair_strength(asset_strength):
    """Calculate pair strength for currency pairs and index pairs"""
    pair_strength = {}
    
    for pair in currency_pairs:
        if pair == 'XAUUSD':
            if 'XAU' in asset_strength and 'USD' in asset_strength:
                pair_strength[pair] = asset_strength['XAU'] - asset_strength['USD']
        elif pair == 'XAGUSD':
            if 'XAG' in asset_strength and 'USD' in asset_strength:
                pair_strength[pair] = asset_strength['XAG'] - asset_strength['USD']
        elif pair == 'SP500USD':
            if 'SP500' in asset_strength and 'USD' in asset_strength:
                pair_strength[pair] = asset_strength['SP500'] - asset_strength['USD']
        elif pair == 'NAS100USD':
            if 'NAS100' in asset_strength and 'USD' in asset_strength:
                pair_strength[pair] = asset_strength['NAS100'] - asset_strength['USD']
        elif pair == 'DJIAUSD':
            if 'DJIA' in asset_strength and 'USD' in asset_strength:
                pair_strength[pair] = asset_strength['DJIA'] - asset_strength['USD']
        else:
            base = pair[:3]
            quote = pair[3:]
            if base in asset_strength and quote in asset_strength:
                pair_strength[pair] = asset_strength[base] - asset_strength[quote]
    
    return pair_strength

def normalize_to_0_100(strengths):
    """Normalize values to 0-100 scale"""
    if not strengths:
        return {}
    values = list(strengths.values())
    min_val, max_val = min(values), max(values)
    range_val = max_val - min_val
    if range_val == 0:
        return {k: 50 for k in strengths}
    return {k: ((v - min_val) / range_val) * 100 for k, v in strengths.items()}

def generate_trade_recommendations(normalized_strengths):
    """Generate buy/sell recommendations based on weighted flow"""
    if not normalized_strengths:
        return pd.DataFrame()
    
    currency_only = {k: v for k, v in normalized_strengths.items() if k not in ['XAU', 'XAG', 'NAS100', 'SP500', 'DJIA', 'BITCOIN', 'BRENT']}
    
    if not currency_only:
        return pd.DataFrame()
    
    sorted_currencies = sorted(currency_only.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_currencies[:3]
    weakest = sorted_currencies[-3:]
    
    recommendations = []
    
    for strong_curr, strong_score in strongest:
        for weak_curr, weak_score in weakest:
            if strong_curr != weak_curr:
                pair = f"{strong_curr}{weak_curr}"
                if pair in currency_pairs:
                    differential = strong_score - weak_score
                    
                    if differential > 50:
                        confidence = "HIGH"
                    elif differential > 30:
                        confidence = "MEDIUM"
                    else:
                        confidence = "LOW"
                    
                    recommendations.append({
                        'Action': 'BUY',
                        'Pair': pair,
                        'Differential': differential,
                        'Confidence': confidence
                    })
    
    for weak_curr, weak_score in weakest:
        for strong_curr, strong_score in strongest:
            if weak_curr != strong_curr:
                pair = f"{weak_curr}{strong_curr}"
                if pair in currency_pairs:
                    differential = weak_score - strong_score
                    
                    if abs(differential) > 50:
                        confidence = "HIGH"
                    elif abs(differential) > 30:
                        confidence = "MEDIUM"
                    else:
                        confidence = "LOW"
                    
                    recommendations.append({
                        'Action': 'SELL',
                        'Pair': pair,
                        'Differential': differential,
                        'Confidence': confidence
                    })
    
    recommendations.sort(key=lambda x: abs(x['Differential']), reverse=True)
    return pd.DataFrame(recommendations)

def generate_momentum_confirmed_trades(weekly_flow, normalized_strengths):
    """Identifies the highest quality trades with accelerating momentum"""
    
    if not normalized_strengths:
        return []
    
    currency_only = {k: v for k, v in normalized_strengths.items() if k not in ['XAU', 'XAG', 'NAS100', 'SP500', 'DJIA', 'BITCOIN', 'BRENT']}
    
    if not currency_only:
        return []
    
    accelerating_bullish = []
    accelerating_bearish = []
    
    for asset, norm_score in currency_only.items():
        asset_data = None
        for market, data in weekly_flow.items():
            if data['currency'] == asset:
                asset_data = data
                break
        
        if asset_data:
            weighted_flow = asset_data['weighted_flow']
            flow_change = asset_data['flow_change']
            
            if weighted_flow > 0.3 and flow_change > 0:
                accelerating_bullish.append({
                    'asset': asset,
                    'weighted_flow': weighted_flow,
                    'flow_change': flow_change,
                    'norm_score': norm_score
                })
            elif weighted_flow < -0.3 and flow_change < 0:
                accelerating_bearish.append({
                    'asset': asset,
                    'weighted_flow': weighted_flow,
                    'flow_change': flow_change,
                    'norm_score': norm_score
                })
    
    accelerating_bullish.sort(key=lambda x: x['norm_score'], reverse=True)
    accelerating_bearish.sort(key=lambda x: x['norm_score'])
    
    superior_pairs = []
    for bull in accelerating_bullish[:3]:
        for bear in accelerating_bearish[:3]:
            if bull['asset'] != bear['asset']:
                pair = f"{bull['asset']}{bear['asset']}"
                if pair in currency_pairs:
                    differential = bull['norm_score'] - bear['norm_score']
                    superior_pairs.append({
                        'Pair': pair,
                        'Base': bull['asset'],
                        'Base_Flow': bull['weighted_flow'],
                        'Quote': bear['asset'],
                        'Quote_Flow': bear['weighted_flow'],
                        'Differential': differential
                    })
    
    superior_pairs.sort(key=lambda x: x['Differential'], reverse=True)
    
    return superior_pairs

# ============================================================================
# LEVERAGED FUNDS SPECIFIC FUNCTIONS
# ============================================================================

@st.cache_data
def load_leverage_data():
    """Load Leveraged Funds data"""
    df = pd.read_excel(leverage_file)
    df['Report_Date_as_MM_DD_YYYY'] = pd.to_datetime(df['Report_Date_as_MM_DD_YYYY'])
    market_names = list(leverage_markets.keys())
    filtered_df = df[df['Market_and_Exchange_Names'].isin(market_names)]
    filtered_df = filtered_df.sort_values(['Market_and_Exchange_Names', 'Report_Date_as_MM_DD_YYYY'])
    return filtered_df

@st.cache_data
def calculate_leverage_flow(df):
    """Calculate Weighted Flow for Leveraged Funds"""
    weekly_flow = {}
    
    for market in leverage_markets.keys():
        market_df = df[df['Market_and_Exchange_Names'] == market].copy()
        
        if len(market_df) >= 5:
            market_history = []
            
            for idx in range(1, len(market_df)):
                curr = market_df.iloc[idx]
                prev = market_df.iloc[idx-1]
                
                change_long = curr.get('Change_in_Lev_Money_Long_All', 0)
                change_short = curr.get('Change_in_Lev_Money_Short_All', 0)
                leveraged_flow = change_long - change_short
                
                open_interest = curr['Open_Interest_All']
                prev_open_interest = prev['Open_Interest_All']
                
                flow_pct_of_oi = (leveraged_flow / open_interest) * 100 if open_interest > 0 else 0
                oi_momentum = ((open_interest - prev_open_interest) / prev_open_interest) * 100 if prev_open_interest > 0 else 0
                weighted_flow = flow_pct_of_oi * (1 + abs(oi_momentum) / 100)
                
                net_position = curr.get('Lev_Money_Positions_Long_All', 0) - curr.get('Lev_Money_Positions_Short_All', 0)
                net_position_pct = (net_position / open_interest) * 100 if open_interest > 0 else 0
                
                market_history.append({
                    'date': curr['Report_Date_as_MM_DD_YYYY'],
                    'weighted_flow': weighted_flow,
                    'oi_momentum_pct': oi_momentum,
                    'change_long': change_long,
                    'change_short': change_short,
                    'net_position': net_position,
                    'net_position_pct': net_position_pct,
                    'open_interest': open_interest,
                    'long_positions': curr.get('Lev_Money_Positions_Long_All', 0),
                    'short_positions': curr.get('Lev_Money_Positions_Short_All', 0)
                })
            
            if len(market_history) >= 1:
                latest = market_history[-1]
                previous = market_history[-2] if len(market_history) >= 2 else latest
                
                if latest['weighted_flow'] > ALERT_THRESHOLDS['accumulate_threshold']:
                    action = "ACCUMULATING"
                elif latest['weighted_flow'] < ALERT_THRESHOLDS['distribute_threshold']:
                    action = "DISTRIBUTING"
                else:
                    action = "NEUTRAL"
                
                if len(market_history) >= 4:
                    ma_4week = np.mean([h['weighted_flow'] for h in market_history[-4:]])
                else:
                    ma_4week = latest['weighted_flow']
                
                flow_change = latest['weighted_flow'] - previous['weighted_flow']
                
                reversal_signal = None
                if previous['weighted_flow'] < -ALERT_THRESHOLDS['reversal_trigger'] and latest['weighted_flow'] > ALERT_THRESHOLDS['accumulate_threshold']:
                    reversal_signal = "🔄 BULLISH REVERSAL PENDING"
                elif previous['weighted_flow'] > ALERT_THRESHOLDS['reversal_trigger'] and latest['weighted_flow'] < ALERT_THRESHOLDS['distribute_threshold']:
                    reversal_signal = "🔄 BEARISH REVERSAL PENDING"
                elif abs(latest['weighted_flow'] - ma_4week) > ALERT_THRESHOLDS['momentum_trigger']:
                    if latest['weighted_flow'] > ma_4week and latest['weighted_flow'] > 0:
                        reversal_signal = "📈 MOMENTUM ACCELERATING BULLISH"
                    elif latest['weighted_flow'] < ma_4week and latest['weighted_flow'] < 0:
                        reversal_signal = "📉 MOMENTUM ACCELERATING BEARISH"
                    elif latest['weighted_flow'] > ma_4week and latest['weighted_flow'] < 0:
                        reversal_signal = "📉 BEARISH WEAKENING"
                    elif latest['weighted_flow'] < ma_4week and latest['weighted_flow'] > 0:
                        reversal_signal = "📈 BULLISH WEAKENING"
                
                if abs(latest['weighted_flow']) > ALERT_THRESHOLDS['high_conviction_flow']:
                    conviction = "HIGH"
                elif abs(latest['weighted_flow']) > 0.5:
                    conviction = "MEDIUM"
                else:
                    conviction = "LOW"
                
                all_weighted_flows = [h['weighted_flow'] for h in market_history]
                percentile_1y = calculate_percentile(all_weighted_flows[-52:], latest['weighted_flow']) if len(all_weighted_flows) >= 52 else 50
                
                mean_flow = np.mean(all_weighted_flows[-52:]) if len(all_weighted_flows) >= 52 else latest['weighted_flow']
                std_flow = np.std(all_weighted_flows[-52:]) if len(all_weighted_flows) >= 52 else 1
                z_score = (latest['weighted_flow'] - mean_flow) / std_flow if std_flow != 0 else 0
                
                weekly_flow[market] = {
                    'date': latest['date'],
                    'currency': leverage_markets.get(market),
                    'weighted_flow': latest['weighted_flow'],
                    'oi_momentum_pct': latest['oi_momentum_pct'],
                    'change_long': latest['change_long'],
                    'change_short': latest['change_short'],
                    'net_position': latest['net_position'],
                    'net_position_pct': latest['net_position_pct'],
                    'open_interest': latest['open_interest'],
                    'action': action,
                    'conviction': conviction,
                    'ma_4week': ma_4week,
                    'prev_flow': previous['weighted_flow'],
                    'flow_change': flow_change,
                    'reversal_signal': reversal_signal,
                    'percentile_1y': percentile_1y,
                    'z_score': z_score,
                    'historical': market_history,
                    'long_positions': latest['long_positions'],
                    'short_positions': latest['short_positions']
                }
    
    return weekly_flow

# ============================================================================
# NON-COMMERCIAL SPECIFIC FUNCTIONS
# ============================================================================

@st.cache_data
def load_noncommercial_data():
    """Load Non-Commercial data"""
    df = pd.read_excel(noncommercial_file)
    df['Report_Date_as_MM_DD_YYYY'] = pd.to_datetime(df['Report_Date_as_MM_DD_YYYY'])
    market_names = list(noncommercial_markets.keys())
    filtered_df = df[df['Market_and_Exchange_Names'].isin(market_names)]
    filtered_df = filtered_df.sort_values(['Market_and_Exchange_Names', 'Report_Date_as_MM_DD_YYYY'])
    return filtered_df

@st.cache_data
def calculate_noncommercial_flow(df):
    """Calculate Weighted Flow for Non-Commercial"""
    weekly_flow = {}
    
    for market in noncommercial_markets.keys():
        market_df = df[df['Market_and_Exchange_Names'] == market].copy()
        
        if len(market_df) >= 5:
            market_history = []
            
            for idx in range(1, len(market_df)):
                curr = market_df.iloc[idx]
                prev = market_df.iloc[idx-1]
                
                change_long = curr.get('Change_in_NonComm_Long_All', 0)
                change_short = curr.get('Change_in_NonComm_Short_All', 0)
                flow = change_long - change_short
                
                open_interest = curr['Open_Interest_All']
                prev_open_interest = prev['Open_Interest_All']
                
                flow_pct_of_oi = (flow / open_interest) * 100 if open_interest > 0 else 0
                oi_momentum = ((open_interest - prev_open_interest) / prev_open_interest) * 100 if prev_open_interest > 0 else 0
                weighted_flow = flow_pct_of_oi * (1 + abs(oi_momentum) / 100)
                
                net_position = curr.get('NonComm_Positions_Long_All', 0) - curr.get('NonComm_Positions_Short_All', 0)
                net_position_pct = (net_position / open_interest) * 100 if open_interest > 0 else 0
                
                market_history.append({
                    'date': curr['Report_Date_as_MM_DD_YYYY'],
                    'weighted_flow': weighted_flow,
                    'oi_momentum_pct': oi_momentum,
                    'change_long': change_long,
                    'change_short': change_short,
                    'net_position': net_position,
                    'net_position_pct': net_position_pct,
                    'open_interest': open_interest,
                    'long_positions': curr.get('NonComm_Positions_Long_All', 0),
                    'short_positions': curr.get('NonComm_Positions_Short_All', 0)
                })
            
            if len(market_history) >= 1:
                latest = market_history[-1]
                previous = market_history[-2] if len(market_history) >= 2 else latest
                
                if latest['weighted_flow'] > ALERT_THRESHOLDS['accumulate_threshold']:
                    action = "ACCUMULATING"
                elif latest['weighted_flow'] < ALERT_THRESHOLDS['distribute_threshold']:
                    action = "DISTRIBUTING"
                else:
                    action = "NEUTRAL"
                
                if len(market_history) >= 4:
                    ma_4week = np.mean([h['weighted_flow'] for h in market_history[-4:]])
                else:
                    ma_4week = latest['weighted_flow']
                
                flow_change = latest['weighted_flow'] - previous['weighted_flow']
                
                reversal_signal = None
                if previous['weighted_flow'] < -ALERT_THRESHOLDS['reversal_trigger'] and latest['weighted_flow'] > ALERT_THRESHOLDS['accumulate_threshold']:
                    reversal_signal = "🔄 BULLISH REVERSAL PENDING"
                elif previous['weighted_flow'] > ALERT_THRESHOLDS['reversal_trigger'] and latest['weighted_flow'] < ALERT_THRESHOLDS['distribute_threshold']:
                    reversal_signal = "🔄 BEARISH REVERSAL PENDING"
                elif abs(latest['weighted_flow'] - ma_4week) > ALERT_THRESHOLDS['momentum_trigger']:
                    if latest['weighted_flow'] > ma_4week and latest['weighted_flow'] > 0:
                        reversal_signal = "📈 MOMENTUM ACCELERATING BULLISH"
                    elif latest['weighted_flow'] < ma_4week and latest['weighted_flow'] < 0:
                        reversal_signal = "📉 MOMENTUM ACCELERATING BEARISH"
                    elif latest['weighted_flow'] > ma_4week and latest['weighted_flow'] < 0:
                        reversal_signal = "📉 BEARISH WEAKENING"
                    elif latest['weighted_flow'] < ma_4week and latest['weighted_flow'] > 0:
                        reversal_signal = "📈 BULLISH WEAKENING"
                
                if abs(latest['weighted_flow']) > ALERT_THRESHOLDS['high_conviction_flow']:
                    conviction = "HIGH"
                elif abs(latest['weighted_flow']) > 0.5:
                    conviction = "MEDIUM"
                else:
                    conviction = "LOW"
                
                all_weighted_flows = [h['weighted_flow'] for h in market_history]
                percentile_1y = calculate_percentile(all_weighted_flows[-52:], latest['weighted_flow']) if len(all_weighted_flows) >= 52 else 50
                
                mean_flow = np.mean(all_weighted_flows[-52:]) if len(all_weighted_flows) >= 52 else latest['weighted_flow']
                std_flow = np.std(all_weighted_flows[-52:]) if len(all_weighted_flows) >= 52 else 1
                z_score = (latest['weighted_flow'] - mean_flow) / std_flow if std_flow != 0 else 0
                
                weekly_flow[market] = {
                    'date': latest['date'],
                    'currency': noncommercial_markets.get(market),
                    'weighted_flow': latest['weighted_flow'],
                    'oi_momentum_pct': latest['oi_momentum_pct'],
                    'change_long': latest['change_long'],
                    'change_short': latest['change_short'],
                    'net_position': latest['net_position'],
                    'net_position_pct': latest['net_position_pct'],
                    'open_interest': latest['open_interest'],
                    'action': action,
                    'conviction': conviction,
                    'ma_4week': ma_4week,
                    'prev_flow': previous['weighted_flow'],
                    'flow_change': flow_change,
                    'reversal_signal': reversal_signal,
                    'percentile_1y': percentile_1y,
                    'z_score': z_score,
                    'historical': market_history,
                    'long_positions': latest['long_positions'],
                    'short_positions': latest['short_positions']
                }
    
    return weekly_flow

# ============================================================================
# SHARED UI FUNCTIONS FOR BOTH REPORTS
# ============================================================================

def get_market_historical_data(weekly_flow, asset_code):
    """Extract historical data for a specific asset"""
    for market, data in weekly_flow.items():
        if data['currency'] == asset_code:
            if 'historical' in data and len(data['historical']) > 0:
                history = sorted(data['historical'], key=lambda x: x['date'])
                dates = [h['date'].strftime('%Y-%m-%d') for h in history]
                net_positions = [h['net_position'] for h in history]
                long_positions = [h['long_positions'] for h in history]
                short_positions = [h['short_positions'] for h in history]
                return dates, net_positions, long_positions, short_positions
    return [], [], [], []

def create_net_positions_chart(asset_code, dates, net_positions, long_positions, short_positions):
    """Create a line chart showing Net Positions over time"""
    if not dates or not net_positions:
        return None
    
    fig = go.Figure()
    
    # Add Net Positions line
    fig.add_trace(go.Scatter(
        x=dates,
        y=net_positions,
        mode='lines+markers',
        name='Net Positions (Long - Short)',
        line=dict(color='#00ff88', width=3),
        marker=dict(size=6, color='#00ff88', symbol='circle'),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 136, 0.1)',
        hovertemplate='<b>Date:</b> %{x}<br><b>Net Positions:</b> %{y:,.0f}<extra></extra>'
    ))
    
    # Add Long positions as a secondary line
    fig.add_trace(go.Scatter(
        x=dates,
        y=long_positions,
        mode='lines+markers',
        name='Long Positions',
        line=dict(color='#00b4d8', width=2, dash='dot'),
        marker=dict(size=5, color='#00b4d8', symbol='diamond'),
        hovertemplate='<b>Date:</b> %{x}<br><b>Long Positions:</b> %{y:,.0f}<extra></extra>'
    ))
    
    # Add Short positions as a secondary line
    fig.add_trace(go.Scatter(
        x=dates,
        y=short_positions,
        mode='lines+markers',
        name='Short Positions',
        line=dict(color='#ff4444', width=2, dash='dot'),
        marker=dict(size=5, color='#ff4444', symbol='x'),
        hovertemplate='<b>Date:</b> %{x}<br><b>Short Positions:</b> %{y:,.0f}<extra></extra>'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="#ffffff", opacity=0.3)
    
    fig.update_layout(
        title=dict(
            text=f"📈 {asset_code} Net Positions Over Time (Long − Short)",
            font=dict(color='white', size=18)
        ),
        xaxis=dict(
            title=dict(text="Report Date", font=dict(color='white')),
            tickangle=45,
            tickfont=dict(color='#e0e0e0'),
            gridcolor='#3a3a4e'
        ),
        yaxis=dict(
            title=dict(text="Contracts", font=dict(color='white')),
            tickfont=dict(color='#e0e0e0'),
            gridcolor='#3a3a4e',
            tickformat=',.0f'
        ),
        plot_bgcolor='rgba(30,30,47,0.8)',
        paper_bgcolor='rgba(30,30,47,0)',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0.5)'
        ),
        height=500,
        margin=dict(t=80, l=50, r=50, b=80)
    )
    
    return fig

def create_detailed_market_table(weekly_flow, asset_code):
    """Create a detailed table for a specific market"""
    for market, data in weekly_flow.items():
        if data['currency'] == asset_code:
            if 'historical' in data and len(data['historical']) > 0:
                history = sorted(data['historical'], key=lambda x: x['date'], reverse=True)
                
                table_data = []
                for h in history:
                    total = h['long_positions'] + h['short_positions']
                    pct_long = (h['long_positions'] / total * 100) if total > 0 else 0
                    pct_short = (h['short_positions'] / total * 100) if total > 0 else 0
                    
                    table_data.append({
                        'Date': h['date'].strftime('%Y-%m-%d'),
                        'Long Positions': f"{h['long_positions']:,.0f}",
                        'Short Positions': f"{h['short_positions']:,.0f}",
                        'Total OI': f"{total:,.0f}",
                        '% Long': f"{pct_long:+.2f}%",
                        '% Short': f"{pct_short:+.2f}%",
                        'Net Positions': f"{h['net_position']:+,.0f}",
                        'Δ Long': f"{h['change_long']:+,.0f}",
                        'Δ Short': f"{h['change_short']:+,.0f}"
                    })
                
                return pd.DataFrame(table_data)
    return pd.DataFrame()

def render_report(weekly_flow, report_name, asset_list):
    """Render a complete report with market selector, table, chart, and analysis"""
    
    if not weekly_flow:
        st.error(f"No data available for {report_name}. Please check your data file.")
        return
    
    # Calculate required data structures
    asset_strength = get_asset_strength(weekly_flow)
    pair_strength = calculate_pair_strength(asset_strength)
    normalized = normalize_to_0_100(asset_strength)
    recommendations = generate_trade_recommendations(normalized)
    superior_pairs = generate_momentum_confirmed_trades(weekly_flow, normalized)
    
    # Get date info
    first_date = list(weekly_flow.values())[0]['date']
    date_info = get_date_info(first_date)
    
    # ==================== MARKET SELECTOR ====================
    st.markdown("## 🎯 Market Explorer: Net Positions Over Time")
    st.markdown("### Click any market button below to see its historical Net Positions (Long − Short)")
    display_date_info(date_info)
    
    # Initialize session state for selected market
    if f'selected_market_{report_name}' not in st.session_state:
        st.session_state[f'selected_market_{report_name}'] = 'CAD'
    
    assets = sorted(asset_list)
    
    cols_per_row = 7
    for i in range(0, len(assets), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, asset in enumerate(assets[i:i+cols_per_row]):
            with cols[j]:
                button_type = "primary" if st.session_state[f'selected_market_{report_name}'] == asset else "secondary"
                if st.button(f"📊 {asset}", key=f"{report_name}_btn_{asset}", use_container_width=True, type=button_type):
                    st.session_state[f'selected_market_{report_name}'] = asset
                    st.rerun()
    
    st.markdown("---")
    
    # ==================== DETAILED MARKET TABLE (FIRST) ====================
    selected_asset = st.session_state[f'selected_market_{report_name}']
    
    st.markdown(f"## 📋 {selected_asset} Detailed Positions History")
    st.markdown("*Total = Long + Short | % Long = (Long / Total) × 100 | % Short = (Short / Total) × 100 | Net Positions = Long - Short*")
    
    detailed_table = create_detailed_market_table(weekly_flow, selected_asset)
    if not detailed_table.empty:
        st.markdown(create_stylish_table(detailed_table, f"{selected_asset} Positions History"), unsafe_allow_html=True)
    else:
        st.info(f"No detailed data available for {selected_asset}")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== NET POSITIONS CHART (SECOND) ====================
    dates, net_positions, long_positions, short_positions = get_market_historical_data(weekly_flow, selected_asset)
    
    if dates and net_positions:
        chart = create_net_positions_chart(selected_asset, dates, net_positions, long_positions, short_positions)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.info(f"No historical chart data available for {selected_asset}")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== KEY METRICS ====================
    st.markdown("## 📈 Key Metrics")
    display_date_info(date_info)
    
    col1, col2, col3, col4 = st.columns(4)
    
    bullish_assets = sum(1 for d in weekly_flow.values() if d['weighted_flow'] > 0.3)
    bearish_assets = sum(1 for d in weekly_flow.values() if d['weighted_flow'] < -0.3)
    reversals = sum(1 for d in weekly_flow.values() if d['reversal_signal'] is not None)
    total_pairs = len(pair_strength)
    
    with col1:
        st.metric("📈 Bullish Assets", bullish_assets)
    with col2:
        st.metric("📉 Bearish Assets", bearish_assets)
    with col3:
        st.metric("🔄 Reversal Signals", reversals)
    with col4:
        st.metric("🔗 Total Pairs", total_pairs)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== ASSET STRENGTH CHART ====================
    st.markdown("## 📊 Asset Strength Analysis")
    display_date_info(date_info)
    fig1 = create_asset_strength_chart(asset_strength, f"{report_name} - Asset Strength by Weighted Flow")
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== ASSET PAIRS TABLE ====================
    st.markdown("## 📈 Asset Pairs - Strength Index")
    st.markdown("**Positive = Buy Base | Negative = Sell Base**")
    display_date_info(date_info)
    
    st.markdown("### Currency Pairs")
    sorted_pairs = sorted(pair_strength.items(), key=lambda x: x[1], reverse=True)
    currency_pairs_list = [(k, v) for k, v in sorted_pairs if k not in ['XAUUSD', 'XAGUSD', 'SP500USD', 'NAS100USD', 'DJIAUSD', 'BTCUSD']]
    
    currency_df = pd.DataFrame(currency_pairs_list, columns=['Pair', 'Strength %'])
    currency_df['Direction'] = currency_df['Strength %'].apply(lambda x: '🟢 BULLISH' if x > 0 else '🔴 BEARISH' if x < 0 else '⚪ NEUTRAL')
    currency_df['Strength %'] = currency_df['Strength %'].apply(lambda x: f"{x:+.2f}%")
    
    st.markdown(create_stylish_table(currency_df, "Currency Pairs - Sorted by Strength"), unsafe_allow_html=True)
    
    # Index & Commodity Pairs
    st.markdown("### Index & Commodity Pairs (vs USD)")
    index_commodity_pairs = [(k, v) for k, v in sorted_pairs if k in ['SP500USD', 'NAS100USD', 'DJIAUSD', 'XAUUSD', 'XAGUSD', 'BTCUSD']]
    idx_comm_data = []
    for pair, value in index_commodity_pairs:
        display_name = pair.replace('USD', ' vs USD')
        if pair == 'SP500USD':
            display_name = "S&P 500 vs USD"
        elif pair == 'NAS100USD':
            display_name = "NASDAQ-100 vs USD"
        elif pair == 'DJIAUSD':
            display_name = "DOW JONES vs USD"
        elif pair == 'XAUUSD':
            display_name = "GOLD vs USD"
        elif pair == 'XAGUSD':
            display_name = "SILVER vs USD"
        elif pair == 'BTCUSD':
            display_name = "BITCOIN vs USD"
        idx_comm_data.append({
            'Asset': display_name,
            'Pair': pair,
            'Strength %': f"{value:+.2f}%",
            'Signal': '🟢 BULLISH' if value > 0 else '🔴 BEARISH'
        })
    idx_comm_df = pd.DataFrame(idx_comm_data)
    st.markdown(create_stylish_table(idx_comm_df, "Index & Commodity Pairs vs USD"), unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== TRADE RECOMMENDATIONS ====================
    st.markdown("## 🎯 Trade Recommendations")
    display_date_info(date_info)
    
    if len(recommendations) > 0:
        st.markdown("### 🔥 Priority Trades (Highest Flow Differential)")
        display_df = recommendations.head(12).copy()
        display_df['Differential'] = display_df['Differential'].apply(lambda x: f"{x:+.1f}%")
        st.markdown(create_stylish_table(display_df, "Trade Recommendations - Sorted by Differential"), unsafe_allow_html=True)
        
        if len(recommendations) > 0:
            best_trade = recommendations.iloc[0]
            st.success(f"🎯 **BEST TRADE:** {best_trade['Action']} {best_trade['Pair']} | Differential: {best_trade['Differential']:+.1f}% | Confidence: {best_trade['Confidence']}")
    else:
        st.info("No clear trade opportunities detected this week")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== FLOW ANALYSIS TABLE ====================
    st.markdown("## 💰 Flow Analysis")
    st.markdown("**Positive = ACCUMULATING (Buying) | Negative = DISTRIBUTING (Selling)**")
    display_date_info(date_info)
    
    flow_data = []
    for market, data in sorted(weekly_flow.items(), key=lambda x: x[1]['weighted_flow'], reverse=True):
        asset = data['currency']
        if asset and asset != 'BRENT':
            if data['weighted_flow'] > 0.3:
                indicator = "🟢"
            elif data['weighted_flow'] < -0.3:
                indicator = "🔴"
            else:
                indicator = "⚪"
            
            flow_data.append({
                'Asset': f"{indicator} {asset}",
                'Weighted Flow %': f"{data['weighted_flow']:+.2f}%",
                'Action': data['action'],
                'Conviction': data['conviction'],
                'OI Momentum %': f"{data['oi_momentum_pct']:+.1f}%",
                'Net Position %': f"{data['net_position_pct']:+.1f}%",
                'Δ Long': f"{data['change_long']:+,.0f}",
                'Δ Short': f"{data['change_short']:+,.0f}",
                '4W MA': f"{data['ma_4week']:+.2f}%",
                'Flow Change': f"{data['flow_change']:+.2f}%",
                'Signal': data['reversal_signal'][:40] if data['reversal_signal'] else "-"
            })
    
    flow_df = pd.DataFrame(flow_data)
    st.markdown(create_stylish_table(flow_df, f"{report_name} Flow Analysis - Sorted by Weighted Flow"), unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== REVERSAL SIGNALS ====================
    st.markdown("## 🔄 Reversal & Momentum Signals")
    display_date_info(date_info)
    
    reversals = [d for d in flow_data if d['Signal'] != "-"]
    if reversals:
        reversal_df = pd.DataFrame(reversals)
        st.markdown(create_stylish_table(reversal_df, "Assets Showing Reversal/Momentum Signals"), unsafe_allow_html=True)
    else:
        st.info("No strong reversal signals detected this week")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== SUPERIOR TRADES ====================
    st.markdown("## 🏆 Superior & Momentum-Confirmed Trades")
    st.markdown("**These trades have accelerating momentum - HIGHEST QUALITY SETUPS**")
    display_date_info(date_info)
    
    if superior_pairs:
        st.markdown("### 🔥 Superior Trades (Both sides accelerating)")
        
        superior_data = []
        for trade in superior_pairs[:10]:
            superior_data.append({
                'Pair': trade['Pair'],
                'Differential': f"{trade['Differential']:+.1f}%",
                'Bullish Asset': trade['Base'],
                'Bullish Flow': f"{trade['Base_Flow']:+.2f}%",
                'Bearish Asset': trade['Quote'],
                'Bearish Flow': f"{trade['Quote_Flow']:+.2f}%"
            })
        
        superior_df = pd.DataFrame(superior_data)
        st.markdown(create_stylish_table(superior_df, "Superior Trades - Sorted by Differential"), unsafe_allow_html=True)
        
        if superior_pairs:
            best = superior_pairs[0]
            st.success(f"🎯 **PRIMARY CURRENCY TRADE:** {best['Pair']}\n\nReason: {best['Base']} is accelerating bullish, {best['Quote']} is accelerating bearish")
    else:
        st.info("No superior trades detected this week")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== QUICK SUMMARY ====================
    st.markdown("## 📊 Quick Summary")
    display_date_info(date_info)
    
    col1, col2 = st.columns(2)
    
    norm_currencies = {k: v for k, v in normalized.items() if k not in ['XAU', 'XAG', 'NAS100', 'SP500', 'DJIA', 'BRENT', 'BITCOIN']}
    
    with col1:
        if norm_currencies:
            strongest = max(norm_currencies.items(), key=lambda x: x[1])
            weakest = min(norm_currencies.items(), key=lambda x: x[1])
            
            st.markdown(f'<p style="color: #ffffff"><strong>✅ STRONGEST CURRENCY:</strong> <span style="color: #00ff88;">{strongest[0]}</span> (<span style="color: #00ff88;">{strongest[1]:.1f}%</span>)</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #ffffff"><strong>❌ WEAKEST CURRENCY:</strong> <span style="color: #ff4444;">{weakest[0]}</span> (<span style="color: #ff4444;">{weakest[1]:.1f}%</span>)</p>', unsafe_allow_html=True)
            
            if superior_pairs:
                st.markdown(f'<p style="color: #ffffff"><strong>🎯 PRIMARY CURRENCY TRADE:</strong> <span style="color: #00ff88;">{superior_pairs[0]["Pair"]}</span> (MOMENTUM-CONFIRMED)</p>', unsafe_allow_html=True)
    
    with col2:
        top_3_bullish = sorted_pairs[:3]
        top_3_bearish = sorted_pairs[-3:]
        
        st.markdown('<p style="color: #ffffff"><strong>📈 TOP 3 BULLISH PAIRS:</strong></p>', unsafe_allow_html=True)
        for pair, value in top_3_bullish:
            st.markdown(f'<p style="color: #ffffff">🟢 <span style="color: #00ff88;">{pair}: {value:+.2f}%</span></p>', unsafe_allow_html=True)
        
        st.markdown('<p style="color: #ffffff"><strong>📉 TOP 3 BEARISH PAIRS:</strong></p>', unsafe_allow_html=True)
        for pair, value in top_3_bearish:
            st.markdown(f'<p style="color: #ffffff">🔴 <span style="color: #ff4444;">{pair}: {value:+.2f}%</span></p>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==================== DETAILED ASSET SUMMARY ====================
    with st.expander("📋 Detailed Asset Summary"):
        summary_data = []
        for market, data in weekly_flow.items():
            if data['currency']:
                action_color = "🟢" if data['action'] == "ACCUMULATING" else "🔴" if data['action'] == "DISTRIBUTING" else "⚪"
                summary_data.append({
                    'Asset': data['currency'],
                    'Weighted Flow %': f"{data['weighted_flow']:+.2f}%",
                    'Action': f"{action_color} {data['action']}",
                    'Conviction': data['conviction'],
                    'Net Position %': f"{data['net_position_pct']:+.1f}%",
                    'OI Momentum %': f"{data['oi_momentum_pct']:+.1f}%",
                    'Percentile 1Y': f"{data['percentile_1y']:.0f}%",
                    'Z-Score': f"{data['z_score']:+.2f}"
                })
        summary_df = pd.DataFrame(summary_data)
        summary_df['Weighted Flow Value'] = summary_df['Weighted Flow %'].str.replace('%', '').str.replace('+', '').astype(float)
        summary_df = summary_df.sort_values('Weighted Flow Value', ascending=False)
        summary_df = summary_df.drop('Weighted Flow Value', axis=1)
        st.markdown(create_stylish_table(summary_df, "Complete Asset Summary - Sorted by Weighted Flow"), unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## 📊 Report Selector")
        st.markdown("Choose which COT report to analyze:")
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This dashboard analyzes two different COT datasets:
        
        **Leveraged Funds Report**
        - Data from: `Leverage.xlsx`
        - Tracks: Hedge Funds, CTAs, Large Speculators
        
        **NonCommercials Report**
        - Data from: `annual.xls`
        - Tracks: Non-Commercial traders (Large Speculators)
        
        Both reports use the same methodology but from different data sources.
        """)
        
        st.markdown("---")
        st.markdown("**Color Legend:**")
        st.markdown("- 🟢 <span style='color: #00ff88;'>Green: Bullish / Positive momentum</span>", unsafe_allow_html=True)
        st.markdown("- 🔴 <span style='color: #ff4444;'>Red: Bearish / Negative momentum</span>", unsafe_allow_html=True)
        st.markdown("- ⚪ <span style='color: #ffaa00;'>Yellow: Neutral</span>", unsafe_allow_html=True)
        st.markdown("- ⚪ <span style='color: #ffffff;'>White: Default text</span>", unsafe_allow_html=True)
    
    # Main Title
    st.title("📊 COT Analysis Dashboard - Dual Report")
    st.markdown("### Leveraged Funds vs Non-Commercials Analysis")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Create tabs for the two reports
    tab1, tab2 = st.tabs(["💰 Leveraged Funds Report", "📈 NonCommercials Report"])
    
    # Tab 1: Leveraged Funds
    with tab1:
        st.markdown("## Leveraged Funds (Hedge Funds, CTAs, Large Speculators)")
        st.markdown("Data source: `FinFutYY.xls`")
        
        with st.spinner("Loading Leveraged Funds data..."):
            df_leverage = load_leverage_data()
            weekly_flow_leverage = calculate_leverage_flow(df_leverage)
            
            # Get assets list
            assets_leverage = sorted([data['currency'] for market, data in weekly_flow_leverage.items() if data['currency']])
        
        render_report(weekly_flow_leverage, "LeveragedFunds", assets_leverage)
    
    # Tab 2: Non-Commercials
    with tab2:
        st.markdown("## Non-Commercials (Large Speculators)")
        st.markdown("Data source: `annual.xls`")
        
        with st.spinner("Loading Non-Commercial data..."):
            df_noncomm = load_noncommercial_data()
            weekly_flow_noncomm = calculate_noncommercial_flow(df_noncomm)
            
            # Get assets list
            assets_noncomm = sorted([data['currency'] for market, data in weekly_flow_noncomm.items() if data['currency'] and data['currency'] != 'BRENT'])
        
        render_report(weekly_flow_noncomm, "NonCommercials", assets_noncomm)

if __name__ == "__main__":
    main()
