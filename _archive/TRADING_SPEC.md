# 📊 MétéoTrader Pro - Spécifications Trading Professionnel

## 🎯 CAS D'USAGE PRINCIPAL

**Trader en commodités électricité** travaillant pour une entreprise de négoce d'énergie.

### Mission
- Garantir des prix fixes à des clients institutionnels (hôpitaux, universités, industries, collectivités)
- Acheter l'électricité sur le marché de gros (spot/futures) au meilleur moment
- Dégager une marge = Prix garanti client - Prix d'achat réel - Coûts opérationnels

### Exemple Concret
```
CLIENT: Hôpital public
CONTRAT: 10 GWh sur 1 an
PRIX GARANTI: 85€/MWh (fixe)
STRATÉGIE TRADER:
  → Acheter sur marché spot quand < 80€/MWh
  → Hedger le risque avec futures si prix monte
  → Objectif: acheter en moyenne à 78€/MWh
  → MARGE = (85 - 78) × 10 000 MWh = 70 000€
```

---

## 🔑 BESOINS CRITIQUES DU TRADER

### 1. GESTION DE PORTEFEUILLE CONTRATS
**Problème actuel:** Pas de système de suivi des contrats clients.

**Besoin:**
- Liste des contrats actifs (client, volume, prix garanti, période)
- P&L par contrat (combien je gagne/perds sur chaque contrat?)
- Exposition totale (combien de MWh je dois acheter cette semaine?)
- Alertes si prix spot > prix garanti (risque de perte!)

**Données à stocker:**
```sql
Contrats:
- id, client_name, volume_mwh, guaranteed_price, 
  start_date, end_date, delivery_pattern (peak/offpeak/baseload)
  
Positions:
- contract_id, timestamp, volume_bought, price_bought, 
  volume_remaining, current_pnl
```

---

### 2. SIGNAUX D'ACHAT OPTIMAUX
**Problème actuel:** Signaux BUY/SELL trop simplistes.

**Besoin:**
- **Quand acheter?** Fenêtres optimales avec probabilité de hausse/baisse
- **Combien acheter?** Suggestion de volume basée sur exposition
- **À quel prix?** Prix cible vs prix actuel
- **Quel risque?** Volatilité attendue, VaR (Value at Risk)

**Calculs requis:**
```python
# Fenêtre d'achat optimale
if predicted_price < guaranteed_price - safety_margin:
    if volatility < threshold:
        if volume_remaining > 0:
            → SIGNAL BUY FORT
            → Volume suggéré: min(volume_remaining, optimal_lot_size)
            → Prix limite: predicted_price + spread
            → Gain attendu: (guaranteed - predicted) × volume
```

---

### 3. RISK MANAGEMENT
**Problème actuel:** Pas de métriques de risque.

**Besoin:**
- **VaR (Value at Risk):** Perte maximale probable à 95% sur 1 jour/1 semaine
- **Exposition nette:** Volume acheté vs volume contracté
- **Stress testing:** "Et si le prix monte à 150€/MWh demain?"
- **Hedge ratio:** Pourcentage du portefeuille couvert

**Métriques:**
```
Portfolio VaR (95%, 1 jour):
  → Perte max probable = -15 000€
  
Exposition:
  → Volume contracté: 100 MWh/jour
  → Volume acheté: 60 MWh/jour
  → Exposition nette: -40 MWh/jour (À ACHETER)
  
Stress Scenario (Prix +30%):
  → Impact P&L: -50 000€
  → Marge restante: 20 000€
  → ⚠️ ALERTE: Hedger 20 MWh maintenant!
```

---

### 4. MARKET INTELLIGENCE (TEMPS RÉEL)
**Problème actuel:** Données statiques, pas d'alertes.

**Besoin:**
- **Prix spot live** (ticker temps réel)
- **Alertes critiques:**
  - Prix > seuil (ex: >100€/MWh)
  - Production nucléaire -10% (hausse prix immédiate)
  - Interconnexion France-Allemagne coupée
  - Prévision canicule/vague de froid
- **News feed:** Actualités impactant les prix (Reuters, Bloomberg)

---

