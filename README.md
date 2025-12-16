# ⚡ MétéoTrader Pro

**Plateforme professionnelle de trading électricité** avec Intelligence Artificielle, données météo et recommandations temps réel.

---

## 🚀 Lancement Rapide

```bash
# Activer l'environnement
source venv/bin/activate

# Lancer l'app
streamlit run app.py
```

**Ou simplement :**
```bash
./run.sh
```

---

## 📊 Fonctionnalités

### 🎯 **Pages Trader** (Sidebar)
- **🏠 Vue d'Ensemble** : Métriques clés, résumé marché
- **🌍 Europe** : Prix multi-pays, comparaison
- **🇫🇷 France Détaillée** : Météo, production, mix énergétique
- **⚖️ Gap Offre/Demande** : Analyse tension marché
- **💰 Arbitrage** : Opportunités cross-border
- **📊 Mes Contrats** : Gestion positions
- **🤖 Modèles ML** : Performance, feature importance

### 🎨 **Design Cursor**
- Ultra dark mode (#0c0c0c)
- Glassmorphism
- Typography fine
- Orange Mistral (#ff6b35)
- Sidebar avec dégradé

### 🔧 **Composants**
- ⏰ Horloge temps réel (Europe/Paris)
- 🔄 Timer rafraîchissement
- 📊 Métriques interactives
- 📈 Graphiques Plotly
- 🤖 Recommandations ML

---

## 📂 Structure

```
meteo-trader/
├── app.py                      # 🎯 App principale (Streamlit + sidebar)
├── components_utils.py         # 🔧 Composants UI (horloge, cartes)
├── requirements.txt            # 📋 Dépendances Python
├── run.sh                      # 🚀 Script lancement
├── src/                        # 📦 Code source
│   ├── data/                   # 📊 Fetch APIs (RTE, ENTSOE-E, Open-Meteo)
│   ├── models/                 # 🧠 ML (Random Forest, prédictions)
│   ├── trading/                # 💰 Recommandations, signals
│   ├── analysis/               # 📈 Supply/demand, arbitrage
│   └── arbitrage/              # 💱 Cross-border opportunities
├── data/                       # 🗄️ SQLite databases
└── _archive/                   # 📦 Anciennes versions (NE PAS UTILISER)
```

---

## 🔑 Configuration

### Variables d'environnement (`.env`)
```bash
# RTE APIs (OAuth2)
RTE_WHOLESALE_CREDENTIALS=xxx
RTE_GENERATION_CREDENTIALS=xxx
RTE_CONSUMPTION_CREDENTIALS=xxx
RTE_FORECAST_CREDENTIALS=xxx

# ENTSOE-E API
ENTSOE_API_TOKEN=xxx
```

### Streamlit Cloud (`.streamlit/secrets.toml`)
Copier les mêmes credentials dans l'interface Streamlit Cloud.

---

## 🌐 Déploiement

**URL Live** : https://meteo-trader-btjtstc9gy72eupdtzsgzj.streamlit.app/

**Auto-deploy** : Chaque `git push` redéploie automatiquement sur Streamlit Cloud.

---

## 🛠️ Technologies

- **Frontend** : Streamlit
- **ML** : Random Forest, XGBoost, scikit-learn
- **Data** : pandas, numpy
- **Viz** : Plotly, matplotlib
- **APIs** : RTE (OAuth2), ENTSOE-E, Open-Meteo
- **DB** : SQLite

---

## 📖 Documentation Complète

Voir `_archive/` pour l'ancienne documentation et les fichiers de spécifications.

---

## 👨‍💻 Auteur

Paul-Antoine Sage  
Account Executive & AI Enthusiast

---

**Version actuelle** : Design Cursor + Sidebar + ML Recommendations  
**Dernière mise à jour** : 16 décembre 2024
