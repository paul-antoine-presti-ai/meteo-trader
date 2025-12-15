# Changelog - MétéoTrader

## [v2.0.0] - 2025-12-16 - Timeline Unifiée 🎉

### ✨ Nouvelles Fonctionnalités
- **Timeline Live Unifiée**: Vue continue passé → présent → futur
  - 72h historique + 48h prédictions
  - Marker "MAINTENANT" temps réel avec bulle annotation
  - Zones colorées passé (bleu) / futur (orange)
  - Graphique interactif Plotly

- **Tracking Accuracy Temps Réel**: 
  - Métriques 1 heure (précision ultra-courte)
  - Métriques 24 heures (journalier)
  - Métriques 7 jours (hebdomadaire)
  - MAE, RMSE, MAPE calculés automatiquement

- **Base de Données SQLite**:
  - Stockage automatique prix réels
  - Stockage automatique prédictions
  - Historique complet avec timestamps
  - Calcul accuracy multi-périodes

- **6 Onglets Dashboard**:
  1. ⏱️ Timeline Live (NOUVEAU)
  2. 📈 Prédictions
  3. 🔮 Prévisions 48h
  4. 🌡️ Impact Météo
  5. ⚡ Production
  6. 🎯 Analyse

### 🐛 Corrections de Bugs
- **FutureWarning Pandas**: 'H' → 'h' pour floor()
- **Création dossier data**: os.makedirs() avec exist_ok
- **Production future**: Correction création DataFrame avec listes
- **Gestion erreurs**: Try/except robustes timeline/prédictions
- **Imports database**: Cache Streamlit optimisé

### 🔧 Améliorations Techniques
- Script de test complet (`test_app.py`)
- Documentation dossier data
- Requirements production séparés
- Template secrets Streamlit
- .gitignore amélioré (*.db, *.db-journal)

### 📚 Documentation
- README.md mis à jour
- CHANGELOG.md créé
- data/README.md ajouté
- Comments code améliorés

---

## [v1.0.0] - 2025-12-15 - MVP Initial

### ✨ Fonctionnalités Initiales
- Modèle Random Forest (R²=0.81)
- Intégration 4 APIs RTE + Open-Meteo
- Dashboard Streamlit 5 onglets
- Prédictions 48h avec intervalles confiance
- Feature importance et analyse
- Déploiement Streamlit Cloud

### 🎯 Métriques
- R² Score: 0.8128
- RMSE: 7.83 €/MWh
- MAE: 5.51 €/MWh
- Erreur: 7.3% du prix moyen
- 744h données réelles

---

## Prochaines Versions Potentielles

### [v2.1.0] - Améliorations ML
- [ ] XGBoost / LightGBM
- [ ] Hyperparameter tuning (GridSearch)
- [ ] Feature engineering avancé
- [ ] Cross-validation temporelle

### [v2.2.0] - Données & APIs
- [ ] Migration APIs RTE Production
- [ ] Historique 3-12 mois
- [ ] Intégration API géopolitique
- [ ] Cache API intelligent

### [v2.3.0] - Dashboard
- [ ] Alertes prix (notifications)
- [ ] Export données CSV/Excel
- [ ] Comparaison modèles
- [ ] Mode mobile optimisé

### [v3.0.0] - Production
- [ ] API REST FastAPI
- [ ] Authentification utilisateurs
- [ ] Multi-régions (EU, US)
- [ ] Scaling cloud (AWS/GCP)

