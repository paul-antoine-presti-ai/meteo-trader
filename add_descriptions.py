#!/usr/bin/env python3
"""
Ajouter textes descriptifs détaillés pour toutes les pages
"""

import re

with open('app.py', 'r') as f:
    content = f.read()

# ========================================
# 1. Vue d'Ensemble
# ========================================
if 'def page_overview' in content:
    content = content.replace(
        'st.markdown("# 📊 Vue d\'Ensemble")',
        '''st.markdown("# 📊 Vue d'Ensemble")
    st.markdown("""
    *Tableau de bord principal pour le trading d'électricité sur les marchés spot européens.*
    
    **Ce que vous voyez ici :**
    - 💰 **Prix moyen** du jour sur le marché français
    - 📈 **Timeline complète** : Prix historiques, prédictions passées (avec accuracy), et prévisions futures 48h
    - 🎯 **Recommandations** : Actions suggérées basées sur les prédictions du modèle ML
    - 💰 **Backtesting** : Performance historique des recommandations (gain/perte par transaction)
    
    **Mise à jour :** Toutes les heures (données RTE + ENTSOE-E)
    """)'''
    )

# ========================================
# 2. France Détaillée
# ========================================
if 'def page_france' in content:
    content = content.replace(
        'st.markdown("# 🇫🇷 France Détaillée")',
        '''st.markdown("# 🇫🇷 France Détaillée")
    st.markdown("""
    *Analyse approfondie du marché français avec météo, production, et prédictions ML.*
    
    **Données disponibles :**
    - 🌡️ **Météo** : Température, vent, pression (impact sur demande et production renouvelable)
    - ⚡ **Production** : Mix énergétique par source (nucléaire, éolien, solaire, hydraulique, fossile)
    - 📊 **Consommation** : Demande électrique en temps réel
    - 🔮 **Prédictions 48h** : Prix futurs avec recommandations (heures optimales d'achat/vente)
    - 🎯 **Modèle ML** : Random Forest & XGBoost entraînés sur 744h de données historiques
    
    **Utilisation trader :**
    - Identifier les heures les moins chères pour acheter
    - Anticiper les pics de demande (canicule, vague de froid)
    - Optimiser les stratégies d'achat/vente selon le mix énergétique
    """)'''
    )

# ========================================
# 3. Gap Offre/Demande
# ========================================
if 'def page_gap' in content:
    content = content.replace(
        'st.markdown("# ⚖️ Gap Offre/Demande")',
        '''st.markdown("# ⚖️ Gap Offre/Demande")
    st.markdown("""
    *Surveillance de l'équilibre production/consommation pour anticiper les tensions sur le réseau.*
    
    **Indicateur clé : Reserve Margin**
    - **Formule** : `(Production - Consommation) / Consommation × 100`
    - **Interprétation** :
      - 🔴 **< 5%** : CRITIQUE (risque blackout, prix explosifs)
      - 🟠 **5-10%** : TENSION (prix élevés, acheter maintenant risqué)
      - 🟢 **10-20%** : ÉQUILIBRÉ (prix normaux)
      - 🔵 **> 20%** : SURPLUS (prix bas, opportunité d'achat)
    
    **Action trader :**
    - **Tension/Critique** : Vendre à prix élevé, éviter d'acheter
    - **Surplus** : Acheter massivement, stocker (si possible)
    - **Équilibré** : Suivre recommandations ML
    """)'''
    )

# ========================================
# 4. Arbitrage
# ========================================
if 'def page_arbitrage' in content:
    content = content.replace(
        'st.markdown("# 💰 Arbitrage Cross-Border")',
        '''st.markdown("# 💰 Arbitrage Cross-Border")
    st.markdown("""
    *Opportunités de trading transfrontalier entre marchés européens.*
    
    **Principe de l'arbitrage :**
    1. **Acheter** dans un pays où le prix est bas (ex: France 50€/MWh)
    2. **Vendre** dans un pays où le prix est élevé (ex: Allemagne 80€/MWh)
    3. **Profit** = Écart de prix - Coûts de transport
    
    **Données affichées :**
    - 📊 **Spreads** : Écarts de prix entre pays (€/MWh)
    - 🚚 **Coûts transport** : Estimés selon capacités interconnexion
    - 💰 **Marge nette** : Gain réel après frais
    - 📦 **Volume optimal** : Quantité à trader pour maximiser le profit
    
    **Top Opportunités** : Classement des meilleures opérations par gain potentiel
    """)'''
    )

# ========================================
# 5. Mes Contrats
# ========================================
if 'def page_contracts' in content:
    content = content.replace(
        'st.markdown("# 📊 Mes Contrats")',
        '''st.markdown("# 📊 Mes Contrats")
    st.markdown("""
    *Gestion des contrats clients et suivi des engagements de prix.*
    
    **Fonctionnalités :**
    - ➕ **Ajouter contrat** : Client, volume (MWh/jour), prix garanti, date de livraison
    - 📊 **Suivi exposition** : Calcul automatique de l'exposition (risque si prix spot > prix garanti)
    - 💰 **P&L contrat** : Gain/perte par contrat selon évolution des prix
    - 🔔 **Alertes** : Notification si marché spot dépasse le prix garanti (risque de perte)
    
    **Stratégie trader :**
    - **Prix garanti élevé** → Acheter sur spot quand prix bas (hedge)
    - **Prix garanti bas** → Risque si spot monte (acheter en avance)
    - **Équilibre portefeuille** : Diversifier les échéances et les prix
    """)'''
    )

# ========================================
# 6. Modèles ML
# ========================================
if 'def page_ml' in content:
    content = content.replace(
        'st.markdown("# 🤖 Modèles ML")',
        '''st.markdown("# 🤖 Modèles ML")
    st.markdown("""
    *Comparaison des algorithmes de prédiction de prix et analyse de performance.*
    
    **Modèles entraînés :**
    - 🌲 **Random Forest** : Robuste, interprétable, baseline solide
    - ⚡ **XGBoost** : Performance supérieure, gestion des non-linéarités
    
    **Métriques d'évaluation :**
    - **R² Score** : % de variance expliquée (plus proche de 1 = mieux)
    - **RMSE** : Erreur moyenne en €/MWh (plus bas = mieux)
    - **MAE** : Erreur absolue moyenne (robuste aux outliers)
    
    **Features importantes :**
    - 🌡️ Température (impact chauffage/clim)
    - 🌬️ Vent (production éolienne)
    - ⏰ Heure/Jour (patterns temporels)
    - ⚡ Demande/Production (équilibre réseau)
    
    **Utilisation :** Le meilleur modèle (plus haut R²) est utilisé pour les prédictions 48h
    """)'''
    )

# Sauvegarder
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Toutes les descriptions ajoutées!")
print("  • Vue d'Ensemble")
print("  • France Détaillée")
print("  • Gap Offre/Demande")
print("  • Arbitrage")
print("  • Mes Contrats")
print("  • Modèles ML")