### 5. ARBITRAGE EUROPÉEN
**Problème actuel:** Carte statique, pas d'analyse de spread.

**Besoin:**
- **Spread analysis:**
  ```
  France: 75€/MWh
  Allemagne: 60€/MWh
  Spread: +15€/MWh
  
  → Opportunité: Acheter en Allemagne, vendre en France
  → Coût interconnexion: 3€/MWh
  → Marge nette: 12€/MWh
  → Volume max: 1000 MWh (capacité interconnexion)
  → SIGNAL: ARBITRAGE FORT
  ```

- **Carte interactive:**
  - Spreads en temps réel
  - Capacités d'interconnexion disponibles
  - Coûts de transport
  - Opportunités d'arbitrage calculées

---

### 6. BACKTESTING & PERFORMANCE
**Problème actuel:** Pas d'historique des décisions.

**Besoin:**
- **Historique des trades:**
  - Quand j'ai acheté, à quel prix?
  - Était-ce une bonne décision?
  - Accuracy: combien de fois le prix a monté après mon achat?
  
- **Performance metrics:**
  ```
  Marge moyenne: 4.2€/MWh (+5.3%)
  Win rate: 68% des achats profitables
  Meilleur trade: +12 000€ (acheté à 65, garanti à 85)
  Pire trade: -3 500€ (acheté à 95, spot baissé à 70)
  ROI annuel: +18%
  ```

- **Strategy optimization:**
  - Backtester une stratégie sur données historiques
  - "Et si j'avais toujours acheté quand prédiction < 75€?"

---

## 🎨 REDESIGN INTERFACE

### Principes UX pour Traders Professionnels

#### ❌ À ÉVITER (design actuel)
- Minimalisme excessif
- Information dispersée dans des onglets
- Pas de données en temps réel
- Métriques "jolies" mais pas actionnables

#### ✅ À VISER (design pro)
- **Information density:** Maximum d'infos utiles en un coup d'œil
- **Real-time:** Tickers live, charts qui bougent
- **Color coding:** Rouge/Vert pour profit/loss, Zones d'achat/vente
- **Alerts:** Visuelles + sonores pour événements critiques
- **Customization:** Widgets déplaçables (comme Bloomberg)

---

### Layout Proposé: "Trading Desk View"

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔴 LIVE │ FR: 78.5€ ▼-2.1%  │ P&L Jour: +2,340€ │ Expo: -45 MWh │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┬─────────────────────┬───────────────────┐
│ 📊 PRIX & PRÉDICTIONS│ 💼 CONTRATS ACTIFS  │ 🎯 SIGNAUX TRADE  │
├─────────────────────┼─────────────────────┼───────────────────┤
│                     │ Hospital Nord       │ 🟢 BUY SIGNAL     │
│   [CHART]           │ 50 MWh @ 85€        │ ━━━━━━━━━━━━━━    │
│   - Spot (bleu)     │ P&L: +1,200€ ▲      │ Score: 87/100     │
│   - Prédit (orange) │ Expo: -15 MWh       │                   │
│   - Zones BUY (vert)│                     │ Acheter MAINTENANT│
│   - Your trades (⭐) │ Univ. Paris         │ Volume: 15 MWh    │
│                     │ 30 MWh @ 82€        │ Prix: < 76€/MWh   │
│   Hover: Opportunité│ P&L: +900€ ▲        │ Gain attendu: 135€│
│   Prix: 74€         │ Expo: -10 MWh       │                   │
│   Gain si buy: +11€ │                     │ Fenêtre: 2h       │
│                     │ [+ 8 autres]        │ Volatilité: Basse │
└─────────────────────┴─────────────────────┴───────────────────┘

