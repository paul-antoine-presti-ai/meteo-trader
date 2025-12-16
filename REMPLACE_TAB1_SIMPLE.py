#!/usr/bin/env python3
"""
Remplacer tab1 par une version ULTRA SIMPLE qui fonctionne
"""

# Tab1 simple sans fallback complexe
tab1_simple = '''    with tab1:
        st.markdown("### Mix Énergétique France")
        st.caption("📊 Production électrique en temps réel")
        
        # Colonnes de production
        prod_cols = [c for c in df_france.columns if 'production_gw' in c.lower()]
        
        if len(prod_cols) > 0 and len(df_france) > 0:
            latest = df_france.iloc[-1]
            
            # Valeurs (avec fallback à 0)
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
                
                # Graphique simple
                import plotly.express as px
                data = {'Source': ['Nucléaire', 'Éolien', 'Solaire', 'Hydraulique'],
                        'Production': [nuclear, wind, solar, hydro]}
                df_mix = pd.DataFrame(data)
                df_mix = df_mix[df_mix['Production'] > 0]
                
                fig = px.pie(df_mix, values='Production', names='Source', 
                            title="Mix Énergétique Actuel",
                            template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pas de données de production disponibles")
        else:
            st.info("Données de production en cours de chargement...")
'''

import re

with open('app.py', 'r') as f:
    content = f.read()

# Remplacer TOUT tab1 (de "with tab1:" jusqu'à "with tab2:")
pattern = r'(    with tab1:.*?)(    with tab2:)'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content.replace(match.group(0), tab1_simple + '\n' + match.group(2))
    print("✅ Tab1 remplacé par version simple")
else:
    print("⚠️ Pattern non trouvé")

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Tab1 ULTRA SIMPLE créé!")

