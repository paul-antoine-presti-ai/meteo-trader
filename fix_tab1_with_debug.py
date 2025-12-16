#!/usr/bin/env python3
"""
Tab1 avec debug et fallback ENTSOE-E simple
"""

tab1_with_fallback = '''    with tab1:
        st.markdown("### Mix Énergétique France")
        st.caption("📊 Production électrique en temps réel")
        
        # Essayer d'abord les données RTE
        prod_cols = [c for c in df_france.columns if 'production_gw' in c.lower()]
        
        # Si pas de colonnes RTE, essayer ENTSOE-E
        if len(prod_cols) == 0:
            st.info("📊 Chargement données ENTSOE-E...")
            try:
                from src.data.entsoe_api import EntsoeClient
                from datetime import datetime, timedelta
                
                client = EntsoeClient()
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=1)
                
                prod_df = client.get_actual_generation('FR', str(start_date), str(end_date))
                
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
                    else:
                        st.warning("Données chargées mais toutes à zéro")
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
'''

import re

with open('app.py', 'r') as f:
    content = f.read()

# Remplacer tab1
pattern = r'(    with tab1:.*?)(    with tab2:)'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content.replace(match.group(0), tab1_with_fallback + '\n' + match.group(2))
    print("✅ Tab1 avec fallback ENTSOE-E")
else:
    print("⚠️ Pattern non trouvé")

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Done!")

