# ⚡ QUICKSTART - Phase 1 (CE SOIR - 1h)

## 🎯 Objectif

Valider qu'on peut prédire les prix de l'électricité avec météo + production.

**Résultat attendu:** R² > 0.80, RMSE < 10€/MWh

---

## 🚀 Setup (5 min)

### 1. Ouvrir le Terminal

```bash
cd /Users/paul-antoinesage/Desktop/meteo-trader
```

### 2. Créer environnement virtuel

```bash
# Créer venv
python3 -m venv venv

# Activer
source venv/bin/activate
```

### 3. Installer dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Temps:** ~2-3 minutes

---

## 📓 Lancer Jupyter (1 min)

```bash
jupyter notebook
```

→ Un navigateur s'ouvre automatiquement

---

## ⚡ Exécuter le Notebook (50 min)

### Dans Jupyter:

1. **Naviguer vers:** `notebooks/1_poc_simulated.ipynb`

2. **Exécuter toutes les cellules:**
   - Menu: `Kernel` → `Restart & Run All`
   - OU: Exécuter cellule par cellule avec `Shift + Enter`

3. **Attendre l'exécution:** ~5-10 minutes
   - La plupart des cellules sont instantanées
   - L'entraînement Random Forest prend 1-2 min

---

## 📊 Ce que vous verrez

### ✅ Cellule 1-2: Setup
- Imports réussis
- Timestamp

### ✅ Cellule 3: Données générées
- 8,760 heures (1 an)
- 10 colonnes
- Aperçu dataset

### ✅ Cellule 4-6: Exploration
- Distribution prix
- Time series
- Corrélations

### ✅ Cellule 7: Features
- 17 features créées
- Dataset enrichi

### ✅ Cellule 8-9: Train/Test
- Split 80/20
- 7,008 train / 1,752 test

### ✅ Cellule 10: Modèle
- Entraînement Random Forest
- Barre de progression

### ✅ Cellule 11-14: Évaluation
- **R² Score:** ~0.85-0.90
- **RMSE:** ~5-8 €/MWh
- **MAE:** ~3-5 €/MWh
- Graphiques prédictions vs réel

### ✅ Cellule 15: Feature Importance
- Top features identifiées
- Graphique importance

### ✅ Cellule 16-17: Prédictions 48h
- Simulation prédictions
- Visualisation

### ✅ Cellule 18: Conclusions
- Résumé complet
- Prochaines étapes

### ✅ Cellule 19: Sauvegarde
- Fichiers CSV créés dans `data/simulated/`

---

## 🎯 Métriques Attendues

| Métrique | Target | Attendu |
|----------|--------|---------|
| **R²** | > 0.80 | ~0.85-0.90 |
| **RMSE** | < 10 €/MWh | ~5-8 €/MWh |
| **MAE** | < 8 €/MWh | ~3-5 €/MWh |

**Si atteint:** ✅ Proof of Concept validé!

---

## 📁 Fichiers Créés

Après exécution, dans `data/simulated/`:

- `data_1year.csv` - Dataset complet
- `predictions_48h.csv` - Prédictions
- `feature_importance.csv` - Features importantes
- `metrics.csv` - Métriques performance

---

## 🔧 Troubleshooting

### Erreur: "No module named 'sklearn'"

```bash
pip install scikit-learn
```

### Erreur: "Module src not found"

→ Vérifier que vous êtes dans le bon dossier:
```bash
pwd
# Devrait afficher: /Users/paul-antoinesage/Desktop/meteo-trader
```

### Jupyter ne s'ouvre pas

```bash
# Vérifier installation
jupyter --version

# Si pas installé
pip install jupyter notebook
```

### Kernel crash pendant Random Forest

→ Réduire n_estimators dans la cellule 10:
```python
model = RandomForestRegressor(
    n_estimators=50,  # Au lieu de 100
    ...
)
```

---

## ⏱️ Timeline Détaillée

```
00:00 - Setup venv + install          (5 min)
00:05 - Lancer Jupyter                 (1 min)
00:06 - Cellules 1-9 (setup + data)   (10 min)
00:16 - Cellule 10 (training)          (2 min)
00:18 - Cellules 11-14 (eval)          (5 min)
00:23 - Cellules 15-19 (analyse)      (10 min)
00:33 - Lecture résultats             (10 min)
00:43 - Notes & prochaines étapes     (7 min)
─────────────────────────────────────────────
TOTAL                                  ~50 min
```

Avec marge: **1 heure** ✅

---

## 🚀 Après Phase 1

### Si tout marche (attendu):

**R² > 0.85** → ✅ Concept validé!

**Prochaines étapes:**

1. **Demain matin (5 min):**
   - S'inscrire sur https://data.rte-france.com/
   - Attendre validation email

2. **Demain soir (30-45 min):**
   - Notebook Phase 2: `2_real_data_pipeline.ipynb`
   - Brancher APIs réelles
   - Re-run modèle

3. **Après (1-2h):**
   - Dashboard Streamlit
   - Optimisation modèle
   - Ajout géopolitique

---

## 💡 Tips

### Pour gagner du temps:

1. **Exécuter tout d'un coup:**
   - `Kernel` → `Restart & Run All`
   - Allez vous chercher un café ☕

2. **Lire pendant l'exécution:**
   - Les markdown cells expliquent tout
   - Préparez questions pour Phase 2

3. **Screenshots:**
   - Prenez des screenshots des graphiques
   - Utiles pour portfolio plus tard

---

## 📊 Analyse Rapide

### Questions à se poser:

1. **R² est bon?** (> 0.80)
   - ✅ Oui → Modèle fonctionne
   - ❌ Non → Bug dans le code (improbable)

2. **Quelles features sont importantes?**
   - Demande > production ?
   - Vent important ?
   - Heure du jour ?

3. **Erreurs sont normales?**
   - Distribution centrée sur 0 ?
   - Pas de pattern suspect ?

4. **Prédictions 48h sont bonnes?**
   - Suivent la tendance réelle ?
   - Erreur acceptable ?

---

## 🎉 Success Criteria

### Phase 1 réussie si:

- ✅ Notebook s'exécute sans erreur
- ✅ R² > 0.80
- ✅ Graphiques générés
- ✅ Fichiers CSV créés
- ✅ Insights compréhensibles

**Si tout ✅ → Prêt pour Phase 2 demain!**

---

## 📞 Support

### Si problème:

1. Vérifier Python version: `python3 --version` (doit être 3.9+)
2. Vérifier packages: `pip list | grep -E "pandas|sklearn|matplotlib"`
3. Relire messages d'erreur (souvent explicites)

---

## 🎯 Objectif Final

**Ce soir:** Valider le concept

**Demain:** Données réelles

**Après:** Portfolio-ready

---

**Bon courage! En 1h vous aurez un proof of concept validé! 🚀**

**Prêt? Let's go!**

```bash
cd /Users/paul-antoinesage/Desktop/meteo-trader
source venv/bin/activate
jupyter notebook
```

⚡ MétéoTrader - Prédire le futur de l'énergie!

