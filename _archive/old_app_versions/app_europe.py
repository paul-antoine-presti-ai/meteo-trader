"""
MétéoTrader Pro Europe - Plateforme Trading Multi-Pays
Interface complète: Prix, Production, Consommation, Gap Offre/Demande, Arbitrage
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Configuration page
st.set_page_config(
    page_title="MétéoTrader Pro Europe",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Minimaliste Dark Mode
st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #ffffff; }
    h1, h2, h3 { color: #ffffff; font-weight: 300; }
    h1 { font-size: 2rem; margin-bottom: 1rem; }
    
    .stMetric { 
        background-color: #1a1a1a; 
        padding: 16px; 
        border-radius: 8px; 
        border: 1px solid #2a2a2a; 
    }
    
    .stMetric label { color: #888888; font-size: 0.875rem; }
    .stMetric [data-testid="stMetricValue"] { 
        color: #ffffff; 
        font-size: 1.5rem; 
        font-weight: 300; 
    }
    
    /* Cards */
    .reco-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #f97316;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
    }
    
    /* Tension levels */
    .tension-critical { color: #ef4444; }
    .tension-high { color: #f97316; }
    .tension-medium { color: #fbbf24; }
    .tension-balanced { color: #10b981; }
    .tension-surplus { color: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FONCTIONS
# ==========================================

@st.cache_resource
def init_clients():
    """Initialise les clients API"""
    from src.data.entsoe_api import EntsoeClient
    from src.data.database import PriceDatabase
    
    os.makedirs('data', exist_ok=True)
    
    return EntsoeClient(), PriceDatabase('data/meteotrader.db')

@st.cache_data(ttl=3600)
def load_european_data(countries=['FR', 'DE', 'ES']):
    """Charge toutes les données européennes"""
    sys.path.append('.')
    from src.data.fetch_europe import fetch_european_prices, predict_prices_europe
    
    # Récupérer prix historiques
    with st.spinner('📊 Récupération prix européens...'):
        prices = fetch_european_prices(countries=countries, days=7)
    
    # Générer prédictions futures
    with st.spinner('🔮 Génération prédictions 48h...'):
        predictions = predict_prices_europe(prices, {}, forecast_hours=48)
    
    return prices, predictions

@st.cache_data(ttl=3600)
def load_supply_demand_data(countries=['FR']):
    """Charge données production + consommation"""
    client, _ = init_clients()
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2)
    
    data = {}
    
    for country in countries:
        try:
            # Production
            prod = client.get_actual_generation(country, str(start_date), str(end_date))
            
            # Consommation
            load = client.get_actual_load(country, str(start_date), str(end_date))
            
            # Prévisions consommation
            forecast = client.get_load_forecast(country, str(start_date), str(end_date))
            
            data[country] = {
                'production': prod,
                'load': load,
                'forecast': forecast
            }
            
        except Exception as e:
            st.warning(f"⚠️ Données {country}: {e}")
    
    return data

def analyze_gap(supply_demand_data, prices):
    """Analyse gap offre/demande"""
    from src.analysis.supply_demand import SupplyDemandAnalyzer
    
    analyzer = SupplyDemandAnalyzer()
    analyses = {}
    
    for country, data in supply_demand_data.items():
        if data['production'].empty or data['load'].empty:
            continue
        
        price_df = prices.get(country, pd.DataFrame())
        
        analysis = analyzer.analyze_country_market(
            production_df=data['production'],
            load_df=data['load'],
            prices_df=price_df
        )
        
        analyses[country] = {
            'analysis': analysis,
            'current': analyzer.get_current_situation(analysis)
        }
    
    return analyses

def calculate_arbitrage(predictions):
    """Calcule opportunités d'arbitrage"""
    from src.arbitrage.engine import ArbitrageEngine
    
    engine = ArbitrageEngine(predictions)
    opps = engine.calculate_all_opportunities()
    
    return engine, opps

# ==========================================
# MAIN APP
# ==========================================

