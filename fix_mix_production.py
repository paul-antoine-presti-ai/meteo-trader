#!/usr/bin/env python3
"""
Fix Mix Énergétique - Utiliser ENTSOE-E comme fallback
"""

import re

with open('app.py', 'r') as f:
    content = f.read()

# Nouvelle section Mix Énergétique avec fallback ENTSOE-E
new_mix_section = '''    with tab1:
        st.markdown("### Mix Énergétique France")
        st.caption("📊 **Répartition de la production électrique en temps réel** : Visualisation du mix par source (nucléaire, hydraulique, éolien, solaire, fossile). Données mises à jour chaque heure via l'API RTE.")
        
        # Production par type
        prod_cols = [c for c in df_france.columns if 'production_gw' in c and c not in ['total_production_gw', 'total_rte_production_gw']]
        
        # FALLBACK: Utiliser ENTSOE-E si RTE ne fournit pas les données
        if not prod_cols or len(prod_cols) == 0:
            st.warning("⚠️ Données RTE production non disponibles, utilisation ENTSOE-E...")
            
            # Charger données ENTSOE-E France
            try:
                import sys
                sys.path.append('.')
                from src.data.entsoe_api import EntsoeClient
                from datetime import datetime, timedelta
                
                client = EntsoeClient()
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=1)
                
                with st.spinner("📊 Chargement production ENTSOE-E..."):
                    prod_df = client.get_actual_generation('FR', str(start_date), str(end_date))
                
                if not prod_df.empty and 'timestamp' in prod_df.columns:
                    # Merger avec df_france
                    df_france = pd.merge(df_france, prod_df, on='timestamp', how='left', suffixes=('', '_entsoe'))
                    prod_cols = [c for c in df_france.columns if 'production_gw' in c.lower() and c not in ['total_production_gw', 'total_rte_production_gw']]
                    st.success(f"✅ {len(prod_cols)} sources d'énergie chargées depuis ENTSOE-E")
                else:
                    st.error("❌ Impossible de charger les données de production")
                    prod_cols = []
            except Exception as e:
                st.error(f"❌ Erreur chargement ENTSOE-E: {e}")
                prod_cols = []
        
        if prod_cols and len(prod_cols) > 0:
            latest = df_france.iloc[-1]
            
            # Calculer totaux par catégorie (compatible RTE et ENTSOE-E)
            nuclear = latest.get('nuclear_production_gw', latest.get('Nuclear_production_gw', 0))
            
            # Hydro (agrégation de toutes les sources hydro)
            hydro_cols = [c for c in prod_cols if 'hydro' in c.lower()]
            hydro = sum([latest.get(c, 0) for c in hydro_cols])
            
            # Wind (agrégation offshore + onshore)
            wind_cols = [c for c in prod_cols if 'wind' in c.lower()]
            wind = sum([latest.get(c, 0) for c in wind_cols])
            
            solar = latest.get('solar_production_gw', latest.get('Solar_production_gw', 0))
            
            # Fossile (gas, coal, oil)
            fossil_cols = [c for c in prod_cols if any(f in c.lower() for f in ['gas', 'coal', 'oil', 'fossil'])]
            fossil = sum([latest.get(c, 0) for c in fossil_cols])
            
            # Autre (biomass, waste)
            other_cols = [c for c in prod_cols if any(o in c.lower() for o in ['biomass', 'waste', 'other'])]
            other = sum([latest.get(c, 0) for c in other_cols])
            
            total_prod = nuclear + hydro + wind + solar + fossil + other
            
            # Métriques principales
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                pct = (nuclear / total_prod * 100) if total_prod > 0 else 0
                st.metric("⚛️ Nucléaire", f"{nuclear:.2f} GW", f"{pct:.1f}%")
            
            with col2:
                pct = (hydro / total_prod * 100) if total_prod > 0 else 0
                st.metric("💧 Hydraulique", f"{hydro:.2f} GW", f"{pct:.1f}%")
            
            with col3:
                pct = (wind / total_prod * 100) if total_prod > 0 else 0
                st.metric("🌬️ Éolien", f"{wind:.2f} GW", f"{pct:.1f}%")
            
            with col4:
                pct = (solar / total_prod * 100) if total_prod > 0 else 0
                st.metric("☀️ Solaire", f"{solar:.2f} GW", f"{pct:.1f}%")
            
            with col5:
                st.metric("⚡ TOTAL", f"{total_prod:.2f} GW")
            
            st.markdown("---")
            
            # Pie chart
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🥧 Mix Énergétique Actuel")
                
                mix_data = pd.DataFrame({
                    'Source': ['⚛️ Nucléaire', '💧 Hydraulique', '🌬️ Éolien', '☀️ Solaire', '🏭 Fossile', '♻️ Autre'],
                    'Production': [nuclear, hydro, wind, solar, fossil, other]
                })
                
                # Filtrer les sources avec production > 0
                mix_data = mix_data[mix_data['Production'] > 0]
                
                fig_pie = px.pie(
                    mix_data,
                    values='Production',
                    names='Source',
                    title=f"Mix Énergétique - {latest['timestamp'].strftime('%d/%m/%Y %H:%M')}",
                    template='plotly_dark',
                    color_discrete_sequence=px.colors.sequential.Oranges_r
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(height=400, paper_bgcolor='#0c0c0c', plot_bgcolor='#161616')
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Évolution 24h")
                
                # Graphique historique (dernières 24h)
                last_24h = df_france.tail(24)
                
                fig_evolution = go.Figure()
                
                if nuclear > 0:
                    fig_evolution.add_trace(go.Scatter(
                        x=last_24h['timestamp'],
                        y=last_24h.get('nuclear_production_gw', last_24h.get('Nuclear_production_gw', 0)),
                        name='⚛️ Nucléaire',
                        line=dict(color='#ff6b35', width=2)
                    ))
                
                if wind > 0:
                    wind_24h = last_24h[[c for c in wind_cols if c in last_24h.columns]].sum(axis=1) if wind_cols else 0
                    fig_evolution.add_trace(go.Scatter(
                        x=last_24h['timestamp'],
                        y=wind_24h,
                        name='🌬️ Éolien',
                        line=dict(color='#3b82f6', width=2)
                    ))
                
                if solar > 0:
                    fig_evolution.add_trace(go.Scatter(
                        x=last_24h['timestamp'],
                        y=last_24h.get('solar_production_gw', last_24h.get('Solar_production_gw', 0)),
                        name='☀️ Solaire',
                        line=dict(color='#fbbf24', width=2)
                    ))
                
                fig_evolution.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#0c0c0c',
                    plot_bgcolor='#161616',
                    height=400,
                    xaxis_title="Heure",
                    yaxis_title="Production (GW)",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_evolution, use_container_width=True)
        
        else:
            st.warning("⚠️ Données de production détaillées non disponibles actuellement")
            st.info("""
            💡 **Pourquoi ?**
            - Les données RTE peuvent avoir un délai de publication
            - L'API ENTSOE-E peut être temporairement indisponible
            - Le mix énergétique sera disponible dès que les données seront mises à jour
            
            **Colonnes recherchées** : `*_production_gw` (nuclear, wind, solar, hydro, gas, etc.)
            """)
'''

# Trouver et remplacer la section tab1 (Mix Énergétique)
pattern = r'(    with tab1:.*?)(    with tab2:|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    rest_of_content = match.group(2) if match.group(2) else ''
    content = content.replace(match.group(0), new_mix_section + '\n' + rest_of_content)
    print("✅ Section Mix Énergétique remplacée avec fallback ENTSOE-E")
else:
    print("⚠️ Section tab1 non trouvée")

# Sauvegarder
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Fix Mix Énergétique appliqué!")

