#!/usr/bin/env python3
"""
Créer une page Prédictions Ultra-Détaillées
"""

import re

with open('app.py', 'r') as f:
    content = f.read()

# Nouvelle page prédictions détaillées
new_predictions_page = '''
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
'''

# Ajouter la nouvelle fonction avant page_ml
pattern = r'(def page_ml\(.*?\):)'
match = re.search(pattern, content)

if match:
    content = content.replace(match.group(0), new_predictions_page + '\n\n' + match.group(0))
    print("✅ Nouvelle page Prédictions Détaillées ajoutée")
else:
    print("⚠️ page_ml non trouvée, ajout en fin de fichier")
    # Ajouter avant main()
    content = content.replace('def main():', new_predictions_page + '\n\ndef main():')

# Ajouter dans la sidebar
sidebar_pattern = r'(page = st\.sidebar\.radio\(\s*"Navigation",\s*\[)(.*?)(\])'
sidebar_match = re.search(sidebar_pattern, content, re.DOTALL)

if sidebar_match:
    current_pages = sidebar_match.group(2)
    # Ajouter avant Modèles ML
    if '"🔮 Prédictions Détaillées"' not in current_pages:
        new_pages = current_pages.replace('"🤖 Modèles ML"', '"🔮 Prédictions Détaillées",\n        "🤖 Modèles ML"')
        content = content.replace(sidebar_match.group(0), sidebar_match.group(1) + new_pages + sidebar_match.group(3))
        print("✅ Page ajoutée au menu sidebar")

# Ajouter le elif pour la nouvelle page
elif_pattern = r'(elif page == "🤖 Modèles ML":)'
elif_match = re.search(elif_pattern, content)

if elif_match:
    new_elif = '''elif page == "🔮 Prédictions Détaillées":
        page_predictions_detaillees(prices_europe, predictions_europe, df_france, model, features)
    '''
    content = content.replace(elif_match.group(0), new_elif + elif_match.group(0))
    print("✅ Route ajoutée pour la nouvelle page")

# Sauvegarder
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Page Prédictions Détaillées créée!")