┌─────────────────────┬─────────────────────┬───────────────────┐
│ ⚠️ ALERTES & NEWS   │ 🗺️ ARBITRAGE EUROPE│ 📈 RISK MGMT      │
├─────────────────────┼─────────────────────┼───────────────────┤
│ 🔴 URGENT           │     [MAP]           │ VaR (95%, 1j):    │
│ Prix > 100€ à 18h   │                     │ -12,500€          │
│ → HEDGE NOW!        │ FR → DE: +12€/MWh   │                   │
│                     │ Opportunité forte   │ Exposition:       │
│ 🟠 ATTENTION        │                     │ ▓▓▓▓▓░░░ 65%      │
│ Nucléaire -5%       │ FR → ES: +8€/MWh    │                   │
│ Prix +10€ prévu     │ Opportunité moyenne │ Stress (+30%):    │
│                     │                     │ Impact: -45k€     │
│ 🟢 INFO             │ FR ← IT: -5€/MWh    │ → Hedger 20 MWh   │
│ Vent fort demain    │ Pas intéressant     │                   │
│ Prix -15€ prévu     │                     │                   │
└─────────────────────┴─────────────────────┴───────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 📊 PERFORMANCE (Mois en cours)                                   │
├─────────────────────────────────────────────────────────────────┤
│ Marge Moy: 4.2€/MWh │ Win Rate: 68% │ ROI: +18% │ Best: +12k€  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Couleurs & Codes Visuels

**Zones de Prix (sur chart):**
- 🟢 **Zone BUY:** Prix < Prix garanti - 5€ (opportunité forte)
- 🟡 **Zone WATCH:** Prix garanti -5€ à -2€ (opportunité moyenne)
- 🔴 **Zone RISK:** Prix > Prix garanti (danger! hedger!)

**Signaux:**
- 🟢 **BUY:** Score > 75, volatilité basse, gain > 3€/MWh
- 🟡 **WAIT:** Score 50-75, attendre meilleur timing
- 🔴 **HEDGE:** Prix spot > garanti, protéger exposition
- ⚫ **HOLD:** Aucune action recommandée

**P&L:**
- 🟢 **Positif:** Vert avec ▲
- 🔴 **Négatif:** Rouge avec ▼
- ⚪ **Neutre:** Gris

---

## 🛠️ PLAN D'IMPLÉMENTATION

### Phase 1: Backend - Gestion Contrats & P&L (2-3h)
**Fichiers:**
- `src/trading/contracts.py` → CRUD contrats, calcul P&L
- `src/trading/portfolio.py` → Exposition, risk metrics
- `src/data/database.py` → Nouvelles tables (contracts, trades)

**Tables:**
```sql
contracts (
  id, client_name, volume_mwh, guaranteed_price_eur_mwh,
  start_date, end_date, delivery_type, created_at
)

trades (
  id, contract_id, timestamp, volume_mwh, price_eur_mwh,
  trade_type (buy/sell), created_at
)

portfolio_snapshot (
  timestamp, total_exposure_mwh, total_pnl_eur, var_1day_eur
)
```

---

### Phase 2: Signaux Trading Avancés (1-2h)
**Fichiers:**
- `src/trading/signals.py` → Refonte complète
  - `calculate_buy_signal(price, prediction, contracts, volatility)`
  - `suggest_volume(contracts, risk_tolerance)`
  - `calculate_expected_gain(buy_price, guaranteed_price, volume)`

**Nouveaux signaux:**
```python
BuySignal:
  - score: 0-100
  - action: BUY | WAIT | HEDGE
  - volume_suggested: MWh
  - price_target: €/MWh
  - expected_gain: €
  - time_window: hours
  - confidence: 0-1
  - reasoning: "Prix prédit 72€, garanti 85€, gain 13€/MWh, volatilité basse"
```

---

### Phase 3: Risk Management (1-2h)
**Fichiers:**
- `src/trading/risk.py`
  - `calculate_var(portfolio, confidence=0.95, horizon=1)`
  - `calculate_exposure(contracts, trades)`
  - `stress_test(portfolio, price_shock=+0.30)`
  - `hedge_recommendation(exposure, var, risk_limit)`

---

### Phase 4: Frontend - Trading Desk UI (3-4h)
**Fichiers:**
- `app.py` → Refonte complète avec nouveau layout
- `assets/style.css` → Trading desk theme

**Nouveau layout:**
- Header: Live ticker + P&L jour + Exposition
- Grid 3×3 de widgets:
  1. Chart prix avec zones BUY/RISK
  2. Liste contrats actifs (scrollable)
  3. Signaux d'achat (cards)
  4. Alertes & News
  5. Carte arbitrage Europe
  6. Risk dashboard
  7. Performance metrics
  8. Backtesting (optionnel)
  9. Settings (optionnel)

