"""
MétéoTrader Pro - Trading Dashboard Minimaliste
Interface simple et efficace pour traders d'électricité
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Configuration page
st.set_page_config(
    page_title="MétéoTrader Pro - Trading",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Minimaliste Dark Mode
st.markdown("""
<style>
    /* Background sombre */
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 300;
    }
    
    h1 {
        font-size: 2rem;
        margin-bottom: 2rem;
    }
    
    /* Sections */
    .section-card {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    /* Metrics */
    .stMetric {
        background-color: #1a1a1a;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #2a2a2a;
    }
    
    .stMetric label {
        color: #888888;
        font-size: 0.875rem;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 300;
    }
    
    /* Boutons */
    .stButton > button {
        background-color: #f97316;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #ea580c;
        box-shadow: 0 0 20px rgba(249, 115, 22, 0.5);
    }
    
    /* Recommandation Card */
    .reco-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #f97316;
        border-radius: 16px;
        padding: 32px;
        margin: 24px 0;
    }
    
    .reco-buy {
        border-color: #10b981;
    }
    
    .reco-hold {
        border-color: #6b7280;
    }
    
    .reco-hedge {
        border-color: #ef4444;
    }
    
    /* Alertes */
    .alert-high {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    
    .alert-medium {
        background-color: rgba(249, 115, 22, 0.1);
        border-left: 4px solid #f97316;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    
    .alert-low {
        background-color: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    
    /* Tables */
    .dataframe {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FONCTIONS
# ==========================================

@st.cache_resource
def init_database():
    """Initialise base de données"""
    os.makedirs('data', exist_ok=True)
    from src.data.database import PriceDatabase
    return PriceDatabase('data/meteotrader.db')

@st.cache_data(ttl=3600)
def load_market_data():
    """Charge données marché"""
    sys.path.append('.')
    from src.data.fetch_apis_oauth import fetch_all_data
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    with st.spinner('📊 Chargement données marché...'):
        df = fetch_all_data(str(start_date), str(end_date))
    
    return df

def get_current_price(df):
    """Récupère prix actuel (ou dernier disponible)"""
    if df.empty:
        return 75.0  # Valeur par défaut
    
    recent = df[df['timestamp'] <= datetime.now()].sort_values('timestamp', ascending=False)
    if not recent.empty:
        return float(recent.iloc[0]['price_eur_mwh'])
    return 75.0

def get_future_predictions(db):
    """Récupère prédictions futures depuis DB"""
    try:
        from src.models.predict_future import predict_future_prices
        from sklearn.ensemble import RandomForestRegressor
        import joblib
        
        # Charger modèle (ou créer un simple si pas dispo)
        model_path = 'models/price_model.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
        else:
            # Modèle simple par défaut
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        predictions = predict_future_prices(model, hours=48)
        return predictions
    except Exception as e:
        st.warning(f"Prédictions non disponibles: {e}")
        # Retourner prédictions simulées
        return pd.DataFrame({
            'timestamp': pd.date_range(start=datetime.now(), periods=48, freq='h'),
            'predicted_price': [75 + i * 0.3 for i in range(48)],
            'confidence_lower': [70 + i * 0.3 for i in range(48)],
            'confidence_upper': [80 + i * 0.3 for i in range(48)]
        })

def generate_recommendation(db, current_price, predictions):
    """Génère recommandation"""
    from src.trading.recommendations import RecommendationEngine
    
    engine = RecommendationEngine(db)
    contracts = db.get_active_contracts()
    
    reco = engine.generate_recommendation(
        current_price=current_price,
        predicted_prices=predictions[['timestamp', 'predicted_price']],
        contracts_df=contracts
    )
    
    # Stocker en DB
    db.store_recommendation(
        action=reco['action'],
        score=reco['score'],
        volume_mwh=reco['volume_mwh'],
        target_price=reco['target_price'],
        expected_gain=reco['expected_gain'],
        reasoning=reco['reasoning']
    )
    
    # Créer alertes
    engine.check_and_create_alerts(current_price, predictions[['timestamp', 'predicted_price']], contracts)
    
    return reco

# ==========================================
# MAIN APP
# ==========================================

def main():
    # Header minimaliste
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚡ MétéoTrader Pro")
    with col2:
        st.metric("", f"{datetime.now().strftime('%H:%M')}", label="Heure")
    
    # Initialiser
    db = init_database()
    
    # Charger données
    try:
        df = load_market_data()
        current_price = get_current_price(df)
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        current_price = 75.0
        df = pd.DataFrame()
    
    # Obtenir prédictions
    predictions = get_future_predictions(db)
    
    # Générer recommandation
    reco = generate_recommendation(db, current_price, predictions)
    
    # ===== MÉTRIQUES PRINCIPALES =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Prix Spot",
            f"{current_price:.1f} €/MWh",
            delta=None
        )
    
    with col2:
        min_pred = predictions['predicted_price'].min()
        delta = min_pred - current_price
        st.metric(
            "Prix Min 48h",
            f"{min_pred:.1f} €/MWh",
            delta=f"{delta:+.1f}€"
        )
    
    with col3:
        contracts = db.get_active_contracts()
        total_volume = contracts['volume_mwh'].sum() if not contracts.empty else 0
        st.metric(
            "Contrats Actifs",
            f"{len(contracts)}",
            delta=f"{total_volume:.0f} MWh"
        )
    
    with col4:
        # P&L approximatif (à améliorer avec trades réels)
        if not contracts.empty:
            avg_guaranteed = (contracts['volume_mwh'] * contracts['guaranteed_price_eur_mwh']).sum() / total_volume
            potential_pnl = (avg_guaranteed - current_price) * total_volume * 0.1
        else:
            potential_pnl = 0
        
        st.metric(
            "P&L Potentiel",
            f"{potential_pnl:+.0f} €",
            delta=None
        )
    
    st.divider()
    
    # ===== 3 SECTIONS PRINCIPALES =====
    
    # 1️⃣ RECOMMANDATION DU MODÈLE
    st.markdown("### 🎯 Recommandation du Modèle")
    
    # Couleur selon action
    reco_class = {
        'BUY': 'reco-buy',
        'HOLD': 'reco-hold',
        'HEDGE': 'reco-hedge'
    }.get(reco['action'], 'reco-hold')
    
    # Emoji selon action
    emoji = {
        'BUY': '💰',
        'HOLD': '⏸️',
        'HEDGE': '⚠️'
    }.get(reco['action'], '•')
    
    st.markdown(f"""
    <div class="reco-card {reco_class}">
        <h2 style="margin: 0 0 16px 0;">{emoji} {reco['action']}</h2>
        <div style="font-size: 0.875rem; color: #888888; margin-bottom: 24px;">
            Score de confiance: {reco['score']}/100
        </div>
        <div style="white-space: pre-wrap; line-height: 1.6;">
            {reco['reasoning']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Détails recommandation
    if reco['action'] in ['BUY', 'HEDGE']:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Volume Recommandé", f"{reco['volume_mwh']:.1f} MWh")
        
        with col2:
            st.metric("Prix Cible", f"{reco['target_price']:.1f} €/MWh")
        
        with col3:
            st.metric("Gain Attendu", f"{reco['expected_gain']:+.0f} €")
    
    st.divider()
    
    # 2️⃣ CONTRATS ACTIFS
    st.markdown("### 📊 Contrats Actifs")
    
    contracts = db.get_active_contracts()
    
    if contracts.empty:
        st.info("Aucun contrat actif. Ajoutez un contrat pour commencer.")
        
        with st.expander("➕ Ajouter un contrat"):
            with st.form("add_contract"):
                client_name = st.text_input("Nom du client")
                col1, col2 = st.columns(2)
                with col1:
                    volume = st.number_input("Volume (MWh)", min_value=0.0, value=100.0)
                with col2:
                    guaranteed_price = st.number_input("Prix garanti (€/MWh)", min_value=0.0, value=85.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Date début", value=datetime.now().date())
                with col2:
                    end_date = st.date_input("Date fin", value=(datetime.now() + timedelta(days=365)).date())
                
                submitted = st.form_submit_button("Ajouter")
                
                if submitted and client_name:
                    db.add_contract(
                        client_name=client_name,
                        volume_mwh=volume,
                        guaranteed_price=guaranteed_price,
                        start_date=str(start_date),
                        end_date=str(end_date)
                    )
                    st.success(f"✅ Contrat '{client_name}' ajouté!")
                    st.rerun()
    else:
        # Afficher liste contrats
        display_contracts = contracts[[
            'client_name', 'volume_mwh', 'guaranteed_price_eur_mwh', 'start_date', 'end_date'
        ]].copy()
        
        display_contracts.columns = ['Client', 'Volume (MWh)', 'Prix Garanti (€/MWh)', 'Début', 'Fin']
        
        # Calculer P&L estimé pour chaque contrat
        display_contracts['P&L Estimé (€)'] = (
            (display_contracts['Prix Garanti (€/MWh)'] - current_price) * 
            display_contracts['Volume (MWh)'] * 0.1  # 10% du volume
        ).round(0)
        
        st.dataframe(display_contracts, use_container_width=True, hide_index=True)
        
        # Bouton ajouter contrat
        with st.expander("➕ Ajouter un contrat"):
            with st.form("add_contract_2"):
                client_name = st.text_input("Nom du client")
                col1, col2 = st.columns(2)
                with col1:
                    volume = st.number_input("Volume (MWh)", min_value=0.0, value=100.0)
                with col2:
                    guaranteed_price = st.number_input("Prix garanti (€/MWh)", min_value=0.0, value=85.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Date début", value=datetime.now().date())
                with col2:
                    end_date = st.date_input("Date fin", value=(datetime.now() + timedelta(days=365)).date())
                
                submitted = st.form_submit_button("Ajouter")
                
                if submitted and client_name:
                    db.add_contract(
                        client_name=client_name,
                        volume_mwh=volume,
                        guaranteed_price=guaranteed_price,
                        start_date=str(start_date),
                        end_date=str(end_date)
                    )
                    st.success(f"✅ Contrat '{client_name}' ajouté!")
                    st.rerun()
    
    st.divider()
    
    # 3️⃣ ALERTES
    st.markdown("### ⚠️ Alertes")
    
    alerts = db.get_active_alerts(limit=10)
    
    if alerts.empty:
        st.success("✅ Aucune alerte active")
    else:
        for idx, alert in alerts.iterrows():
            severity_class = f"alert-{alert['severity']}"
            
            st.markdown(f"""
            <div class="{severity_class}">
                <strong>{alert['message']}</strong>
                <div style="font-size: 0.75rem; color: #888888; margin-top: 8px;">
                    {alert['timestamp']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # ===== GRAPHIQUE PRÉDICTIONS (optionnel, minimaliste) =====
    with st.expander("📈 Voir les prédictions détaillées"):
        # Timeline simple
        fig = go.Figure()
        
        # Prix actuels (si disponibles)
        if not df.empty:
            historical = df[df['timestamp'] <= datetime.now()].tail(72)
            fig.add_trace(go.Scatter(
                x=historical['timestamp'],
                y=historical['price_eur_mwh'],
                mode='lines',
                name='Prix Réel',
                line=dict(color='#3b82f6', width=2)
            ))
        
        # Prédictions
        fig.add_trace(go.Scatter(
            x=predictions['timestamp'],
            y=predictions['predicted_price'],
            mode='lines',
            name='Prix Prédit',
            line=dict(color='#f97316', width=2)
        ))
        
        # Zone de confiance
        fig.add_trace(go.Scatter(
            x=predictions['timestamp'].tolist() + predictions['timestamp'].tolist()[::-1],
            y=predictions['confidence_upper'].tolist() + predictions['confidence_lower'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(249, 115, 22, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            name='Intervalle de confiance'
        ))
        
        # Layout minimaliste
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#0a0a0a',
            plot_bgcolor='#1a1a1a',
            margin=dict(l=0, r=0, t=20, b=0),
            height=400,
            xaxis_title='',
            yaxis_title='Prix (€/MWh)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666666; padding: 48px 0 24px 0; font-size: 0.875rem;">
        MétéoTrader Pro • Données temps réel RTE • Prédictions IA
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

