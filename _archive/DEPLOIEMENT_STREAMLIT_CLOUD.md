# 🚀 Déployer sur Streamlit Cloud (Gratuit & 24/7)

## ✅ Ton App Tournera en Permanence !

**Plus besoin de lancer de commande !**  
→ URL permanente accessible partout  
→ Tourne 24/7 gratuitement  
→ Se met à jour automatiquement avec GitHub

---

## 📋 ÉTAPES (5 minutes)

### 1️⃣ **Va sur Streamlit Cloud**

👉 https://share.streamlit.io/

### 2️⃣ **Connecte ton GitHub**

- Click "Sign in with GitHub"
- Autorise Streamlit Cloud

### 3️⃣ **Déploie l'App**

- Click "New app"
- Sélectionne le repo: `paul-antoine-presti-ai/meteo-trader`
- Branch: `main`
- Main file path: `app.py`
- Click "Deploy!"

### 4️⃣ **Configure les Secrets**

**IMPORTANT** : Ajoute tes tokens API dans Streamlit Cloud

- Click sur "⚙️ Settings" (en bas à droite)
- Click sur "Secrets"
- Copie-colle le contenu de `.streamlit/secrets.toml` :

```toml
# RTE APIs
RTE_WHOLESALE_CREDENTIALS = "MjljNzE2Y2EtNWUzNS00MWY2LTkzNDEtMWNjY2I3ODBhM2MzOmNkZTQ4NTY0LWYwYmMtNDg5Mi04MzdhLTlhNjFiZmExZjMxMw=="
RTE_GENERATION_CREDENTIALS = "Yjc5YjZhODQtYzRjNS00YmEyLThkZjktYzEyYjA2YzczZWQ2OjEzOTc3NGFlLWYyZWItNDA5YS1iYjE5LTQ4YzQwNWMwOGE2Yg=="
RTE_CONSUMPTION_CREDENTIALS = "ZjY2YjQyY2ItMmMyYS00ZDQ4LTk1YzYtOWIwMWM0NGQyODEyOjhjMTQ4MDBhLTMyMGEtNDQwNC04N2VmLWQ4MTQ0ZjU1N2Q0ZQ=="
RTE_FORECAST_CREDENTIALS = "ODBlNDNiMjktZGUyMy00MWFhLTk4NGItYTg0YjZkMzEzNDRkOmJkNDliODdiLTM2NGMtNDEwMy04MzRkLTViY2MwYzcyNDFkMA=="

# ENTSOE-E API
ENTSOE_API_TOKEN = "a3624a65-8e38-4c5f-86f7-beaf1d936baf"
```

- Click "Save"

### 5️⃣ **C'est Prêt ! 🎉**

Streamlit va :
- Installer les dépendances (`requirements.txt`)
- Lancer l'app
- Te donner une URL permanente

**Exemple URL :**
```
https://meteo-trader-[ton-id].streamlit.app
```

---

## ✨ AVANTAGES STREAMLIT CLOUD

### **Gratuit**
✅ Hébergement gratuit  
✅ Pas de carte bancaire  
✅ Pas de limite de temps

### **Automatique**
✅ Se met à jour avec GitHub (push = déploiement auto)  
✅ Tourne 24/7  
✅ Pas besoin de serveur

### **Facile**
✅ Déploiement en 1 clic  
✅ Logs en direct  
✅ Redémarrage automatique si crash

---

## 🔄 MISES À JOUR AUTO

**Quand tu push sur GitHub :**
```bash
git add .
git commit -m "Update"
git push origin main
```

→ **Streamlit Cloud redéploie automatiquement !**

Pas besoin de faire quoi que ce soit !

---

## 📊 MONITORING

Une fois déployé, tu peux :
- ✅ Voir les logs en temps réel
- ✅ Redémarrer l'app si besoin
- ✅ Voir le nombre de visiteurs
- ✅ Changer les secrets

---

## 🎯 RÉSULTAT

**Avant :**
```bash
# À chaque fois
./run.sh
# Tourne seulement quand ton Mac est allumé
```

**Après :**
```
https://meteo-trader-xxx.streamlit.app
# Tourne 24/7 partout dans le monde ! 🌍
```

---

## 🔗 LIEN POUR TON PORTFOLIO

Une fois déployé, ajoute le lien dans ton portfolio :

**`/Users/paul-antoinesage/Desktop/portfolio/data/projects.ts` :**

```typescript
{
  title: "MétéoTrader Pro",
  description: "Plateforme de trading électricité...",
  demo: "https://meteo-trader-xxx.streamlit.app", // ← TON URL
  github: "https://github.com/paul-antoine-presti-ai/meteo-trader"
}
```

---

## ⚡ LANCE LE DÉPLOIEMENT !

👉 https://share.streamlit.io/

**En 5 minutes ton app tourne 24/7 ! 🚀**