**Interactions:**
- Click sur chart → Détails de l'opportunité
- Click sur contrat → Vue détaillée + historique trades
- Click sur signal BUY → Modal avec confirmation
- Hover sur carte → Détails spread + capacité interconnexion

---

### Phase 5: Real-time & Alerts (2h)
**Fichiers:**
- `src/alerts/engine.py`
  - `check_price_alerts(current_price, thresholds)`
  - `check_production_alerts(production_data)`
  - `check_pnl_alerts(contracts)`

**Streamlit workaround pour "real-time":**
```python
# Auto-refresh toutes les 60s
st_autorefresh(interval=60000, key="autorefresh")

# WebSocket simulé avec polling
if st.session_state.get('last_update', 0) < time.time() - 60:
    refresh_data()
    st.session_state.last_update = time.time()
```

---

### Phase 6: Arbitrage Européen (1h)
**Fichiers:**
- `src/trading/arbitrage.py`
  - `calculate_spread(price_fr, price_de, transport_cost)`
  - `find_opportunities(european_prices, interconnection_capacity)`

**Nouveau visuel carte:**
- Flèches colorées entre pays (vert=opportunité, rouge=non profitable)
- Épaisseur flèche = taille opportunité
- Chiffres sur flèches = spread net
- Click → Détails (prix achat, prix vente, coût transport, marge)

---

## 📊 MÉTRIQUES DE SUCCÈS

### Pour le Trader
- **Augmentation marge:** +15-25% grâce à meilleurs timings d'achat
- **Réduction risque:** VaR mieux maîtrisé, moins de pertes
- **Time saved:** 30 min/jour gagnées vs tableau Excel manuel
- **Win rate:** 70%+ d'achats profitables

### Pour la Plateforme
- **Actionable signals:** 100% des signaux avec volume + prix + timing
- **Real-time:** Refresh < 60s
- **Accuracy:** Prédictions < 5€/MWh d'erreur
- **UX:** Information density élevée, 0 clic superflu

---

## 🎯 DIFFÉRENCES CLÉs vs VERSION ACTUELLE

| Aspect | Avant (Dashboard Démo) | Après (Trading Desk Pro) |
|--------|------------------------|--------------------------|
| **Audience** | Grand public / Curieux | Trader professionnel |
| **Layout** | Onglets séquentiels | Grid multi-widgets |
| **Données** | Historique statique | Live ticker + refresh |
| **Signaux** | Génériques (BUY/SELL) | Précis (volume, prix, timing) |
| **Contracts** | ❌ Aucun | ✅ Gestion complète |
| **P&L** | ❌ Aucun | ✅ Par contrat + total |
| **Risk** | ❌ Aucun | ✅ VaR, exposition, stress test |
| **Arbitrage** | Carte statique | Spreads calculés + opportunités |
| **Alerts** | ❌ Aucune | ✅ Prix, production, P&L |
| **Backtesting** | ❌ Aucun | ✅ Performance historique |
| **Actions** | Informationnel | Décisionnel (buy now!) |

---

## 💰 VALEUR BUSINESS

### Pour un Trader
**Scénario:**
- 10 contrats × 50 MWh/mois × 12 mois = 6 000 MWh/an
- Marge actuelle sans outil: 3€/MWh
- Marge avec MétéoTrader Pro: 5€/MWh (+66%)
- **Gain annuel: +12 000€**

### Pour une Entreprise de Négoce
- 5 traders utilisant la plateforme
- **Gain annuel: +60 000€**
- ROI: Infini (plateforme gratuite/interne)

---

## 🚀 PROCHAINE ÉTAPE

**Veux-tu qu'on démarre par:**
1. **Phase 1 (Backend contrats)** → Base solide pour tout le reste
2. **Phase 4 (UI redesign)** → Impact visuel immédiat pour portfolio
3. **Prototype papier** → On dessine ensemble le layout idéal

**Ou tu veux qu'on code direct Phase 1 + 4 ce soir ?** (3-4h de travail)

