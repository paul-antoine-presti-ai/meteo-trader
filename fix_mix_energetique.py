#!/usr/bin/env python3
"""
Corriger Mix Énergétique - Ajouter debug et fallback
"""

import re

with open('app.py', 'r') as f:
    content = f.read()

# Trouver la section Mix Énergétique et ajouter du debug
old_mix_code = '''        # Production par type
        prod_cols = [c for c in df_france.columns if 'production_gw' in c and c not in ['total_production_gw', 'total_rte_production_gw']]
        
        if prod_cols and len(prod_cols) > 0:'''

new_mix_code = '''        # Production par type
        prod_cols = [c for c in df_france.columns if 'production_gw' in c and c not in ['total_production_gw', 'total_rte_production_gw']]
        
        # DEBUG: Afficher les colonnes disponibles
        all_cols = list(df_france.columns)
        st.caption(f"🔍 Colonnes disponibles ({len(all_cols)}): {', '.join([c for c in all_cols if 'production' in c.lower()][:5])}...")
        
        if prod_cols and len(prod_cols) > 0:'''

content = content.replace(old_mix_code, new_mix_code)

# Ajouter un else block pour le cas où prod_cols est vide
old_else = '''        else:
            st.warning("Données de production par type non disponibles")'''

new_else = '''        else:
            st.warning("⚠️ Données de production détaillées non disponibles actuellement")
            st.info("""
            💡 **Pourquoi ?**
            - Les données RTE peuvent avoir un délai de publication
            - Certaines colonnes de production peuvent être manquantes dans l'API
            - Le mix énergétique sera disponible dès que les données seront mises à jour
            
            **Colonnes recherchées** : `*_production_gw` (nuclear, wind, solar, hydro, gas, etc.)
            """)
            
            # Afficher au moins les colonnes disponibles
            avail_prod_cols = [c for c in df_france.columns if 'production' in c.lower()]
            if avail_prod_cols:
                st.caption(f"📊 Colonnes production trouvées: {', '.join(avail_prod_cols)}")
            else:
                st.caption("❌ Aucune colonne de production trouvée dans les données")'''

content = content.replace(old_else, new_else)

# Sauvegarder
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Mix Énergétique corrigé avec debug et fallback!")