def main():
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("⚡ MétéoTrader Pro Europe")
    
    with col2:
        st.metric("Heure", datetime.now().strftime('%H:%M'))
    
    with col3:
        st.metric("Marchés", "🟢 Ouverts")
    
    st.divider()
    
    # Charger données
    try:
        prices, predictions = load_european_data(countries=['FR', 'DE', 'ES'])
        supply_demand = load_supply_demand_data(countries=['FR'])
        gap_analyses = analyze_gap(supply_demand, prices)
        arb_engine, opportunities = calculate_arbitrage(predictions)
        
    except Exception as e:
        st.error(f"❌ Erreur chargement: {e}")
        return
    
    # ===== MÉTRIQUES PRINCIPALES =====
    col1, col2, col3, col4 = st.columns(4)
    
    # Prix spot France
    if 'FR' in prices and not prices['FR'].empty:
        latest_price = prices['FR'].iloc[-1]['price_eur_mwh']
        with col1:
            st.metric("Prix Spot FR", f"{latest_price:.1f} €/MWh")
    
    # Gap France
    if 'FR' in gap_analyses and gap_analyses['FR']['current']:
        current = gap_analyses['FR']['current']
        with col2:
            st.metric(
                "Gap FR", 
                f"{current['gap_gw']:+.1f} GW",
                delta=f"{current['reserve_margin_pct']:+.1f}%"
            )
    
    # Opportunités
    if not opportunities.empty:
        n_opps = len(opportunities[opportunities['score'] >= 50])
        with col3:
            st.metric("Opportunités", f"{n_opps}")
    
    # Marge potentielle
    margin_info = arb_engine.calculate_potential_margin(hours=48)
    with col4:
        st.metric("Marge 48h", f"{margin_info['total_margin']:.0f} €")
    
    st.divider()
    
    # ===== RECOMMANDATION PRINCIPALE =====
    st.markdown("### 🎯 Recommandation Principale")
    
    best_opp = arb_engine.get_best_opportunity()
    
    if best_opp:
        from src.arbitrage.engine import generate_recommendation
        from src.data.entsoe_api import EntsoeClient
        
        reco_text = generate_recommendation(best_opp, EntsoeClient.COUNTRY_NAMES)
        
        st.markdown(f"""
        <div class="reco-card">
            {reco_text.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aucune opportunité d'arbitrage forte pour le moment.")
    
    st.divider()
    
    # ===== TABS =====
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Gap Offre/Demande",
        "🗺️ Comparaison Europe", 
        "💰 Top Opportunités",
        "📈 Analyse Détaillée"
    ])
    
    # TAB 1: Gap Offre/Demande
    with tab1:
        if 'FR' in gap_analyses and gap_analyses['FR']['current']:
            current = gap_analyses['FR']['current']
            tension = current['tension']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Production", f"{current['production_gw']:.1f} GW")
            
            with col2:
                st.metric("Consommation", f"{current['load_gw']:.1f} GW")
            
            with col3:
                st.metric(
                    "Marge Réserve",
                    f"{current['reserve_margin_pct']:+.1f}%",
                    delta=tension['emoji']
                )
            
            # Situation marché
            st.markdown(f"""
            <div style="background:#1a1a1a; padding:20px; border-radius:12px; margin:20px 0;">
                <h3>{tension['emoji']} {tension['level']}</h3>
                <p style="font-size:1.1rem; margin:10px 0;">{tension['description']}</p>
                <p><strong>Impact Prix:</strong> {tension['price_impact']}</p>
                <p><strong>Action Trader:</strong> {tension['trader_action']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Graphique historique Gap
            if 'analysis' in gap_analyses['FR']:
                analysis_df = gap_analyses['FR']['analysis']
                
                fig = go.Figure()
                
                # Gap
                fig.add_trace(go.Scatter(
                    x=analysis_df['timestamp'],
                    y=analysis_df['gap_gw'],
                    mode='lines',
                    name='Gap (Prod - Conso)',
                    line=dict(color='#f97316', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(249, 115, 22, 0.2)'
                ))
                
                # Ligne zéro
                fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
                
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#0a0a0a',
                    plot_bgcolor='#1a1a1a',
                    height=400,
                    title="Gap Offre/Demande France (48h)",
                    xaxis_title="",
                    yaxis_title="Gap (GW)",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("Données gap non disponibles")
    
    # TAB 2: Comparaison Europe
    with tab2:
        fig = go.Figure()
        
        # Courbes prix par pays
        colors = {
            'FR': '#3b82f6',
            'DE': '#10b981',
            'ES': '#f97316',
            'IT': '#ef4444',
            'GB': '#8b5cf6'
        }
        
        for country, pred_df in predictions.items():
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
            paper_bgcolor='#0a0a0a',
            plot_bgcolor='#1a1a1a',
            height=500,
            title="Comparaison Prix Prédits (48h)",
            xaxis_title="",
            yaxis_title="Prix (€/MWh)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats par pays
        st.markdown("#### 📊 Statistiques par Pays")
        
        stats_data = []
        for country, pred_df in predictions.items():
            if not pred_df.empty:
                stats_data.append({
                    'Pays': f"🏴 {country}",
                    'Prix Moyen': f"{pred_df['predicted_price'].mean():.1f} €",
                    'Min': f"{pred_df['predicted_price'].min():.1f} €",
                    'Max': f"{pred_df['predicted_price'].max():.1f} €",
                    'Volatilité': f"{pred_df['predicted_price'].std():.1f} €"
                })
        
        st.table(pd.DataFrame(stats_data))
    
    # TAB 3: Top Opportunités
    with tab3:
        if not opportunities.empty:
            top10 = arb_engine.get_top_opportunities(n=10, min_score=30)
            
            if not top10.empty:
                display_opps = top10[['from_country', 'to_country', 'timestamp', 
                                       'spread_net', 'volume_optimal', 'gain_total', 'score']].copy()
                
                display_opps.columns = ['Achat', 'Vente', 'Heure', 'Spread Net (€/MWh)', 
                                        'Volume (MWh)', 'Gain (€)', 'Score']
                
                # Formatage
                display_opps['Achat'] = display_opps['Achat'].apply(lambda x: f"🏴 {x}")
                display_opps['Vente'] = display_opps['Vente'].apply(lambda x: f"🏴 {x}")
                display_opps['Heure'] = pd.to_datetime(display_opps['Heure']).dt.strftime('%d/%m %H:%M')
                display_opps['Spread Net (€/MWh)'] = display_opps['Spread Net (€/MWh)'].round(1)
                display_opps['Volume (MWh)'] = display_opps['Volume (MWh)'].round(0)
                display_opps['Gain (€)'] = display_opps['Gain (€)'].round(0)
                
                st.dataframe(display_opps, use_container_width=True, hide_index=True)
                
                # Résumé
                st.markdown(f"""
                **📊 Résumé:**
                - **{len(top10)}** opportunités identifiées
                - **Spread moyen:** {top10['spread_net'].mean():.1f} €/MWh
                - **Gain potentiel total:** {top10['gain_total'].sum():.0f} €
                """)
            else:
                st.info("Aucune opportunité forte pour le moment")
        else:
            st.info("Calcul en cours...")
    
    # TAB 4: Analyse Détaillée
    with tab4:
        st.markdown("#### 🔍 Analyse de Marché Avancée")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Prix Historiques**")
            
            for country, df in prices.items():
                if not df.empty:
                    st.metric(
                        f"🏴 {country}",
                        f"{df['price_eur_mwh'].mean():.1f} €/MWh",
                        delta=f"±{df['price_eur_mwh'].std():.1f}€"
                    )
        
        with col2:
            st.markdown("**💰 Meilleurs Spreads**")
            
            if not opportunities.empty:
                best_routes = opportunities.groupby(['from_country', 'to_country']).agg({
                    'spread_net': 'mean',
                    'gain_total': 'sum'
                }).sort_values('gain_total', ascending=False).head(5)
                
                for idx, (countries, row) in enumerate(best_routes.iterrows(), 1):
                    st.write(f"{idx}. {countries[0]}→{countries[1]}: {row['spread_net']:.1f}€/MWh")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align:center; color:#666666; padding:24px 0; font-size:0.875rem;">
        MétéoTrader Pro Europe • Données ENTSOE-E + Open-Meteo • Prédictions IA Multi-Pays
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

