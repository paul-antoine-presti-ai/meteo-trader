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

from dotenv import load_dotenv

# Charger variables d'environnement
load_dotenv()
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
             "⚖️ Gap Offre/Demande", "💰 Arbitrage", "📊 Mes Contrats", "🤖 Modèles ML"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown(f"**{datetime.now().strftime('%H:%M')}**")
        st.markdown(f"{datetime.now().strftime('%d %B %Y')}")
        
        return page

# ==========================================
# PAGES
# ==========================================

def page_overview(df_france, prices_europe, predictions_europe, supply_demand):
    """Vue d'ensemble"""
    st.markdown("# 🏠 Vue d'Ensemble")
    st.markdown("Tous vos marchés en un coup d'œil")
    
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

def page_europe(prices_europe, predictions_europe):
    """Page Europe"""
    st.markdown("# 🌍 Marchés Européens")
    
    # Stats par pays
    st.markdown("### 📊 Prix par Pays")
    
    cols = st.columns(3)
    
    for idx, (country, df) in enumerate(prices_europe.items()):
        if not df.empty:
            with cols[idx % 3]:
                avg_price = df['price_eur_mwh'].mean()
                min_price = df['price_eur_mwh'].min()
                max_price = df['price_eur_mwh'].max()
                
                st.markdown(f"""
                <div class="glass-card">
                    <h3>🏴 {country}</h3>
                    <p style="font-size:2rem; margin:10px 0;">{avg_price:.1f}€/MWh</p>
                    <p style="color:#a0a0a0;">Min: {min_price:.1f}€ • Max: {max_price:.1f}€</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Graphique détaillé
    st.markdown("### 📈 Évolution Prix (7 jours)")
    
    fig = go.Figure()
    colors = {'FR': '#3b82f6', 'DE': '#10b981', 'ES': '#f97316'}
    
    for country, df in prices_europe.items():
        if not df.empty:
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['price_eur_mwh'],
                mode='lines',
                name=f"🏴 {country}",
                line=dict(color=colors.get(country, '#ffffff'), width=2)
            ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0c0c0c',
        plot_bgcolor='#161616',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def page_france(df_france, model, features):
    """Page France détaillée"""
    st.markdown("# 🇫🇷 France Détaillée")
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📊 Production Mix", "🌡️ Météo", "📈 Prédictions"])
    
    with tab1:
        st.markdown("### Mix Énergétique France")
        
        # Production par type
        prod_cols = [c for c in df_france.columns if 'production_gw' in c and c != 'total_production_gw']
        
        if prod_cols:
            latest = df_france.iloc[-1]
            
            fig = go.Figure(data=[go.Pie(
                labels=[c.replace('_production_gw', '').upper() for c in prod_cols],
                values=[latest[c] for c in prod_cols],
                hole=0.4
            )])
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#0c0c0c',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if 'temperature_c' in df_france.columns:
            st.markdown("### Données Météo")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_france['timestamp'],
                y=df_france['temperature_c'],
                mode='lines',
                name='Température',
                line=dict(color='#f97316')
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#0c0c0c',
                plot_bgcolor='#161616',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Prédictions 48h")
        
        from src.data.fetch_europe import fetch_weather_forecast
        
        try:
            weather_forecast = fetch_weather_forecast('FR', days=2)
            
            if not weather_forecast.empty:
                # Prédire
                hourly_patterns = df_france.tail(168).groupby('hour').agg({
                    'nuclear_production_gw': 'mean',
                    'total_production_gw': 'mean',
                    'demand_gw': 'mean'
                }).to_dict()
                
                forecast_df = weather_forecast.copy()
                forecast_df['hour'] = forecast_df['timestamp'].dt.hour
                forecast_df['nuclear_production_gw'] = forecast_df['hour'].map(hourly_patterns['nuclear_production_gw'])
                forecast_df['total_production_gw'] = forecast_df['hour'].map(hourly_patterns['total_production_gw'])
                forecast_df['demand_gw'] = forecast_df['hour'].map(hourly_patterns['demand_gw'])
                
                forecast_df['day_of_week'] = forecast_df['timestamp'].dt.dayofweek
                forecast_df['month'] = forecast_df['timestamp'].dt.month
                forecast_df['is_weekend'] = (forecast_df['day_of_week'] >= 5).astype(int)
                forecast_df['is_peak_hour'] = ((forecast_df['hour'] >= 18) & (forecast_df['hour'] <= 20)).astype(int)
                forecast_df['temp_extreme'] = ((forecast_df['temperature_c'] < 5) | (forecast_df['temperature_c'] > 25)).astype(int)
                forecast_df['renewable_share'] = 0.2
                forecast_df['production_demand_gap'] = forecast_df['demand_gw'] - forecast_df['total_production_gw']
                
                X_future = forecast_df[features].fillna(0)
                predicted_prices = model.predict(X_future)
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=forecast_df['timestamp'],
                    y=predicted_prices,
                    mode='lines',
                    name='Prix Prédit',
                    line=dict(color='#ff6b35', width=2)
                ))
                
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#0c0c0c',
                    plot_bgcolor='#161616',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Prédictions non disponibles")

def page_gap(supply_demand, prices_europe):
    """Page Gap Offre/Demande"""
    st.markdown("# ⚖️ Gap Offre/Demande")
    st.markdown("Analyse de l'équilibre Production vs Consommation")
    
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

def page_ml(df_france, model, features, X_test, y_test):
    """Page Modèles ML"""
    st.markdown("# 🤖 Modèles ML")
    
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
        df_france, prices_europe, predictions_europe, supply_demand = load_all_data()
        model, features, df_full, X_test, y_test = train_models(df_france)
    except Exception as e:
        st.error(f"❌ Erreur chargement: {e}")
        return
    
    # Navigation
    page = show_sidebar()
    
    # Router
    if page == "🏠 Vue d'Ensemble":
        page_overview(df_france, prices_europe, predictions_europe, supply_demand)
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
    elif page == "🤖 Modèles ML":
        page_ml(df_france, model, features, X_test, y_test)

if __name__ == "__main__":
    main()

