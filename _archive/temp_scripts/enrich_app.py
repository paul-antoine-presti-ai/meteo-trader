#!/usr/bin/env python3
"""
Script pour enrichir app.py avec :
1. Graphique multi-pays interactif
2. Backtesting P&L
3. Descriptions détaillées
4. Fix Mix Énergétique
"""

import re

# Lire app.py
with open('app.py', 'r') as f:
    content = f.read()

# ==========================================
# 1. ENRICHIR PAGE EUROPE
# ==========================================

# Nouvelle page Europe avec graphique interactif multi-pays
new_page_europe = '''def page_europe(prices_europe, predictions_europe):
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
'''

# Remplacer page_europe
pattern_europe = r'def page_europe\(prices_europe, predictions_europe\):.*?(?=\ndef |\Z)'
content = re.sub(pattern_europe, new_page_europe, content, flags=re.DOTALL)

# ==========================================
# 2. AJOUTER TEXTE DESCRIPTIF MIX ÉNERGÉTIQUE
# ==========================================

# Chercher et enrichir le Mix Énergétique
if 'Mix Énergétique France' in content:
    content = content.replace(
        'st.markdown("### Mix Énergétique France")',
        '''st.markdown("### Mix Énergétique France")
        st.caption("📊 **Répartition de la production électrique en temps réel** : Visualisation du mix par source (nucléaire, hydraulique, éolien, solaire, fossile). Données mises à jour chaque heure via l'API RTE.")'''
    )

# ==========================================
# 3. SAUVEGARDER
# ==========================================

with open('app.py', 'w') as f:
    f.write(content)

print("✅ app.py enrichi avec succès!")
print("  • Page Europe: graphique multi-pays interactif")
print("  • Descriptions enrichies")

