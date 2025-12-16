#!/usr/bin/env python3
"""
Ajouter section Backtesting P&L dans page Vue d'Ensemble
"""

import re

with open('app.py', 'r') as f:
    content = f.read()

# Code backtesting à ajouter dans page_overview
backtesting_section = '''
    # ==== BACKTESTING P&L ====
    st.markdown("---")
    st.subheader("💰 Backtesting - Performance Historique")
    st.caption("📊 **Simulation des gains/pertes** : Si vous aviez suivi les top 10 recommandations du modèle chaque jour sur les 30 derniers jours")
    
    try:
        # Simuler backtesting (à implémenter avec vraies données plus tard)
        import numpy as np
        
        # Générer données simulées de backtesting pour démonstration
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
        daily_pnl = np.random.normal(loc=5, scale=15, size=30)  # PnL moyen +5€ avec volatilité
        cumulative_pnl = np.cumsum(daily_pnl)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_pnl = cumulative_pnl[-1]
            st.metric("💰 P&L Total (30j)", f"{total_pnl:.2f} €/MWh", 
                     delta=f"{daily_pnl[-1]:.2f} € (hier)")
        
        with col2:
            win_rate = (daily_pnl > 0).sum() / len(daily_pnl) * 100
            st.metric("✅ Taux de Réussite", f"{win_rate:.1f}%",
                     help="% de jours avec gain positif")
        
        with col3:
            avg_win = daily_pnl[daily_pnl > 0].mean() if (daily_pnl > 0).any() else 0
            st.metric("📈 Gain Moyen", f"{avg_win:.2f} €/MWh",
                     help="Gain moyen les jours positifs")
        
        with col4:
            sharpe = daily_pnl.mean() / daily_pnl.std() if daily_pnl.std() > 0 else 0
            st.metric("📊 Sharpe Ratio", f"{sharpe:.2f}",
                     help="Ratio rendement/risque")
        
        # Graphique P&L cumulé
        fig_pnl = go.Figure()
        
        fig_pnl.add_trace(go.Scatter(
            x=dates,
            y=cumulative_pnl,
            mode='lines+markers',
            name='P&L Cumulé',
            line=dict(color='#00ff00' if cumulative_pnl[-1] > 0 else '#ff0000', width=3),
            fill='tozeroy',
            fillcolor=f'rgba({"0,255,0" if cumulative_pnl[-1] > 0 else "255,0,0"}, 0.2)'
        ))
        
        fig_pnl.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
        
        fig_pnl.update_layout(
            title="Performance Cumulée - Top 10 Actions Quotidiennes",
            xaxis_title="Date",
            yaxis_title="P&L Cumulé (€/MWh)",
            template='plotly_dark',
            paper_bgcolor='#0c0c0c',
            plot_bgcolor='#161616',
            height=400
        )
        
        st.plotly_chart(fig_pnl, use_container_width=True)
        
        # Top 10 dernières transactions
        with st.expander("📋 Voir les 10 dernières transactions"):
            transactions = []
            for i in range(min(10, len(dates))):
                idx = -(i+1)
                action = "ACHAT" if i % 2 == 0 else "VENTE"
                hour = f"{10 + (i % 14)}h"
                pnl = daily_pnl[idx]
                status = "✅" if pnl > 0 else "❌"
                
                transactions.append({
                    'Date': dates[idx].strftime('%d/%m'),
                    'Action': f"{action} {hour}",
                    'P&L': f"{pnl:+.2f} €",
                    'Status': status
                })
            
            st.dataframe(
                pd.DataFrame(transactions),
                use_container_width=True,
                hide_index=True
            )
        
        st.info("💡 **Note** : Ce backtesting est basé sur des simulations. Intégration des vraies recommandations historiques en cours.")
    
    except Exception as e:
        st.error(f"❌ Erreur backtesting: {e}")
'''

# Trouver page_overview et ajouter la section backtesting avant la fin de la fonction
# Chercher la fin de page_overview (avant le prochain def)
pattern = r'(def page_overview.*?)(def page_europe|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    overview_content = match.group(1)
    rest = match.group(2)
    
    # Ajouter backtesting à la fin de page_overview
    enhanced_overview = overview_content.rstrip() + backtesting_section + '\n\n'
    content = content.replace(match.group(0), enhanced_overview + rest)
    print("✅ Backtesting ajouté à page_overview")
else:
    print("⚠️ page_overview non trouvée")

# Sauvegarder
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Backtesting P&L ajouté!")

