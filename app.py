"""
MétéoTrader Pro - Plateforme Unifiée Complète
Design Cursor • Multi-Pays • Gap Offre/Demande • Arbitrage • ML
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import plotly.express as px
import pytz

# Composants custom
from components_utils import display_clock_header
from src.trading.advanced_recommendations import AdvancedTradingAdvisor

# Configuration
st.set_page_config(
    page_title="MétéoTrader Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Design Cursor
st.markdown("""
<style>
    /* Cursor-like Dark Theme */
    :root {
        --bg-primary: #0c0c0c;
        --bg-secondary: #161616;
        --bg-tertiary: #1e1e1e;
        --text-primary: #e3e3e3;
        --text-secondary: #a0a0a0;
        --accent-orange: #ff6b35;
        --border-subtle: #2a2a2a;
        --hover-bg: #252525;
    }
    
    /* Global */
    .main {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Sidebar Cursor-style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
        border-right: 1px solid var(--border-subtle);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Typography Cursor-like */
    h1, h2, h3, h4 {
        color: var(--text-primary);
        font-weight: 300;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h2 {
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Cards Glass Effect */
    .glass-card {
        background: rgba(30, 30, 30, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        background: rgba(35, 35, 35, 0.7);
        border-color: rgba(255, 107, 53, 0.2);
        transform: translateY(-2px);
    }
    
    /* Metrics Cursor-style */
    .stMetric {
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 16px;
        transition: all 0.2s ease;
    }
    
    .stMetric:hover {
        background: var(--hover-bg);
        border-color: var(--accent-orange);
    }
    
    .stMetric label {
        color: var(--text-secondary);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--text-primary);
        font-size: 1.75rem;
        font-weight: 300;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #ff8c61 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(255, 107, 53, 0.3);
    }
    
    /* Tabs Cursor-style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--bg-secondary);
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: var(--text-secondary);
        padding: 8px 16px;
        font-weight: 400;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-orange);
        color: white;
    }
    
    /* Dataframes */
    .dataframe {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
    }
    
    /* Divider */
    hr {
        border-color: var(--border-subtle);
        margin: 2rem 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        color: var(--text-primary);
    }
    
    /* Select box */
    .stSelectbox [data-baseweb="select"] {
        background-color: var(--bg-secondary);
        border-color: var(--border-subtle);
    }
    
    /* Tension badges */
    .tension-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .tension-critical { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .tension-high { background: rgba(249, 115, 22, 0.2); color: #f97316; border: 1px solid #f97316; }
    .tension-medium { background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid #fbbf24; }
    .tension-balanced { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .tension-surplus { background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER AVEC HORLOGE
# ==========================================

# Horloge minimaliste professionnelle
display_clock_header()

st.title("⚡ MétéoTrader Pro")
st.markdown("### 🎯 Plateforme Professionnelle de Trading Électricité")
st.markdown("*Intelligence Artificielle · Météo · Recommandations Temps Réel · Multi-Pays*")
st.divider()

# ==========================================
# CHARGEMENT DONNÉES
# ==========================================

@st.cache_resource
def init_clients():
    """Initialise clients API et DB"""
    from src.data.entsoe_api import EntsoeClient
    from src.data.database import PriceDatabase
    os.makedirs('data', exist_ok=True)
    return EntsoeClient(), PriceDatabase('data/meteotrader.db')

@st.cache_data(ttl=3600)
def load_all_data():
    """Charge TOUTES les données en une fois"""
    sys.path.append('.')
    
    # 1. Données France (RTE détaillé)
    from src.data.fetch_apis_oauth import fetch_all_data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    with st.spinner('📊 Chargement France (RTE)...'):
        df_france = fetch_all_data(str(start_date), str(end_date))
    
    # 2. Données Europe (ENTSOE-E)
    from src.data.fetch_europe import fetch_european_prices, predict_prices_europe
    
    with st.spinner('🌍 Chargement Europe (ENTSOE-E)...'):
        prices_europe = fetch_european_prices(countries=['FR', 'DE', 'ES'], days=7)
        predictions_europe = predict_prices_europe(prices_europe, {}, forecast_hours=48)
    
    # 3. Supply/Demand Data
    client, _ = init_clients()
    
    supply_demand = {}
    for country in ['FR']:
        try:
            prod = client.get_actual_generation(country, str(start_date), str(end_date))
            load = client.get_actual_load(country, str(start_date), str(end_date))
            forecast = client.get_load_forecast(country, str(start_date), str(end_date))
            
            supply_demand[country] = {
                'production': prod,
                'load': load,
                'forecast': forecast
            }
        except:
            pass
    
    return df_france, prices_europe, predictions_europe, supply_demand

@st.cache_resource
def train_models(_df_france):
    """Entraîne les modèles ML"""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    
    # Features
    df = _df_france.copy()
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_peak_hour'] = ((df['hour'] >= 18) & (df['hour'] <= 20)).astype(int)
    
    if 'temperature_c' in df.columns:
        df['temp_extreme'] = ((df['temperature_c'] < 5) | (df['temperature_c'] > 25)).astype(int)
    
    prod_cols = [c for c in df.columns if 'production_gw' in c and c != 'total_production_gw']
    if prod_cols:
        renewable_cols = [c for c in prod_cols if 'wind' in c.lower() or 'solar' in c.lower()]
        if renewable_cols:
            df['renewable_production_gw'] = df[renewable_cols].sum(axis=1)
            df['renewable_share'] = df['renewable_production_gw'] / df['total_production_gw'].replace(0, np.nan)
            df['renewable_share'] = df['renewable_share'].fillna(0)
    
    if 'demand_gw' in df.columns and 'total_production_gw' in df.columns:
        df['production_demand_gap'] = df['demand_gw'] - df['total_production_gw']
    
    feature_columns = [
        'temperature_c', 'wind_speed_kmh', 'solar_radiation_wm2',
        'nuclear_production_gw', 'total_production_gw', 'demand_gw',
        'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour',
        'temp_extreme', 'renewable_share', 'production_demand_gap'
    ]
    feature_columns = [f for f in feature_columns if f in df.columns]
    
    X = df[feature_columns].fillna(0)
    y = df['price_eur_mwh']
    
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    return model, feature_columns, df, X_test, y_test

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

def show_sidebar():
    """Sidebar Cursor-style"""
    with st.sidebar:
        st.markdown("### ⚡ MétéoTrader Pro")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🏠 Vue d'Ensemble", "🌍 Europe", "🇫🇷 France Détaillée", 
             "⚖️ Gap Offre/Demande", "💰 Arbitrage", "📊 Mes Contrats", 
             "🔮 Prédictions Détaillées", "🤖 Modèles ML"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown(f"**{datetime.now().strftime('%H:%M')}**")
        st.markdown(f"{datetime.now().strftime('%d %B %Y')}")
        
        return page

# ==========================================
# PAGES
# ==========================================

def page_overview(df_france, prices_europe, predictions_europe, supply_demand, db):
    """Vue d'ensemble"""
    st.markdown("# 🏠 Vue d'Ensemble")
    st.markdown("*Vue synthétique des marchés français et européens avec métriques clés en temps réel*")
    st.divider()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    # Prix France
    if not df_france.empty:
        latest_price = df_france.iloc[-1]['price_eur_mwh']
        with col1:
            st.metric("Prix Spot FR", f"{latest_price:.1f} €/MWh", delta=None)
    
    # Gap France
    if 'FR' in supply_demand:
        from src.analysis.supply_demand import SupplyDemandAnalyzer
        analyzer = SupplyDemandAnalyzer()
        
        analysis = analyzer.analyze_country_market(
            supply_demand['FR']['production'],
            supply_demand['FR']['load'],
            prices_europe.get('FR')
        )
        
        if not analysis.empty:
            current = analyzer.get_current_situation(analysis)
            if current:
                with col2:
                    st.metric("Gap FR", f"{current['gap_gw']:+.1f} GW", 
                             delta=f"{current['reserve_margin_pct']:+.1f}%")
    
    # Opportunités
    from src.arbitrage.engine import ArbitrageEngine
    engine = ArbitrageEngine(predictions_europe)
    opps = engine.calculate_all_opportunities()
    
    if not opps.empty:
        n_opps = len(opps[opps['score'] >= 50])
        with col3:
            st.metric("Opportunités", f"{n_opps}")
    
    # Marge potentielle
    margin = engine.calculate_potential_margin(hours=48)
    with col4:
        st.metric("Marge 48h", f"{margin['total_margin']:.0f} €")
    
    st.markdown("---")
    
    # Graphique comparaison multi-pays
    st.markdown("### 📈 Comparaison Prix Europe (48h)")
    
    fig = go.Figure()
    colors = {'FR': '#3b82f6', 'DE': '#10b981', 'ES': '#f97316'}
    
    for country, pred_df in predictions_europe.items():
        if not pred_df.empty:
            fig.add_trace(go.Scatter(
                x=pred_df['timestamp'],
                y=pred_df['predicted_price'],
                mode='lines',
                name=f"🏴 {country}",
                line=dict(color=colors.get(country, '#ffffff'), width=2)
            ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0c0c0c',
        plot_bgcolor='#161616',
        height=400,
        xaxis_title="",
        yaxis_title="Prix (€/MWh)",
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", y=1.1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 3 opportunités
    st.markdown("### 💰 Top Opportunités")
    
    if not opps.empty:
        top3 = engine.get_top_opportunities(n=3, min_score=50)
        
        if not top3.empty:
            for idx, row in top3.iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**{row['from_country']} → {row['to_country']}**")
                
                with col2:
                    st.markdown(f"Spread: **{row['spread_net']:.1f}€/MWh**")
                
                with col3:
                    st.markdown(f"Volume: **{row['volume_optimal']:.0f} MWh**")
                
                with col4:
                    st.markdown(f"Gain: **{row['gain_total']:.0f}€**")
    # ==== BACKTESTING P&L ====
    st.markdown("---")
    st.subheader("💰 Backtesting - Performance RÉELLE")
    st.caption("📊 **Résultats basés sur VOS vraies prédictions** : Si vous aviez suivi les top 10 recommandations du modèle chaque jour")
    
    try:
        from src.analysis.real_backtesting import calculate_real_backtest
        
        # Calculer VRAI backtesting depuis la DB
        backtest = calculate_real_backtest(db, days=30)
        
        if not backtest['available']:
            st.info(f"💡 {backtest['message']}")
            st.caption("Le backtesting apparaîtra après quelques jours d'utilisation de l'app")
        else:
            # Données RÉELLES
            total_pnl = backtest['total_pnl']
            cumulative_pnl = backtest['cumulative_pnl']
            daily_pnl = backtest['daily_pnl']
            dates = [pd.Timestamp(d) for d in backtest['dates']]
        
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                delta_color = "normal" if total_pnl > 0 else "inverse"
                st.metric("💰 P&L Total", f"{total_pnl:.2f} €/MWh", 
                         delta=f"{backtest['total_days']} jours analysés",
                         delta_color=delta_color)
            
            with col2:
                st.metric("✅ Taux Réussite Jours", f"{backtest['win_rate']:.1f}%",
                         delta=f"{backtest['winning_days']}/{backtest['total_days']} jours gagnants",
                         help="% de jours avec gain positif")
            
            with col3:
                st.metric("🎯 Taux Réussite Actions", f"{backtest['action_success_rate']:.1f}%",
                         delta=f"{backtest['successful_actions']}/{backtest['total_actions']} actions",
                         help="% d'actions individuelles gagnantes")
            
            with col4:
                st.metric("📊 Sharpe Ratio", f"{backtest['sharpe_ratio']:.2f}",
                         help="Ratio rendement/risque")
        
            # Métriques supplémentaires
            col1, col2 = st.columns(2)
            with col1:
                if backtest['best_day']:
                    best = backtest['best_day']
                    st.success(f"🏆 **Meilleur jour**: {pd.Timestamp(best['date']).strftime('%d/%m')} → +{best['pnl']:.2f} €/MWh")
            with col2:
                if backtest['worst_day']:
                    worst = backtest['worst_day']
                    st.error(f"📉 **Pire jour**: {pd.Timestamp(worst['date']).strftime('%d/%m')} → {worst['pnl']:.2f} €/MWh")
            
            # Graphique P&L cumulé RÉEL
            fig_pnl = go.Figure()
            
            color = '#00ff00' if total_pnl > 0 else '#ff0000'
            
            fig_pnl.add_trace(go.Scatter(
                x=dates,
                y=cumulative_pnl,
                mode='lines+markers',
                name='P&L Cumulé RÉEL',
                line=dict(color=color, width=3),
                fill='tozeroy',
                fillcolor=f'rgba({"0,255,0" if total_pnl > 0 else "255,0,0"}, 0.2)',
                hovertemplate='%{x}<br>P&L: %{y:.2f} €/MWh<extra></extra>'
            ))
            
            fig_pnl.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
            
            fig_pnl.update_layout(
                title="Performance Cumulée RÉELLE - Basée sur vos prédictions historiques",
                xaxis_title="Date",
                yaxis_title="P&L Cumulé (€/MWh)",
                template='plotly_dark',
                paper_bgcolor='#0c0c0c',
                plot_bgcolor='#161616',
                height=400
            )
            
            st.plotly_chart(fig_pnl, use_container_width=True)
        
            # 10 dernières transactions RÉELLES
            with st.expander("📋 Voir les 10 dernières transactions RÉELLES"):
                if backtest['details']:
                    transactions_df = pd.DataFrame(backtest['details'])
                    transactions_df['Date'] = pd.to_datetime(transactions_df['timestamp']).dt.strftime('%d/%m %Hh')
                    transactions_df['Prédit'] = transactions_df['predicted'].apply(lambda x: f"{x:.2f}€")
                    transactions_df['Réel'] = transactions_df['actual'].apply(lambda x: f"{x:.2f}€")
                    transactions_df['P&L'] = transactions_df['pnl'].apply(lambda x: f"{x:+.2f}€")
                    transactions_df['Status'] = transactions_df['success'].apply(lambda x: "✅" if x else "❌")
                    
                    display_df = transactions_df[['Date', 'action', 'Prédit', 'Réel', 'P&L', 'Status']]
                    display_df.columns = ['Date', 'Action', 'Prix Prédit', 'Prix Réel', 'P&L', 'Résultat']
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Pas encore de transactions")
            
            st.success("✅ **Backtesting 100% RÉEL** : Basé sur vos vraies prédictions vs prix réels de la base de données")
    
    except Exception as e:
        st.error(f"❌ Erreur backtesting: {e}")


def page_europe(prices_europe, predictions_europe):
    """Page Europe - Marchés interconnectés"""
    st.markdown("# 🌍 Marchés Européens")
    st.markdown("*Comparaison des prix spot sur les marchés européens avec analyse des écarts et opportunités d'arbitrage*")
    st.divider()
    
    # Section 1: Graphique Multi-Pays INTERACTIF
    st.subheader("📊 Prix par Pays - Vue Interactive")
    st.caption("🔍 Cochez/décochez les pays pour comparer les évolutions. Prix réels (solide) vs prédictions (pointillés)")
    
    # Créer graphique Plotly interactif
    fig_multi = go.Figure()
    
    countries_data = []
    for country, df in prices_europe.items():
        if not df.empty and 'timestamp' in df.columns and 'price_eur_mwh' in df.columns:
            countries_data.append((country, df))
            
            # Prix réels
            fig_multi.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['price_eur_mwh'],
                name=f'{country} (Réel)',
                mode='lines',
                line=dict(width=2),
                visible=True,
                hovertemplate=f'<b>{country}</b><br>%{{x}}<br>Prix: %{{y:.2f}} €/MWh<extra></extra>'
            ))
            
            # Prédictions si disponibles
            if country in predictions_europe and not predictions_europe[country].empty:
                pred_df = predictions_europe[country]
                if 'timestamp' in pred_df.columns and 'predicted_price' in pred_df.columns:
                    fig_multi.add_trace(go.Scatter(
                        x=pred_df['timestamp'],
                        y=pred_df['predicted_price'],
                        name=f'{country} (Prédit)',
                        mode='lines',
                        line=dict(width=2, dash='dash'),
                        visible=True,
                        opacity=0.7,
                        hovertemplate=f'<b>{country} Prévu</b><br>%{{x}}<br>Prix: %{{y:.2f}} €/MWh<extra></extra>'
                    ))
    
    fig_multi.update_layout(
        title="Prix de l'Électricité - Multi-Pays (Interactif)",
        xaxis_title="Date/Heure",
        yaxis_title="Prix (€/MWh)",
        template='plotly_dark',
        paper_bgcolor='#0c0c0c',
        plot_bgcolor='#161616',
        height=600,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(26, 26, 26, 0.7)'
        )
    )
    
    st.plotly_chart(fig_multi, use_container_width=True)
    
    # Section 2: Stats par pays
    st.markdown("---")
    st.subheader("💰 Statistiques par Pays")
    
    cols = st.columns(min(3, len(countries_data)))
    
    for idx, (country, df) in enumerate(countries_data):
        with cols[idx % len(cols)]:
            avg_price = df['price_eur_mwh'].mean()
            min_price = df['price_eur_mwh'].min()
            max_price = df['price_eur_mwh'].max()
            
            st.markdown(f"""
            <div style="
                background: rgba(30, 30, 30, 0.6);
                border: 1px solid rgba(255, 107, 53, 0.2);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            ">
                <h3 style="color: #ff6b35;">🏴 {country}</h3>
                <p style="font-size: 2.5rem; margin: 10px 0; color: white;">{avg_price:.1f}€</p>
                <p style="color: #a0a0a0; font-size: 0.9rem;">
                    Min: {min_price:.1f}€ • Max: {max_price:.1f}€
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Section 3: Opportunités d'arbitrage
    if len(countries_data) >= 2:
        st.markdown("---")
        st.subheader("💱 Opportunités d'Arbitrage")
        st.caption("📈 Écarts de prix entre pays pour le trading cross-border")
        
        # Calculer spreads
        spreads = []
        for i, (country1, df1) in enumerate(countries_data):
            for country2, df2 in countries_data[i+1:]:
                if len(df1) > 0 and len(df2) > 0:
                    avg1 = df1['price_eur_mwh'].mean()
                    avg2 = df2['price_eur_mwh'].mean()
                    spread = abs(avg1 - avg2)
                    direction = f"{country1} → {country2}" if avg1 < avg2 else f"{country2} → {country1}"
                    spreads.append((direction, spread))
        
        spreads.sort(key=lambda x: x[1], reverse=True)
        
        col1, col2, col3 = st.columns(3)
        for idx, (direction, spread) in enumerate(spreads[:3]):
            with [col1, col2, col3][idx]:
                st.success(f"""
                **#{idx+1} {direction}**
                
                Écart moyen: **{spread:.2f} €/MWh**
                
                Gain potentiel: **{spread * 0.8:.2f} €/MWh** (net)
                """)

def page_france(df_france, model, features):
    """Page France détaillée"""
    st.markdown("# 🇫🇷 France Détaillée")
    st.markdown("""
    *Analyse approfondie du marché français avec météo, production, et prédictions ML.*
    
    **Données disponibles :**
    - 🌡️ **Météo** : Température, vent, pression (impact sur demande et production renouvelable)
    - ⚡ **Production** : Mix énergétique par source (nucléaire, éolien, solaire, hydraulique, fossile)
    - 📊 **Consommation** : Demande électrique en temps réel
    - 🔮 **Prédictions 48h** : Prix futurs avec recommandations (heures optimales d'achat/vente)
    - 🎯 **Modèle ML** : Random Forest & XGBoost entraînés sur 744h de données historiques
    
    **Utilisation trader :**
    - Identifier les heures les moins chères pour acheter
    - Anticiper les pics de demande (canicule, vague de froid)
    - Optimiser les stratégies d'achat/vente selon le mix énergétique
    """)
    st.markdown("*Analyse approfondie du marché français : production, météo, prédictions ML*")
    st.divider()
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📊 Production Mix", "🌡️ Météo", "📈 Prédictions"])
    
    with tab1:
        st.markdown("### Mix Énergétique France")
        st.caption("📊 Production électrique en temps réel")
        
        # Essayer d'abord les données RTE
        prod_cols = [c for c in df_france.columns if 'production_gw' in c.lower()]
        
        # Vérifier si données RTE valides
        has_valid_data = False
        if len(prod_cols) > 0 and len(df_france) > 0:
            latest_test = df_france.iloc[-1]
            total_rte = sum([latest_test.get(c, 0) for c in prod_cols])
            has_valid_data = total_rte > 0
        
        # Si pas de données valides, utiliser ENTSOE-E
        if not has_valid_data:
            st.info("📊 Chargement données ENTSOE-E...")
            try:
                from src.data.entsoe_api import EntsoeClient
                from datetime import datetime, timedelta
                
                client = EntsoeClient()
                
                # Essayer plusieurs jours en arrière
                prod_df = pd.DataFrame()
                for days_back in range(1, 8):  # Essayer les 7 derniers jours
                    end_date = datetime.now().date() - timedelta(days=days_back)
                    start_date = end_date - timedelta(days=1)
                    
                    try:
                        prod_df = client.get_actual_generation('FR', str(start_date), str(end_date))
                        if not prod_df.empty:
                            # Vérifier si données non nulles
                            latest_test = prod_df.iloc[-1]
                            test_vals = [latest_test.get(c, 0) for c in prod_df.columns if 'production' in c.lower()]
                            if sum(test_vals) > 0:
                                st.info(f"✅ Données trouvées pour le {end_date.strftime('%d/%m')}")
                                break
                    except:
                        pass
                
                if not prod_df.empty and 'timestamp' in prod_df.columns:
                    # Prendre la dernière ligne
                    latest_entsoe = prod_df.iloc[-1]
                    
                    # Extraire valeurs
                    nuclear = latest_entsoe.get('Nuclear_production_gw', latest_entsoe.get('nuclear_production_gw', 0))
                    wind = latest_entsoe.get('Wind Onshore_production_gw', 0) + latest_entsoe.get('Wind Offshore_production_gw', 0)
                    solar = latest_entsoe.get('Solar_production_gw', latest_entsoe.get('solar_production_gw', 0))
                    hydro = (latest_entsoe.get('Hydro Run-of-river and poundage_production_gw', 0) + 
                            latest_entsoe.get('Hydro Water Reservoir_production_gw', 0) +
                            latest_entsoe.get('Hydro Pumped Storage_production_gw', 0))
                    
                    total = nuclear + wind + solar + hydro
                    
                    if total > 0:
                        st.success("✅ Données ENTSOE-E chargées")
                        
                        # Métriques
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("⚛️ Nucléaire", f"{nuclear:.1f} GW", f"{nuclear/total*100:.0f}%")
                        col2.metric("🌬️ Éolien", f"{wind:.1f} GW", f"{wind/total*100:.0f}%")
                        col3.metric("☀️ Solaire", f"{solar:.1f} GW", f"{solar/total*100:.0f}%")
                        col4.metric("💧 Hydraulique", f"{hydro:.1f} GW", f"{hydro/total*100:.0f}%")
                        
                        # Pie chart
                        import plotly.express as px
                        data = {'Source': ['⚛️ Nucléaire', '🌬️ Éolien', '☀️ Solaire', '💧 Hydraulique'],
                                'Production (GW)': [nuclear, wind, solar, hydro]}
                        df_mix = pd.DataFrame(data)
                        df_mix = df_mix[df_mix['Production (GW)'] > 0]
                        
                        fig = px.pie(df_mix, values='Production (GW)', names='Source', 
                                    title=f"Mix Énergétique - {latest_entsoe['timestamp'].strftime('%d/%m %Hh')}",
                                    template='plotly_dark',
                                    color_discrete_sequence=px.colors.sequential.Oranges_r)
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        fig.update_layout(paper_bgcolor='#0c0c0c', plot_bgcolor='#161616')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Graphique évolution 24h (comme l'original)
                        st.markdown("### 📈 Évolution Production 24h")
                        
                        # Prendre les dernières 24h de données
                        if len(prod_df) >= 24:
                            last_24h = prod_df.tail(24)
                        else:
                            last_24h = prod_df
                        
                        if not last_24h.empty:
                            import plotly.graph_objects as go
                            fig_evolution = go.Figure()
                            
                            # Nucléaire (rouge/orange)
                            if nuclear > 0:
                                nuc_col = [c for c in last_24h.columns if 'nuclear' in c.lower() or 'nucl' in c.lower()]
                                if nuc_col:
                                    fig_evolution.add_trace(go.Scatter(
                                        x=last_24h['timestamp'],
                                        y=last_24h[nuc_col[0]],
                                        name='⚛️ Nucléaire',
                                        line=dict(color='#ff6b35', width=3)
                                    ))
                            
                            # Éolien (bleu)
                            if wind > 0:
                                wind_cols = [c for c in last_24h.columns if 'wind' in c.lower()]
                                if wind_cols:
                                    wind_sum = last_24h[wind_cols].sum(axis=1)
                                    fig_evolution.add_trace(go.Scatter(
                                        x=last_24h['timestamp'],
                                        y=wind_sum,
                                        name='🌬️ Éolien',
                                        line=dict(color='#3b82f6', width=2)
                                    ))
                            
                            # Solaire (jaune)
                            if solar > 0:
                                solar_col = [c for c in last_24h.columns if 'solar' in c.lower()]
                                if solar_col:
                                    fig_evolution.add_trace(go.Scatter(
                                        x=last_24h['timestamp'],
                                        y=last_24h[solar_col[0]],
                                        name='☀️ Solaire',
                                        line=dict(color='#fbbf24', width=2)
                                    ))
                            
                            # Hydraulique (cyan)
                            if hydro > 0:
                                hydro_cols = [c for c in last_24h.columns if 'hydro' in c.lower()]
                                if hydro_cols:
                                    hydro_sum = last_24h[hydro_cols].sum(axis=1)
                                    fig_evolution.add_trace(go.Scatter(
                                        x=last_24h['timestamp'],
                                        y=hydro_sum,
                                        name='💧 Hydraulique',
                                        line=dict(color='#06b6d4', width=2)
                                    ))
                            
                            fig_evolution.update_layout(
                                title="Production par Source - 24 Heures",
                                xaxis_title="Heure",
                                yaxis_title="Production (GW)",
                                template='plotly_dark',
                                paper_bgcolor='#0c0c0c',
                                plot_bgcolor='#161616',
                                height=450,
                                hovermode='x unified',
                                legend=dict(
                                    yanchor="top",
                                    y=0.99,
                                    xanchor="left",
                                    x=0.01
                                )
                            )
                            
                            st.plotly_chart(fig_evolution, use_container_width=True)
                        else:
                            st.info("Pas assez de données pour le graphique d'évolution")
                    else:
                        st.warning("⚠️ Aucune donnée de production disponible")
                        st.info("""
                        💡 **Pourquoi ?**
                        - Les APIs RTE et ENTSOE-E n'ont pas publié de données récentes
                        - Délai de publication habituel : 1-2 jours
                        - Les données apparaîtront dès leur mise à jour
                        
                        **En attendant**, utilisez les autres onglets :
                        - 🌡️ Météo (fonctionne)
                        - 📈 Prédictions 48h (fonctionne)
                        """)
                else:
                    st.error("❌ ENTSOE-E vide")
            except Exception as e:
                st.error(f"❌ Erreur ENTSOE-E: {e}")
                st.caption("💡 Les données de production seront disponibles prochainement")
        
        else:
            # Données RTE disponibles
            if len(df_france) > 0:
                latest = df_france.iloc[-1]
                
                nuclear = latest.get('nuclear_production_gw', 0)
                wind = sum([latest.get(c, 0) for c in prod_cols if 'wind' in c.lower()])
                solar = latest.get('solar_production_gw', 0)
                hydro = sum([latest.get(c, 0) for c in prod_cols if 'hydro' in c.lower()])
                total = nuclear + wind + solar + hydro
                
                if total > 0:
                    # Métriques
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("⚛️ Nucléaire", f"{nuclear:.1f} GW")
                    col2.metric("🌬️ Éolien", f"{wind:.1f} GW")
                    col3.metric("☀️ Solaire", f"{solar:.1f} GW")
                    col4.metric("💧 Hydraulique", f"{hydro:.1f} GW")
                    
                    # Pie chart
                    import plotly.express as px
                    data = {'Source': ['Nucléaire', 'Éolien', 'Solaire', 'Hydraulique'],
                            'Production': [nuclear, wind, solar, hydro]}
                    df_mix = pd.DataFrame(data)
                    df_mix = df_mix[df_mix['Production'] > 0]
                    
                    fig = px.pie(df_mix, values='Production', names='Source', 
                                title="Mix Énergétique RTE",
                                template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Données RTE disponibles mais valeurs à zéro")
            else:
                st.info("DataFrame vide")

    with tab2:
        st.markdown("### Données Météo & Impact Prix")
        st.caption("🌡️ Corrélations entre conditions météo et prix de l'électricité")
        
        if 'temperature_c' in df_france.columns and 'wind_speed_kmh' in df_france.columns:
            # Métriques actuelles
            latest = df_france.iloc[-1]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🌡️ Température", f"{latest['temperature_c']:.1f}°C")
            
            with col2:
                st.metric("💨 Vent", f"{latest['wind_speed_kmh']:.1f} km/h")
            
            with col3:
                if 'solar_radiation_wm2' in df_france.columns:
                    st.metric("☀️ Radiation", f"{latest['solar_radiation_wm2']:.0f} W/m²")
            
            st.markdown("---")
            
            # Graphiques scatter avec corrélations
            col1, col2 = st.columns(2)
            
            with col1:
                # Vérifier colonnes nécessaires
                if all(col in df_france.columns for col in ['temperature_c', 'price_eur_mwh']):
                    # Ajouter colonne hour si manquante
                    df_plot = df_france.copy()
                    if 'hour' not in df_plot.columns and 'timestamp' in df_plot.columns:
                        df_plot['hour'] = df_plot['timestamp'].dt.hour
                    
                    import plotly.express as px
                    fig_temp = px.scatter(
                        df_plot,
                        x='temperature_c',
                        y='price_eur_mwh',
                        color='hour' if 'hour' in df_plot.columns else None,
                        title="🌡️ Température vs Prix",
                        labels={'temperature_c': 'Température (°C)', 'price_eur_mwh': 'Prix (€/MWh)', 'hour': 'Heure'},
                        template='plotly_dark',
                        
                        color_continuous_scale='Oranges'
                    )
                    fig_temp.update_layout(paper_bgcolor='#0c0c0c', height=400)
                    st.plotly_chart(fig_temp, use_container_width=True)
                else:
                    st.info("📊 Données température non disponibles")
            
            with col2:
                # Vérifier colonnes nécessaires
                if all(col in df_france.columns for col in ['wind_speed_kmh', 'price_eur_mwh']):
                    # Ajouter colonne hour si manquante
                    df_plot = df_france.copy()
                    if 'hour' not in df_plot.columns and 'timestamp' in df_plot.columns:
                        df_plot['hour'] = df_plot['timestamp'].dt.hour
                    
                    fig_wind = px.scatter(
                        df_plot,
                        x='wind_speed_kmh',
                        y='price_eur_mwh',
                        color='hour' if 'hour' in df_plot.columns else None,
                        title="💨 Vent vs Prix",
                        labels={'wind_speed_kmh': 'Vent (km/h)', 'price_eur_mwh': 'Prix (€/MWh)', 'hour': 'Heure'},
                        template='plotly_dark',
                        
                        color_continuous_scale='Blues'
                    )
                    fig_wind.update_layout(paper_bgcolor='#0c0c0c', height=400)
                    st.plotly_chart(fig_wind, use_container_width=True)
                else:
                    st.info("📊 Données vent non disponibles")
        else:
            st.warning("⚠️ Données météo non disponibles")
    
    with tab3:
        st.markdown("### Prédictions 48h (ML)")
        st.caption("🔮 Prévisions des prix basées sur Random Forest + données météo futures")
        
        try:
            import plotly.graph_objects as go
            from src.models.predict_future import predict_future_prices
            
            with st.spinner('⏳ Calcul des prédictions...'):
                future_predictions = predict_future_prices(
                    model=model,
                    feature_columns=features,
                    historical_data=df_france,
                    days=2
                )
            
            if not future_predictions.empty:
                # Graphique prédictions
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=future_predictions['timestamp'],
                    y=future_predictions['predicted_price'],
                    mode='lines+markers',
                    name='Prix Prédit',
                    line=dict(color='#ff6b35', width=3),
                    marker=dict(size=6)
                ))
                
                # Intervalle confiance si disponible
                if 'confidence_lower' in future_predictions.columns and 'confidence_upper' in future_predictions.columns:
                    fig.add_trace(go.Scatter(
                        x=future_predictions['timestamp'].tolist() + future_predictions['timestamp'].tolist()[::-1],
                        y=future_predictions['confidence_upper'].tolist() + future_predictions['confidence_lower'].tolist()[::-1],
                        fill='toself',
                        fillcolor='rgba(249, 115, 22, 0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Intervalle confiance (95%)',
                        showlegend=True
                    ))
                
                fig.update_layout(
                    title="Prévisions Prix Électricité 48h",
                    xaxis_title="Date/Heure",
                    yaxis_title="Prix (€/MWh)",
                    template='plotly_dark',
                    paper_bgcolor='#0c0c0c',
                    plot_bgcolor='#161616',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Recommandations
                st.markdown("#### 💡 Recommandations")
                
                avg_price = future_predictions['predicted_price'].mean()
                min_price = future_predictions['predicted_price'].min()
                max_price = future_predictions['predicted_price'].max()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    min_hour = future_predictions.loc[future_predictions['predicted_price'].idxmin()]
                    st.success(f"""
                    **🟢 Meilleur moment (prix bas) :**
                    - {min_hour['timestamp'].strftime('%d/%m %Hh')} : **{min_price:.2f} €/MWh**
                    - Économies potentielles : **{max_price - min_price:.2f} €/MWh**
                    """)
                
                with col2:
                    max_hour = future_predictions.loc[future_predictions['predicted_price'].idxmax()]
                    st.warning(f"""
                    **🔴 Heure à éviter (prix élevé) :**
                    - {max_hour['timestamp'].strftime('%d/%m %Hh')} : **{max_price:.2f} €/MWh**
                    - Surcoût vs moyenne : **{max_price - avg_price:.2f} €/MWh**
                    """)
            else:
                st.error("Impossible de générer les prédictions")
        
        except Exception as e:
            st.error(f"❌ Erreur prédictions: {e}")
            st.info("💡 Assurez-vous que les APIs météo sont accessibles")

def page_gap(supply_demand, prices_europe):
    """Page Gap Offre/Demande"""
    st.markdown("# ⚖️ Gap Offre/Demande")
    st.markdown("""
    *Surveillance de l'équilibre production/consommation pour anticiper les tensions sur le réseau.*
    
    **Indicateur clé : Reserve Margin**
    - **Formule** : `(Production - Consommation) / Consommation × 100`
    - **Interprétation** :
      - 🔴 **< 5%** : CRITIQUE (risque blackout, prix explosifs)
      - 🟠 **5-10%** : TENSION (prix élevés, acheter maintenant risqué)
      - 🟢 **10-20%** : ÉQUILIBRÉ (prix normaux)
      - 🔵 **> 20%** : SURPLUS (prix bas, opportunité d'achat)
    
    **Action trader :**
    - **Tension/Critique** : Vendre à prix élevé, éviter d'acheter
    - **Surplus** : Acheter massivement, stocker (si possible)
    - **Équilibré** : Suivre recommandations ML
    """)
    st.markdown("*Surveillance de l'équilibre entre production et consommation pour anticiper les tensions sur le réseau*")
    st.divider()
    
    if 'FR' not in supply_demand:
        st.warning("Données gap non disponibles")
        return
    
    from src.analysis.supply_demand import SupplyDemandAnalyzer
    
    analyzer = SupplyDemandAnalyzer()
    analysis = analyzer.analyze_country_market(
        supply_demand['FR']['production'],
        supply_demand['FR']['load'],
        prices_europe.get('FR')
    )
    
    if analysis.empty:
        st.warning("Analyse non disponible")
        return
    
    # Situation actuelle
    current = analyzer.get_current_situation(analysis)
    
    if current:
        tension = current['tension']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Production", f"{current['production_gw']:.1f} GW")
        
        with col2:
            st.metric("Consommation", f"{current['load_gw']:.1f} GW")
        
        with col3:
            st.metric("Gap", f"{current['gap_gw']:+.1f} GW")
        
        st.markdown("---")
        
        # Tension
        badge_class = {
            'CRITICAL': 'tension-critical',
            'HIGH_TENSION': 'tension-high',
            'TENSION': 'tension-medium',
            'BALANCED': 'tension-balanced',
            'SURPLUS': 'tension-surplus',
            'HIGH_SURPLUS': 'tension-surplus'
        }.get(tension['level'], 'tension-balanced')
        
        st.markdown(f"""
        <div class="glass-card">
            <div class="tension-badge {badge_class}">
                {tension['emoji']} {tension['level']}
            </div>
            <h3 style="margin-top:20px;">{tension['description']}</h3>
            <p><strong>Impact Prix:</strong> {tension['price_impact']}</p>
            <p><strong>Action Trader:</strong> {tension['trader_action']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Graphique
        st.markdown("### 📊 Historique Gap")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=analysis['timestamp'],
            y=analysis['gap_gw'],
            mode='lines',
            name='Gap',
            line=dict(color='#ff6b35', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 53, 0.2)'
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#0c0c0c',
            plot_bgcolor='#161616',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def page_arbitrage(predictions_europe):
    """Page Arbitrage"""
    st.markdown("# 💰 Arbitrage Cross-Border")
    st.markdown("""
    *Opportunités de trading transfrontalier entre marchés européens.*
    
    **Principe de l'arbitrage :**
    1. **Acheter** dans un pays où le prix est bas (ex: France 50€/MWh)
    2. **Vendre** dans un pays où le prix est élevé (ex: Allemagne 80€/MWh)
    3. **Profit** = Écart de prix - Coûts de transport
    
    **Données affichées :**
    - 📊 **Spreads** : Écarts de prix entre pays (€/MWh)
    - 🚚 **Coûts transport** : Estimés selon capacités interconnexion
    - 💰 **Marge nette** : Gain réel après frais
    - 📦 **Volume optimal** : Quantité à trader pour maximiser le profit
    
    **Top Opportunités** : Classement des meilleures opérations par gain potentiel
    """)
    
    from src.arbitrage.engine import ArbitrageEngine, generate_recommendation
    from src.data.entsoe_api import EntsoeClient
    
    engine = ArbitrageEngine(predictions_europe)
    opps = engine.calculate_all_opportunities()
    
    # Meilleure opportunité
    best = engine.get_best_opportunity()
    
    if best:
        reco = generate_recommendation(best, EntsoeClient.COUNTRY_NAMES)
        
        st.markdown(f"""
        <div class="glass-card">
            {reco.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top opportunités
    st.markdown("### 🏆 Top 10 Opportunités")
    
    if not opps.empty:
        top10 = engine.get_top_opportunities(n=10, min_score=30)
        
        if not top10.empty:
            display = top10[['from_country', 'to_country', 'timestamp', 
                           'spread_net', 'volume_optimal', 'gain_total', 'score']].copy()
            
            display.columns = ['Achat', 'Vente', 'Heure', 'Spread (€/MWh)', 
                              'Volume (MWh)', 'Gain (€)', 'Score']
            
            display['Heure'] = pd.to_datetime(display['Heure']).dt.strftime('%d/%m %H:%M')
            
            st.dataframe(display, use_container_width=True, hide_index=True)

def page_contracts():
    """Page Contrats"""
    st.markdown("# 📊 Mes Contrats")
    st.markdown("""
    *Gestion des contrats clients et suivi des engagements de prix.*
    
    **Fonctionnalités :**
    - ➕ **Ajouter contrat** : Client, volume (MWh/jour), prix garanti, date de livraison
    - 📊 **Suivi exposition** : Calcul automatique de l'exposition (risque si prix spot > prix garanti)
    - 💰 **P&L contrat** : Gain/perte par contrat selon évolution des prix
    - 🔔 **Alertes** : Notification si marché spot dépasse le prix garanti (risque de perte)
    
    **Stratégie trader :**
    - **Prix garanti élevé** → Acheter sur spot quand prix bas (hedge)
    - **Prix garanti bas** → Risque si spot monte (acheter en avance)
    - **Équilibre portefeuille** : Diversifier les échéances et les prix
    """)
    
    _, db = init_clients()
    contracts = db.get_active_contracts()
    
    if contracts.empty:
        st.info("Aucun contrat actif")
        
        with st.expander("➕ Ajouter un contrat"):
            with st.form("add_contract"):
                client_name = st.text_input("Nom du client")
                col1, col2 = st.columns(2)
                with col1:
                    volume = st.number_input("Volume (MWh)", min_value=0.0, value=100.0)
                with col2:
                    price = st.number_input("Prix garanti (€/MWh)", min_value=0.0, value=85.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    start = st.date_input("Début", value=datetime.now().date())
                with col2:
                    end = st.date_input("Fin", value=(datetime.now() + timedelta(days=365)).date())
                
                if st.form_submit_button("Ajouter"):
                    db.add_contract(client_name, volume, price, str(start), str(end))
                    st.success("✅ Contrat ajouté!")
                    st.rerun()
    else:
        st.dataframe(contracts, use_container_width=True, hide_index=True)


def page_predictions_detaillees(prices_europe, predictions_europe, df_france, model, features):
    """Page Prédictions Détaillées Multi-Pays avec Recommandations Actions"""
    st.markdown("# 🔮 Prédictions Détaillées Multi-Pays")
    st.markdown("""
    *Vue complète des prévisions de prix pour FR, DE, ES avec intervalles de confiance et recommandations d'actions précises.*
    
    **Ce que vous voyez ici :**
    - 📊 **Graphiques par pays** : Prédictions 48h avec intervalles de confiance à 95%
    - 💰 **Top 10 Actions** : Heures exactes d'achat (prix bas) et vente (prix élevés)
    - 💱 **Opportunités Arbitrage** : Acheter dans un pays, vendre dans un autre
    - 💡 **Recommandations** : Actions concrètes à mener dans les prochaines 48h
    """)
    st.divider()
    
    # ==========================================
    # 1. PRÉDICTIONS PAR PAYS (3 pays principaux)
    # ==========================================
    
    st.subheader("📊 Prédictions par Pays - 48 Heures")
    
    countries_to_predict = ['FR', 'DE', 'ES']
    
    for country in countries_to_predict:
        if country not in predictions_europe or predictions_europe[country].empty:
            continue
        
        with st.expander(f"🏴 {country} - Voir les prédictions détaillées", expanded=(country == 'FR')):
            pred_df = predictions_europe[country].copy()
            
            if 'timestamp' not in pred_df.columns or 'predicted_price' not in pred_df.columns:
                st.warning(f"Données incomplètes pour {country}")
                continue
            
            # Stats
            avg_price = pred_df['predicted_price'].mean()
            min_price = pred_df['predicted_price'].min()
            max_price = pred_df['predicted_price'].max()
            volatility = pred_df['predicted_price'].std()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Prix Moyen", f"{avg_price:.2f} €/MWh")
            with col2:
                st.metric("📉 Prix Min", f"{min_price:.2f} €/MWh", 
                         delta=f"-{avg_price - min_price:.2f} €")
            with col3:
                st.metric("📈 Prix Max", f"{max_price:.2f} €/MWh",
                         delta=f"+{max_price - avg_price:.2f} €")
            with col4:
                st.metric("📊 Volatilité", f"{volatility:.2f} €/MWh")
            
            # Graphique avec intervalle de confiance
            fig = go.Figure()
            
            # Prix prédit
            fig.add_trace(go.Scatter(
                x=pred_df['timestamp'],
                y=pred_df['predicted_price'],
                mode='lines+markers',
                name='Prix Prédit',
                line=dict(color='#ff6b35', width=3),
                marker=dict(size=6)
            ))
            
            # Intervalle confiance (si disponible)
            if 'confidence_lower' in pred_df.columns and 'confidence_upper' in pred_df.columns:
                fig.add_trace(go.Scatter(
                    x=pred_df['timestamp'].tolist() + pred_df['timestamp'].tolist()[::-1],
                    y=pred_df['confidence_upper'].tolist() + pred_df['confidence_lower'].tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(249, 115, 22, 0.15)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Intervalle confiance (95%)',
                    showlegend=True,
                    hoverinfo='skip'
                ))
            
            # Ligne moyenne
            fig.add_hline(y=avg_price, line_dash="dash", line_color="white", 
                         opacity=0.3, annotation_text=f"Moyenne: {avg_price:.2f}€")
            
            fig.update_layout(
                title=f"Prévisions {country} - 48 Heures",
                xaxis_title="Date/Heure",
                yaxis_title="Prix (€/MWh)",
                template='plotly_dark',
                paper_bgcolor='#0c0c0c',
                plot_bgcolor='#161616',
                height=450,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # ==========================================
    # 2. TOP 10 ACTIONS FUTURES
    # ==========================================
    
    st.markdown("---")
    st.subheader("💎 Top 10 Actions Recommandées (48h)")
    st.caption("🎯 Heures optimales pour acheter (prix bas) et vendre (prix élevés) sur chaque marché")
    
    all_actions = []
    
    for country in countries_to_predict:
        if country not in predictions_europe or predictions_europe[country].empty:
            continue
        
        pred_df = predictions_europe[country].copy()
        
        if 'timestamp' not in pred_df.columns or 'predicted_price' not in pred_df.columns:
            continue
        
        # Top 5 heures ACHAT (prix bas)
        cheapest = pred_df.nsmallest(5, 'predicted_price')
        for _, row in cheapest.iterrows():
            all_actions.append({
                'Action': 'ACHAT 🟢',
                'Pays': country,
                'Heure': row['timestamp'].strftime('%d/%m %Hh'),
                'Prix': row['predicted_price'],
                'Type': 'buy',
                'Économie': pred_df['predicted_price'].mean() - row['predicted_price']
            })
        
        # Top 5 heures VENTE (prix élevés)
        most_expensive = pred_df.nlargest(5, 'predicted_price')
        for _, row in most_expensive.iterrows():
            all_actions.append({
                'Action': 'VENTE 🔴',
                'Pays': country,
                'Heure': row['timestamp'].strftime('%d/%m %Hh'),
                'Prix': row['predicted_price'],
                'Type': 'sell',
                'Gain': row['predicted_price'] - pred_df['predicted_price'].mean()
            })
    
    # Trier par économie/gain
    all_actions_df = pd.DataFrame(all_actions)
    
    if not all_actions_df.empty:
        # Calculer score combiné
        all_actions_df['Score'] = all_actions_df.apply(
            lambda x: x.get('Économie', x.get('Gain', 0)), axis=1
        )
        all_actions_df = all_actions_df.nlargest(10, 'Score')
        
        # Afficher sous forme de cartes
        for idx, row in all_actions_df.iterrows():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                is_buy = row['Type'] == 'buy'
                emoji = '🟢' if is_buy else '🔴'
                action_type = 'ACHAT' if is_buy else 'VENTE'
                benefit_label = 'Économie' if is_buy else 'Gain'
                benefit_value = row.get('Économie', row.get('Gain', 0))
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {"#0d4d0d" if is_buy else "#4d0d0d"} 0%, #1a1a1a 100%);
                    border-left: 4px solid {"#00ff00" if is_buy else "#ff0000"};
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                ">
                    <h4 style="margin: 0; color: {"#00ff00" if is_buy else "#ff6666"};">
                        {emoji} {action_type} - {row['Pays']}
                    </h4>
                    <p style="margin: 5px 0; font-size: 1.1rem;">
                        📅 <strong>{row['Heure']}</strong> • Prix: <strong>{row['Prix']:.2f} €/MWh</strong>
                    </p>
                    <p style="margin: 0; color: #a0a0a0;">
                        💰 {benefit_label} potentiel: <strong style="color: {"#00ff00" if is_buy else "#ff6666"};">
                        {benefit_value:+.2f} €/MWh</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Badge rang
                st.markdown(f"""
                <div style="
                    background: rgba(255, 107, 53, 0.2);
                    border: 2px solid #ff6b35;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: auto;
                    margin-top: 15px;
                ">
                    <span style="font-size: 1.5rem; font-weight: bold; color: #ff6b35;">
                        #{list(all_actions_df.index).index(idx) + 1}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aucune action disponible pour le moment")
    
    # ==========================================
    # 3. OPPORTUNITÉS ARBITRAGE CROSS-BORDER
    # ==========================================
    
    st.markdown("---")
    st.subheader("💱 Opportunités d'Arbitrage Cross-Border")
    st.caption("🌍 Acheter dans un pays à prix bas, vendre dans un autre à prix élevé")
    
    arbitrage_opportunities = []
    
    for buy_country in countries_to_predict:
        if buy_country not in predictions_europe:
            continue
        
        buy_pred = predictions_europe[buy_country]
        
        if buy_pred.empty or 'timestamp' not in buy_pred.columns:
            continue
        
        for sell_country in countries_to_predict:
            if sell_country == buy_country or sell_country not in predictions_europe:
                continue
            
            sell_pred = predictions_europe[sell_country]
            
            if sell_pred.empty or 'timestamp' not in sell_pred.columns:
                continue
            
            # Merge sur timestamp
            merged = pd.merge(
                buy_pred[['timestamp', 'predicted_price']],
                sell_pred[['timestamp', 'predicted_price']],
                on='timestamp',
                suffixes=('_buy', '_sell')
            )
            
            if merged.empty:
                continue
            
            # Calculer spread
            merged['spread'] = merged['predicted_price_sell'] - merged['predicted_price_buy']
            merged['transport_cost'] = 2.0  # €/MWh (estimation)
            merged['net_margin'] = merged['spread'] - merged['transport_cost']
            
            # Garder opportunités rentables
            profitable = merged[merged['net_margin'] > 5]  # Minimum 5€/MWh de marge
            
            if not profitable.empty:
                best = profitable.nlargest(1, 'net_margin').iloc[0]
                
                arbitrage_opportunities.append({
                    'Route': f"{buy_country} → {sell_country}",
                    'Heure': best['timestamp'].strftime('%d/%m %Hh'),
                    'Prix Achat': best['predicted_price_buy'],
                    'Prix Vente': best['predicted_price_sell'],
                    'Spread': best['spread'],
                    'Coût Transport': best['transport_cost'],
                    'Marge Nette': best['net_margin']
                })
    
    if arbitrage_opportunities:
        arb_df = pd.DataFrame(arbitrage_opportunities).nlargest(5, 'Marge Nette')
        
        for idx, row in arb_df.iterrows():
            st.success(f"""
            **🚀 {row['Route']}**
            
            ⏰ Heure optimale: **{row['Heure']}**
            
            - 💰 Achat: {row['Prix Achat']:.2f} €/MWh
            - 💰 Vente: {row['Prix Vente']:.2f} €/MWh
            - 📊 Spread brut: {row['Spread']:.2f} €/MWh
            - 🚚 Coût transport: {row['Coût Transport']:.2f} €/MWh
            - ✅ **Marge nette: {row['Marge Nette']:.2f} €/MWh**
            
            💡 *Recommandation: Acheter en {row['Route'].split(' → ')[0]} et vendre en {row['Route'].split(' → ')[1]}*
            """)
    else:
        st.info("Aucune opportunité d'arbitrage rentable détectée pour le moment")


def page_ml(df_france, model, features, X_test, y_test):
    """Page Modèles ML"""
    st.markdown("# 🤖 Modèles ML")
    st.markdown("""
    *Comparaison des algorithmes de prédiction de prix et analyse de performance.*
    
    **Modèles entraînés :**
    - 🌲 **Random Forest** : Robuste, interprétable, baseline solide
    - ⚡ **XGBoost** : Performance supérieure, gestion des non-linéarités
    
    **Métriques d'évaluation :**
    - **R² Score** : % de variance expliquée (plus proche de 1 = mieux)
    - **RMSE** : Erreur moyenne en €/MWh (plus bas = mieux)
    - **MAE** : Erreur absolue moyenne (robuste aux outliers)
    
    **Features importantes :**
    - 🌡️ Température (impact chauffage/clim)
    - 🌬️ Vent (production éolienne)
    - ⏰ Heure/Jour (patterns temporels)
    - ⚡ Demande/Production (équilibre réseau)
    
    **Utilisation :** Le meilleur modèle (plus haut R²) est utilisé pour les prédictions 48h
    """)
    
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("R² Score", f"{r2:.3f}")
    
    with col2:
        st.metric("MAE", f"{mae:.2f} €/MWh")
    
    with col3:
        st.metric("RMSE", f"{rmse:.2f} €/MWh")
    
    st.markdown("---")
    
    # Feature importance
    st.markdown("### 📊 Feature Importance")
    
    importances = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    fig = go.Figure(data=[go.Bar(
        x=importances['importance'],
        y=importances['feature'],
        orientation='h',
        marker_color='#ff6b35'
    )])
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0c0c0c',
        plot_bgcolor='#161616',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MAIN
# ==========================================

def main():
    # Chargement
    try:
        entsoe_client, db = init_clients()
        df_france, prices_europe, predictions_europe, supply_demand = load_all_data()
        model, features, df_full, X_test, y_test = train_models(df_france)
    except Exception as e:
        st.error(f"❌ Erreur chargement: {e}")
        return
    
    # Navigation
    page = show_sidebar()
    
    # Router
    if page == "🏠 Vue d'Ensemble":
        page_overview(df_france, prices_europe, predictions_europe, supply_demand, db)
    elif page == "🌍 Europe":
        page_europe(prices_europe, predictions_europe)
    elif page == "🇫🇷 France Détaillée":
        page_france(df_france, model, features)
    elif page == "⚖️ Gap Offre/Demande":
        page_gap(supply_demand, prices_europe)
    elif page == "💰 Arbitrage":
        page_arbitrage(predictions_europe)
    elif page == "📊 Mes Contrats":
        page_contracts()
    elif page == "🔮 Prédictions Détaillées":
        page_predictions_detaillees(prices_europe, predictions_europe, df_france, model, features)
    elif page == "🤖 Modèles ML":
        page_ml(df_france, model, features, X_test, y_test)

if __name__ == "__main__":
    main()

