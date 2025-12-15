# ⚡ MétéoTrader - Prédiction Prix Électricité France

> Dashboard ML temps réel pour prédire les prix de l'électricité en France via données météo et production énergétique

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52-red.svg)](https://streamlit.io/)
[![ML](https://img.shields.io/badge/ML-Scikit--learn-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 **Objectif**

Prédire les prix de l'électricité en France (48h) en utilisant **Machine Learning**, données **météorologiques** (Open-Meteo) et **production énergétique** (RTE) en temps réel.

---

## 📊 **Performance**

| Métrique | Valeur | Description |
|----------|--------|-------------|
| **R² Score** | 0.8128 | 81% de la variance expliquée |
| **MAE** | 5.51 €/MWh | Erreur moyenne absolue |
| **RMSE** | 7.83 €/MWh | Erreur quadratique moyenne |
| **Précision** | 92.7% | (100% - 7.3% erreur) |
| **Dataset** | 744 heures | 31 jours de données réelles |

---

## 🚀 **Démo Live**

**🌐 Dashboard interactif:** [meteo-trader.streamlit.app](https://meteo-trader.streamlit.app)

---

## ✨ **Features**

- ⚡ **Prédictions temps réel** avec Random Forest (R²=0.81)
- 🌡️ **Impact météo** sur les prix (température, vent, radiation solaire)
- 🔋 **Production par filière** (nucléaire, éolien, solaire, hydro, gaz)
- 💰 **Génération prix réalistes** basée sur loi offre/demande
- 📊 **Dashboard Streamlit** moderne avec graphiques Plotly interactifs
- 🎨 **Dark mode élégant** avec touches orange (Mistral-inspired)
- 🔐 **OAuth2 RTE** avec intégration 4 APIs
- 📈 **Feature importance** et insights business

---

## 🛠️ **Technologies**

| Catégorie | Technologies |
|-----------|-------------|
| **Backend** | Python 3.13 |
| **ML** | Scikit-learn (Random Forest) |
| **Data** | Pandas, NumPy |
| **Viz** | Matplotlib, Seaborn, Plotly |
| **Dashboard** | Streamlit |
| **APIs** | RTE OAuth2, Open-Meteo |

---

## 📁 **Structure**

```
meteo-trader/
├── app.py                          # Dashboard Streamlit
├── requirements.txt                # Dépendances
├── .streamlit/
│   ├── config.toml                 # Config UI
│   └── secrets.toml.example        # Template secrets
├── src/
│   ├── data/
│   │   ├── simulate.py             # Données simulées
│   │   └── fetch_apis_oauth.py     # APIs RTE OAuth2
│   ├── features/
│   │   └── generate_prices.py      # Génération prix
│   └── models/
├── notebooks/
│   ├── 1_poc_simulated.ipynb       # Phase 1: POC
│   └── 2_real_data_sandbox.ipynb   # Phase 2: Données réelles
└── data/
```

---

## 🚀 **Quick Start**

### **1. Cloner le repo**
```bash
git clone https://github.com/paul-antoine-presti-ai/meteo-trader.git
cd meteo-trader
```

### **2. Créer environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
```

### **3. Installer dépendances**
```bash
pip install -r requirements.txt
```

### **4. Configurer credentials RTE**
Créez un fichier `.env`:
```bash
RTE_WHOLESALE_CREDENTIALS=votre_credential_base64
RTE_GENERATION_CREDENTIALS=votre_credential_base64
RTE_CONSUMPTION_CREDENTIALS=votre_credential_base64
RTE_FORECAST_CREDENTIALS=votre_credential_base64
```

> **Obtenir credentials:** [RTE Data Portal](https://data.rte-france.com/)

### **5. Lancer le dashboard**
```bash
streamlit run app.py
```

Dashboard accessible sur: `http://localhost:8501`

---

## 📊 **Cas d'Usage Business**

### **1. Trading Électricité**
- Anticiper variations prix J+1
- Optimiser achats/ventes
- **ROI:** 2-5% économies

### **2. Optimisation Industrielle**
- Planifier production heures creuses
- Réduire facture électricité
- **ROI:** 10-15% économies

### **3. Production Renouvelable**
- Prévoir revenus vente
- Optimiser stockage batteries
- Planification maintenance

### **4. Grid Management**
- Anticiper pics demande
- Équilibrage réseau
- Prévention black-out

---

## 📈 **Résultats**

### **Graphiques Dashboard:**
- 📈 Prédictions vs Prix réels (time series)
- 🌡️ Corrélation Température-Prix
- 💨 Corrélation Vent-Prix
- ⚡ Production par filière (stacked area)
- 🎯 Feature importance (bar chart)

### **Métriques Clés:**
- R² = 0.81 (excellent pour un MVP!)
- Erreur moyenne: 5.51€ (7.3%)
- 16 features engineering
- 744h données réelles

---

## 🔮 **Roadmap**

### **Court terme**
- [ ] Accès API RTE production (3-12 mois données)
- [ ] Hyperparameter tuning
- [ ] Cross-validation

### **Moyen terme**
- [ ] Tester XGBoost, LightGBM
- [ ] Facteurs géopolitiques (NewsAPI)
- [ ] Prédictions J+2, J+3

### **Long terme**
- [ ] API REST (FastAPI)
- [ ] Mobile app
- [ ] Alertes temps réel (email/SMS)

---

## 📝 **Documentation**

- 📘 [Quick Start](QUICKSTART.md)
- 🚀 [Déploiement Streamlit](DEPLOYMENT_STREAMLIT.md)
- 📊 [Résumé Projet](PROJECT_SUMMARY.md)

---

## 👤 **Auteur**

**Paul-Antoine Sage**  
Account Executive & AI Enthusiast  
Passionné par l'IA appliquée aux cas d'usage business réels

📧 Contact: [Votre Email]  
💼 LinkedIn: [Votre LinkedIn]  
🌐 Portfolio: [Votre Portfolio]

---

## 📄 **License**

MIT License - Voir [LICENSE](LICENSE) pour détails

---

## 🙏 **Remerciements**

- **RTE France** pour les APIs de données électriques
- **Open-Meteo** pour les données météorologiques gratuites
- **Streamlit** pour le framework de dashboard
- **Scikit-learn** pour les outils ML

---

## 🌟 **Star ce projet!**

Si ce projet vous a été utile, n'hésitez pas à lui donner une ⭐ sur GitHub!

---

*Projet réalisé en décembre 2025*
