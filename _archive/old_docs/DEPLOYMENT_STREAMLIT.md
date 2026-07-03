# 🚀 Déploiement Dashboard Streamlit

## 🌐 **Option 1: Streamlit Cloud (GRATUIT & RECOMMANDÉ)**

### **Étapes:**

1. **Créer compte Streamlit Cloud**
   - Allez sur: https://share.streamlit.io
   - Connectez-vous avec GitHub

2. **Pusher le projet sur GitHub**
   ```bash
   cd /Users/paul-antoinesage/Desktop/meteo-trader
   git init
   git add .
   git commit -m "MétéoTrader Dashboard - ML Prix Électricité"
   git remote add origin https://github.com/VOTRE_USERNAME/meteo-trader.git
   git push -u origin main
   ```

3. **Déployer sur Streamlit Cloud**
   - Cliquez sur "New app"
   - Sélectionnez votre repo `meteo-trader`
   - Main file: `app.py`
   - Cliquez "Deploy"

4. **Configurer les Secrets**
   Dans les paramètres de l'app, ajoutez:
   ```toml
   RTE_WHOLESALE_CREDENTIALS = "MjljNzE2Y2EtNWUzNS00MWY2LTkzNDEtMWNjY2I3ODBhM2MzOmNkZTQ4NTY0LWYwYmMtNDg5Mi04MzdhLTlhNjFiZmExZjMxMw=="
   RTE_GENERATION_CREDENTIALS = "Yjc5YjZhODQtYzRjNS00YmEyLThkZjktYzEyYjA2YzczZWQ2OjEzOTc3NGFlLWYyZWItNDA5YS1iYjE5LTQ4YzQwNWMwOGE2Yg=="
   RTE_CONSUMPTION_CREDENTIALS = "ZjY2YjQyY2ItMmMyYS00ZDQ4LTk1YzYtOWIwMWM0NGQyODEyOjhjMTQ4MDBhLTMyMGEtNDQwNC04N2VmLWQ4MTQ0ZjU1N2Q0ZQ=="
   RTE_FORECAST_CREDENTIALS = "ODBlNDNiMjktZGUyMy00MWFhLTk4NGItYTg0YjZkMzEzNDRkOmJkNDliODdiLTM2NGMtNDEwMy04MzRkLTViY2MwYzcyNDFkMA=="
   ```

5. **Récupérer l'URL publique**
   - Exemple: `https://meteo-trader.streamlit.app`
   - Partageable sur votre portfolio!

---

## 🖥️ **Option 2: Local (Développement)**

```bash
cd /Users/paul-antoinesage/Desktop/meteo-trader
source venv/bin/activate
streamlit run app.py
```

URL: http://localhost:8501

---

## 📸 **Intégration Portfolio**

### **Dans votre portfolio Next.js:**

Ajoutez une carte projet:

```tsx
{
  id: 3,
  title: "MétéoTrader",
  description: "Dashboard ML prédisant les prix de l'électricité en France via météo et production énergétique",
  technologies: ["Python", "Streamlit", "Scikit-learn", "Plotly", "RTE API"],
  link: "https://meteo-trader.streamlit.app",
  github: "https://github.com/VOTRE_USERNAME/meteo-trader",
  image: "/projects/meteotrader.png",
  metrics: {
    accuracy: "81% R²",
    data: "744h données réelles",
    error: "7.3% erreur moyenne"
  }
}
```

### **Screenshots à inclure:**
1. Dashboard avec métriques (header)
2. Graphique prédictions vs réel
3. Feature importance
4. Production par filière

---

## 🎯 **Optimisations (Optionnel)**

### **Performance:**
- Cache données (déjà implémenté avec `@st.cache_data`)
- Optimiser chargement modèle
- Compresser images

### **Features supplémentaires:**
- Sélecteur de dates
- Export CSV/Excel
- Alertes prix (email/SMS)
- Comparaison modèles ML

---

## 📊 **Ressources**

- **Streamlit Docs:** https://docs.streamlit.io
- **Plotly Docs:** https://plotly.com/python/
- **RTE Data Portal:** https://data.rte-france.com

---

## 🎊 **Résultat Final**

✅ Dashboard live 24/7
✅ URL publique à partager
✅ Mise à jour automatique (si push GitHub)
✅ Gratuit et scalable
✅ Portfolio professionnel!

