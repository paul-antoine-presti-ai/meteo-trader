# ⚡ MétéoTrader Pro - Version Trading

Interface minimaliste pour traders d'électricité.

## 🎯 Ce qui change

### Design
- **Minimaliste** : Focus sur l'essentiel
- **Dark mode** : Fond noir, texte blanc
- **Simple** : 3 sections principales

### Fonctionnalités

#### 1️⃣ Recommandation du Modèle
- **BUY** : Opportunité d'achat détectée
- **HOLD** : Attendre un meilleur moment
- **HEDGE** : Protéger votre position (risque de perte)

Chaque recommandation inclut :
- Score de confiance (0-100)
- Volume recommandé
- Prix cible
- Gain attendu
- Explication détaillée

#### 2️⃣ Contrats Actifs
- Liste de vos contrats clients
- Volume, prix garanti, dates
- P&L estimé par contrat
- Ajout rapide de nouveaux contrats

#### 3️⃣ Alertes
- Prix élevé (>100€/MWh)
- Risque de perte (prix > garanti)
- Opportunités fortes (marge >10€/MWh)

Alertes avec 3 niveaux de sévérité :
- 🔴 **High** : Action immédiate requise
- 🟠 **Medium** : Surveiller
- 🔵 **Low** : Information

## 🚀 Lancement Rapide

### Option 1 : Script automatique
```bash
./run_trading.sh
```

### Option 2 : Manuel
```bash
source venv/bin/activate
streamlit run app_trading.py
```

L'application s'ouvre sur http://localhost:8501

## 📊 Workflow Trader

### 1. Ajouter vos contrats clients
- Client : "Hôpital Nord"
- Volume : 100 MWh
- Prix garanti : 85€/MWh
- Dates : 01/01/2025 - 31/12/2025

### 2. Consulter la recommandation
Le modèle analyse :
- Prix spot actuel
- Prédictions 48h
- Vos contrats
- Volatilité du marché

Et génère une recommandation :
```
💰 BUY - Score: 87/100

Prix actuel: 78€/MWh
Prix prédit optimal: 72€/MWh (dans 6h)
Prix garanti: 85€/MWh
Marge: 13€/MWh

Volume recommandé: 10 MWh
Gain attendu: 130€
```

### 3. Agir sur les alertes
- ⚠️ **Prix > garanti** → Hedger maintenant
- 💰 **Opportunité forte** → Acheter rapidement
- 📊 **Prix élevé** → Surveiller le marché

## 🔧 Configuration

### Contrats
Les contrats sont stockés dans la base SQLite (`data/meteotrader.db`).

Vous pouvez :
- Ajouter des contrats via l'interface
- Les modifier directement en base
- Les désactiver (status='cancelled')

### Alertes
Les alertes sont automatiques. Paramètres par défaut :
- Prix élevé : >100€/MWh
- Opportunité : marge >10€/MWh
- Risque : prix spot > prix garanti

Modifiable dans `src/trading/recommendations.py`

### Prédictions
Le modèle génère des prédictions 48h automatiquement.

Si le modèle n'est pas disponible, l'app utilise des prédictions simulées.

## 📁 Structure

```
meteo-trader/
├── app_trading.py              # ✨ Nouvelle interface minimaliste
├── run_trading.sh              # Script de lancement
├── src/
│   ├── data/
│   │   └── database.py         # ✅ Étendu (contrats, alertes)
│   └── trading/
│       ├── recommendations.py  # ✨ Nouveau moteur
│       └── signals.py          # Ancien (conservé)
└── data/
    └── meteotrader.db          # SQLite (auto-créé)
```

## 🆚 Ancienne vs Nouvelle Version

| Fonctionnalité | app.py (Ancien) | app_trading.py (Nouveau) |
|----------------|-----------------|---------------------------|
| **Interface** | 8 onglets complexes | 1 page, 3 sections |
| **Design** | Glassmorphism | Minimaliste dark |
| **Contrats** | ❌ Non | ✅ Oui |
| **Recommandations** | Signaux génériques | Recommandations personnalisées |
| **Alertes** | ❌ Non | ✅ Oui |
| **P&L** | ❌ Non | ✅ Estimé |
| **Complexité** | 1700+ lignes | ~550 lignes |

## 💡 Cas d'Usage

### Scénario 1 : Opportunité d'achat
```
1. Prix actuel: 78€/MWh
2. Prédiction: baisse à 70€/MWh dans 4h
3. Votre contrat: 85€/MWh garanti
4. Recommandation: BUY 15 MWh @ 70€/MWh
5. Gain: (85-70) × 15 = 225€
```

### Scénario 2 : Risque de perte
```
1. Prix actuel: 92€/MWh
2. Prédiction: hausse à 95€/MWh
3. Votre contrat: 85€/MWh garanti
4. Recommandation: HEDGE (protéger)
5. Action: Acheter futures ou réduire exposition
```

### Scénario 3 : Attendre
```
1. Prix actuel: 80€/MWh
2. Prédiction: stable autour de 79€/MWh
3. Votre contrat: 85€/MWh garanti
4. Recommandation: HOLD (marge insuffisante)
5. Action: Surveiller, attendre < 75€/MWh
```

## 🎯 Prochaines Améliorations

- [ ] Historique des trades (enregistrer achats)
- [ ] Calcul P&L réel (vs estimé)
- [ ] Backtesting de stratégies
- [ ] Intégration futures (hedging)
- [ ] Alertes par email/SMS
- [ ] Dashboard multi-marchés (Allemagne, Espagne)

## ⚙️ Paramètres Avancés

### Seuil de marge
Par défaut : 2€/MWh de sécurité

Modifier dans `recommendations.py` :
```python
safety_margin = 2  # Changer ici
```

### Volume par achat
Par défaut : 10% du volume total

Modifier dans `recommendations.py` :
```python
suggested_volume = total_volume * 0.1  # Changer ici
```

### Seuil de volatilité
Par défaut : 10€/MWh

Passer en paramètre :
```python
reco = engine.generate_recommendation(
    ...
    volatility_threshold=15  # Augmenter pour accepter plus de volatilité
)
```

## 🐛 Troubleshooting

### "Aucune recommandation"
→ Ajoutez au moins 1 contrat actif

### "Prédictions non disponibles"
→ Normal au premier lancement, l'app utilise des prédictions simulées

### "Erreur chargement données"
→ Vérifiez vos credentials RTE dans `.env`

### Base de données corrompue
```bash
rm data/meteotrader.db
# Redémarrer l'app (recrée la DB)
```

## 📞 Support

Questions ? Ouvrez une issue sur GitHub ou contactez l'équipe.

---

**MétéoTrader Pro** - Prédire pour mieux trader ⚡

