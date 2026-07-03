"""
MétéoTrader Pro - Plateforme Trading Électricité
Design Cursor · Machine Learning · Recommandations Pro
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import pytz

# Components
from components_utils import display_clock_header
from src.trading.advanced_recommendations import AdvancedTradingAdvisor

# Configuration
st.set_page_config(
    page_title="MétéoTrader Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS DESIGN CURSOR (COMPLET)
# ==========================================

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
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
        border-right: 1px solid var(--border-subtle);
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
    
    /* Info/Warning/Success boxes */
    .stAlert {
        background-color: var(--bg-secondary);
        border-left: 3px solid var(--accent-orange);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

@st.cache_data(ttl=3600)
def load_data():
    """Charge données depuis APIs RTE + Open-Meteo"""
    sys.path.append('.')
    from src.data.fetch_apis_oauth import fetch_all_data
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    with st.spinner('📊 Récupération des données (RTE + Open-Meteo)...'):
        df = fetch_all_data(str(start_date), str(end_date))
    
    return df

@st.cache_resource
def init_database():
    """Initialise SQLite database"""
    from src.data.database import PriceDatabase
    os.makedirs('data', exist_ok=True)
    return PriceDatabase('data/meteotrader.db')

def train_model(df):
    """Entraîne modèle ML (Random Forest + XGBoost)"""
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    
    # Features engineering
    df_ml = df.copy()
    df_ml['hour'] = df_ml['timestamp'].dt.hour
    df_ml['day_of_week'] = df_ml['timestamp'].dt.dayofweek
    df_ml['month'] = df_ml['timestamp'].dt.month
    df_ml['is_weekend'] = (df_ml['day_of_week'] >= 5).astype(int)
    df_ml['is_peak_hour'] = ((df_ml['hour'] >= 18) & (df_ml['hour'] <= 20)).astype(int)
    
    # Features disponibles
    feature_columns = [
        'temperature_c', 'wind_speed_kmh', 'solar_radiation_wm2',
        'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour'
    ]
    
    # Ajouter production si disponible
    prod_cols = [c for c in df_ml.columns if 'production_gw' in c and c != 'total_production_gw']
    if prod_cols:
        feature_columns.extend(prod_cols)
    
    # Ajouter demand
    if 'demand_gw' in df_ml.columns:
        feature_columns.append('demand_gw')
    
    # Filtrer features disponibles
    feature_columns = [f for f in feature_columns if f in df_ml.columns]
    
    # Préparer X et y
    X = df_ml[feature_columns].fillna(0)
    y = df_ml['price_eur_mwh']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entraîner
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Prédictions
    y_pred = model.predict(X_test)
    
    # Métriques
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return model, X_test, y_test, y_pred, feature_columns, df_ml, {'rmse': rmse, 'mae': mae, 'r2': r2}

# ==========================================
# HEADER
# ==========================================

# Horloge minimaliste avec timer
display_clock_header()

st.title("⚡ MétéoTrader Pro")
st.markdown("### 🎯 Plateforme Professionnelle de Trading Électricité")
st.markdown("*Intelligence Artificielle · Météo · Recommandations Temps Réel*")
st.divider()

# ==========================================
# CHARGEMENT DONNÉES
# ==========================================

try:
    df = load_data()
    db = init_database()
    model, X_test, y_test, y_pred, features, df_full, metrics = train_model(df)
    
    # Stocker historique dans DB
    actual_prices = df_full[df_full['timestamp'] < pd.Timestamp.now()][['timestamp', 'price_eur_mwh']].copy()
    actual_prices.columns = ['timestamp', 'price']
    db.store_actual_prices(actual_prices)
    
    st.success(f"✅ **Données chargées** : {len(df)} heures | **Modèle ML** : R² = {metrics['r2']:.3f}, MAE = {metrics['mae']:.2f} €/MWh")
    
except Exception as e:
    st.error(f"❌ Erreur chargement: {e}")
    st.stop()

# ==========================================
# TABS PRINCIPAUX
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⏱️ Timeline Live",
    "🤖 Recommandations ML",
    "🌡️ Météo & Impact",
    "⚡ Production Mix",
    "🎯 Analyse Modèle"
])

# ==========================================
# TAB 1: TIMELINE LIVE
# ==========================================

with tab1:
    st.subheader("⏱️ Timeline Unifiée - Passé, Présent & Futur")
    
    st.info("🚀 **Live** : Vue complète des prix (historique réel → prédictions futures) avec tracking accuracy")
    
    # Générer prédictions futures
    try:
        from src.models.predict_future import predict_future_prices
        
        with st.spinner('🔮 Génération prédictions futures...'):
            future_predictions = predict_future_prices(
                model=model,
                feature_columns=features,
                historical_data=df_full,
                days=2
            )
        
        # Stocker prédictions dans DB
        if not future_predictions.empty:
            pred_df = future_predictions[['timestamp', 'predicted_price']].copy()
            pred_df.columns = ['timestamp', 'predicted_price']
            pred_df['model_version'] = 'RF_v1'
            db.store_predictions(pred_df)
        
        # Récupérer timeline unifiée depuis DB
        timeline = db.get_unified_timeline(hours=60)  # 60h (30h passé + 30h futur)
        
        if not timeline.empty:
            now = pd.Timestamp.now()
            past_data = timeline[timeline['timestamp'] <= now]
            future_data = timeline[timeline['timestamp'] > now]
            
            # Graphique Timeline
            fig_timeline = go.Figure()
            
            # Prix réels (passé)
            if not past_data.empty and 'actual_price' in past_data.columns:
                fig_timeline.add_trace(go.Scatter(
                    x=past_data['timestamp'],
                    y=past_data['actual_price'],
                    name='Prix Réel',
                    line=dict(color='#3b82f6', width=3),
                    mode='lines'
                ))
            
            # Prix prédits (futur)
            if not future_data.empty and 'predicted_price' in future_data.columns:
                fig_timeline.add_trace(go.Scatter(
                    x=future_data['timestamp'],
                    y=future_data['predicted_price'],
                    name='Prix Prédit',
                    line=dict(color='#ff6b35', width=3, dash='dash'),
                    mode='lines'
                ))
            
            # Ligne "NOW"
            y_min = min(timeline['actual_price'].min() if 'actual_price' in timeline.columns else 0,
                       timeline['predicted_price'].min() if 'predicted_price' in timeline.columns else 0)
            y_max = max(timeline['actual_price'].max() if 'actual_price' in timeline.columns else 100,
                       timeline['predicted_price'].max() if 'predicted_price' in timeline.columns else 100)
            
            fig_timeline.add_trace(go.Scatter(
                x=[now, now],
                y=[y_min, y_max],
                mode='lines',
                name='NOW',
                line=dict(color='rgba(255, 255, 255, 0.5)', width=2, dash='dot'),
                hoverinfo='skip',
                showlegend=False
            ))
            
            # Bulle NOW sur la courbe
            closest_past = past_data[past_data['timestamp'] <= now].tail(1)
            if not closest_past.empty and 'actual_price' in closest_past.columns:
                current_price = closest_past['actual_price'].iloc[0]
                
                fig_timeline.add_trace(go.Scatter(
                    x=[now],
                    y=[current_price],
                    mode='markers+text',
                    name='MAINTENANT',
                    marker=dict(
                        size=18,
                        color='white',
                        line=dict(color='#ff6b35', width=3)
                    ),
                    text=['NOW'],
                    textposition='top center',
                    textfont=dict(size=12, color='white'),
                    hovertemplate=f'<b>MAINTENANT</b><br>{now.strftime("%d %b %H:%M")}<br>Prix: <b>{current_price:.2f} €/MWh</b><extra></extra>',
                    showlegend=False
                ))
            
            # Layout
            x_min = now - pd.Timedelta(hours=30)
            x_max = now + pd.Timedelta(hours=30)
            
            fig_timeline.update_layout(
                title=dict(
                    text=f"<b>Timeline Unifiée</b> · {now.strftime('%d %b %H:%M')}",
                    font=dict(size=20, color='white'),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title="",
                yaxis_title="Prix (€/MWh)",
                hovermode='x unified',
                template='plotly_dark',
                height=600,
                paper_bgcolor='rgba(12, 12, 12, 0.9)',
                plot_bgcolor='rgba(22, 22, 22, 0.6)',
                xaxis=dict(range=[x_min, x_max]),
                font=dict(family='Arial, sans-serif', color='#e3e3e3')
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Métriques accuracy
            st.subheader("📊 Accuracy Modèle")
            
            if 'historical_predicted_price' in past_data.columns:
                hist_with_pred = past_data[past_data['historical_predicted_price'].notna()]
                if not hist_with_pred.empty:
                    mae = (hist_with_pred['historical_predicted_price'] - hist_with_pred['actual_price']).abs().mean()
                    mape = (mae / hist_with_pred['actual_price'].mean()) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("🎯 MAE", f"{mae:.2f} €/MWh", help="Erreur Absolue Moyenne")
                    
                    with col2:
                        st.metric("📉 MAPE", f"{mape:.1f}%", help="Erreur en %")
                    
                    with col3:
                        accuracy = 100 - mape if mape < 100 else 0
                        st.metric("✅ Précision", f"{accuracy:.1f}%")
        
    except Exception as e:
        st.error(f"❌ Erreur timeline: {e}")

# ==========================================
# TAB 2: RECOMMANDATIONS ML
# ==========================================

with tab2:
    st.subheader("🤖 Recommandations ML Professionnelles")
    
    st.info("🎯 **Système Expert** : Analyse ML pour recommandations BUY/SELL/HOLD basées sur 9 règles de décision")
    
    try:
        # Créer advisor
        advisor = AdvancedTradingAdvisor(model=model, features=features)
        
        # Générer recommandation
        recommendation = advisor.generate_recommendation(
            df_historical=df_full,
            df_future_predictions=future_predictions if 'future_predictions' in locals() else pd.Series([])
        )
        
        # Afficher carte recommandation
        from components_utils import format_recommendation_card
        
        current_price = df_full['price_eur_mwh'].iloc[-1]
        future_prices = future_predictions['predicted_price'].values[:24] if 'future_predictions' in locals() and not future_predictions.empty else [current_price]
        
        format_recommendation_card(recommendation, current_price, future_prices)
        
        # Opportunités d'arbitrage
        st.markdown("---")
        st.subheader("💰 Opportunités d'Arbitrage Intraday")
        
        if 'future_predictions' in locals() and not future_predictions.empty:
            opportunities = advisor.find_optimal_trading_windows(future_predictions, window_hours=6)
            
            if opportunities['arbitrage_opportunities']:
                for i, (buy_time, sell_time, gain) in enumerate(opportunities['arbitrage_opportunities'][:3], 1):
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**#{i} · Gain: +{gain:.2f} €/MWh**")
                    
                    with col2:
                        st.success(f"📈 Acheter: {buy_time if isinstance(buy_time, str) else buy_time.strftime('%H:%M')}")
                    
                    with col3:
                        st.warning(f"📉 Vendre: {sell_time if isinstance(sell_time, str) else sell_time.strftime('%H:%M')}")
            else:
                st.info("Aucune opportunité d'arbitrage significative détectée pour le moment.")
        
    except Exception as e:
        st.error(f"❌ Erreur recommandations: {e}")

# ==========================================
# TAB 3: MÉTÉO & IMPACT
# ==========================================

with tab3:
    exec(open('app.py').read().split('# TAB 6: MÉTÉO')[1].split('with tab7:')[0])

# ==========================================
# TAB 4: PRODUCTION MIX
# ==========================================

with tab4:
    exec(open('app.py').read().split('with tab7:')[1].split('# TAB 8')[0])

# ==========================================
# TAB 5: ANALYSE MODÈLE
# ==========================================

with tab5:
    st.subheader("🎯 Performance du Modèle ML")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 R² Score", f"{metrics['r2']:.3f}", help="Variance expliquée (0-1)")
    
    with col2:
        st.metric("📉 RMSE", f"{metrics['rmse']:.2f} €/MWh", help="Erreur quadratique moyenne")
    
    with col3:
        st.metric("🎯 MAE", f"{metrics['mae']:.2f} €/MWh", help="Erreur absolue moyenne")
    
    st.markdown("---")
    
    # Feature importance
    st.subheader("📊 Importance des Features")
    
    importances = pd.DataFrame({
        'Feature': features,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    fig_imp = px.bar(
        importances.head(15),
        x='Importance',
        y='Feature',
        orientation='h',
        title="Top 15 Features les Plus Importantes",
        template='plotly_dark',
        color='Importance',
        color_continuous_scale='Oranges'
    )
    fig_imp.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_imp, use_container_width=True)
    
    # Scatter prédictions vs réel
    st.subheader("📈 Prédictions vs Prix Réels")
    
    fig_scatter = px.scatter(
        x=y_test,
        y=y_pred,
        labels={'x': 'Prix Réel (€/MWh)', 'y': 'Prix Prédit (€/MWh)'},
        title=f"Précision du Modèle (R² = {metrics['r2']:.3f})",
        template='plotly_dark',
        trendline='ols',
        trendline_color_override='#ff6b35'
    )
    fig_scatter.add_trace(go.Scatter(
        x=[y_test.min(), y_test.max()],
        y=[y_test.min(), y_test.max()],
        mode='lines',
        name='Parfait',
        line=dict(color='white', dash='dash', width=2)
    ))
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption("⚡ MétéoTrader Pro · Données: RTE + Open-Meteo · ML: Random Forest · Mis à jour chaque heure")

