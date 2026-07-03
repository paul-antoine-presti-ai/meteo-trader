# ⚡ MétéoTrader Pro Europe - Spécifications

## 🎯 Vision Unique

**Une seule app** qui prédit les prix d'électricité dans **5 pays européens** et recommande **où acheter** et **à qui vendre** pour maximiser la marge.

---

## 🌍 Pays Intégrés

### 1. 🇫🇷 France
- **Mix énergétique** : 70% nucléaire, 10% éolien, 10% solaire, 10% autres
- **Caractéristiques** : Prix stable, peu sensible météo
- **Prédiction basée sur** : Demande, nucléaire, météo

### 2. 🇩🇪 Allemagne
- **Mix énergétique** : 40% renouvelables (éolien+solaire), 35% charbon, 15% gaz, 10% nucléaire
- **Caractéristiques** : Très volatile, très sensible météo (vent/soleil)
- **Prédiction basée sur** : Météo (vent++), demande, charbon

### 3. 🇪🇸 Espagne
- **Mix énergétique** : 50% renouvelables (solaire++), 30% gaz, 20% autres
- **Caractéristiques** : Volatile, très sensible soleil
- **Prédiction basée sur** : Météo (soleil++), demande, gaz

### 4. 🇮🇹 Italie
- **Mix énergétique** : 40% gaz, 30% renouvelables, 20% importations, 10% autres
- **Caractéristiques** : Prix élevés, dépendance importations
- **Prédiction basée sur** : Importations, gaz, météo

### 5. 🇬🇧 UK
- **Mix énergétique** : 35% gaz, 30% éolien offshore, 20% nucléaire, 15% autres
- **Caractéristiques** : Prix élevés, très sensible vent offshore
- **Prédiction basée sur** : Météo (vent maritime), gaz, demande

---

## 📊 Architecture App

### **1 PAGE - 4 SECTIONS**

```
┌─────────────────────────────────────────────────────────┐
│ ⚡ MétéoTrader Pro Europe                              │
│ Prix Spot FR: 78€ │ Opportunités: 3 │ Marge: +450€    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🎯 RECOMMANDATION PRINCIPALE                            │
├─────────────────────────────────────────────────────────┤
│ 💰 ARBITRAGE FORT - Score: 92/100                       │
│                                                         │
│ ACHETER:  🇩🇪 Allemagne @ 65€/MWh (dans 3h)           │
│ VENDRE:   🇮🇹 Italie     @ 88€/MWh                     │
│                                                         │
│ Spread brut:    23€/MWh                                 │
│ Coût transport: -3€/MWh                                 │
│ MARGE NETTE:    20€/MWh                                 │
│                                                         │
│ Volume optimal: 50 MWh                                  │
│ GAIN TOTAL:     1,000€                                  │
│                                                         │
│ Raison: Forte production éolienne en Allemagne         │
│         + Faible production en Italie                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🗺️ CARTE EUROPE - VUE D'ENSEMBLE                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         🇬🇧 UK                                          │
│         82€                                             │
│          ↓ +10€ (VENDRE)                                │
│                                                         │
│    🇩🇪 DE ────────→ 🇫🇷 FR ────────→ 🇮🇹 IT          │
│    65€   -7€       78€   +10€       88€                │
│    ↑ ACHETER              ↑ VENDRE                     │
│                                                         │
│              🇪🇸 ES                                     │
│              72€                                        │
│              ↕ Neutre                                   │
│                                                         │
│ Flèches = Opportunités d'arbitrage                     │
│ Verte = Forte, Orange = Moyenne, Grise = Faible        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📊 COMPARAISON PAYS (48h)                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ [GRAPHIQUE: 5 courbes superposées]                     │
│                                                         │
│ 🇫🇷 France (bleu)     : 75-82€  │ Stable              │
│ 🇩🇪 Allemagne (vert)  : 60-90€  │ Volatile ⚠️         │
│ 🇪🇸 Espagne (orange)  : 68-85€  │ Moyen               │
│ 🇮🇹 Italie (rouge)    : 80-95€  │ Élevé               │
│ 🇬🇧 UK (violet)       : 75-88€  │ Moyen-Élevé         │
│                                                         │
│ Zones d'arbitrage surlignées:                           │
│ - 14h-18h: Acheter DE (65€), Vendre IT (88€)           │
│ - 20h-23h: Acheter ES (70€), Vendre UK (85€)           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🎯 TOP 5 OPPORTUNITÉS                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. 🟢 DE→IT  │ 20€/MWh │ 14h │ 50 MWh │ +1,000€       │
│ 2. 🟢 ES→UK  │ 15€/MWh │ 20h │ 30 MWh │   +450€       │
│ 3. 🟡 FR→IT  │ 10€/MWh │ 18h │ 20 MWh │   +200€       │
│ 4. 🟡 DE→FR  │  8€/MWh │ 16h │ 25 MWh │   +200€       │
│ 5. 🟡 ES→FR  │  6€/MWh │ 12h │ 15 MWh │    +90€       │
│                                                         │
│ TOTAL MARGE POTENTIELLE: +1,940€ (sur 48h)             │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 Prédictions Multi-Pays

### Approche Simplifiée (Ce soir - 2h)

**Pour chaque pays :**
1. Récupérer météo (Open-Meteo) pour capitale
2. Appliquer un **modèle de prix** basé sur le mix énergétique
3. Formule simplifiée :

```python
# Allemagne (très sensible vent)
prix_DE = base_price_DE - (wind_speed * 2.5) + (demand_factor * 10)

# Espagne (très sensible soleil)
prix_ES = base_price_ES - (solar_radiation * 0.8) + (demand_factor * 8)

# France (stable, nucléaire)
prix_FR = base_price_FR + (demand_factor * 5) + (temperature_extreme * 3)

# Italie (élevé, dépendance gaz)
prix_IT = base_price_IT + (gas_price_factor * 15) + (demand_factor * 12)

# UK (élevé, vent offshore)
prix_UK = base_price_UK - (wind_speed * 1.8) + (gas_price_factor * 10)
```

**Prix de base** (moyennes réalistes) :
- France : 75€/MWh
- Allemagne : 72€/MWh
- Espagne : 78€/MWh
- Italie : 85€/MWh
- UK : 82€/MWh

### Approche Avancée (Plus tard - Si on a accès ENTSOE-E)

**ENTSOE-E Transparency Platform** (API gratuite, données réelles) :
- Prix spot réels par pays
- Production par type
- Échanges transfrontaliers
- Capacités d'interconnexion

---

## 💰 Moteur d'Arbitrage

### Calcul d'Opportunité

```python
def calculate_arbitrage(price_buy_country, price_sell_country, 
                       transport_cost, capacity_limit):
    """
    Calcule opportunité d'arbitrage entre 2 pays
    
    Returns:
        - spread_net: Marge nette (€/MWh)
        - volume_optimal: Volume max transférable (MWh)
        - gain_total: Gain total (€)
        - score: 0-100
    """
    # Spread brut
    spread_gross = price_sell_country - price_buy_country
    
    # Coûts transport (interconnexion)
    transport_cost_per_mwh = 3  # €/MWh (moyenne)
    
    # Spread net
    spread_net = spread_gross - transport_cost_per_mwh
    
    # Volume optimal (limité par capacité interconnexion)
    volume_optimal = min(capacity_limit, 100)  # Max 100 MWh pour simplicité
    
    # Gain total
    gain_total = spread_net * volume_optimal
    
    # Score (0-100)
    if spread_net < 5:
        score = 0  # Pas intéressant
    elif spread_net < 10:
        score = 50  # Moyen
    elif spread_net < 15:
        score = 75  # Bon
    else:
        score = 100  # Excellent
    
    return {
        'spread_net': spread_net,
        'volume_optimal': volume_optimal,
        'gain_total': gain_total,
        'score': score
    }
```

### Matrice d'Interconnexions

```python
# Capacités maximales (MW) - Simplifiées
INTERCONNECTIONS = {
    ('FR', 'DE'): 3000,  # France-Allemagne
    ('FR', 'ES'): 2800,  # France-Espagne
    ('FR', 'IT'): 3200,  # France-Italie
    ('FR', 'UK'): 2000,  # France-UK
    ('DE', 'FR'): 3000,
    ('ES', 'FR'): 2800,
    ('IT', 'FR'): 3200,
    ('UK', 'FR'): 2000,
    # Autres connexions directes
    ('DE', 'ES'): 0,     # Pas de connexion directe (via FR)
    ('DE', 'IT'): 0,
    # etc.
}

# Coûts transport (€/MWh)
TRANSPORT_COSTS = {
    ('FR', 'DE'): 2.5,
    ('FR', 'ES'): 3.0,
    ('FR', 'IT'): 3.5,
    ('FR', 'UK'): 4.0,
    # Inverses (mêmes coûts)
    ('DE', 'FR'): 2.5,
    ('ES', 'FR'): 3.0,
    ('IT', 'FR'): 3.5,
    ('UK', 'FR'): 4.0,
}
```

---

## 🎨 Design Minimaliste

### Palette de Couleurs

```css
/* Fond */
background: #0a0a0a;         /* Noir profond */

/* Cards */
card-bg: #1a1a1a;            /* Gris foncé */
border: #2a2a2a;             /* Gris border */

/* Texte */
text-primary: #ffffff;       /* Blanc */
text-secondary: #888888;     /* Gris clair */

/* Pays (codes couleur) */
france: #3b82f6;             /* Bleu */
germany: #10b981;            /* Vert */
spain: #f97316;              /* Orange */
italy: #ef4444;              /* Rouge */
uk: #8b5cf6;                 /* Violet */

/* Status */
buy-signal: #10b981;         /* Vert */
sell-signal: #ef4444;        /* Rouge */
neutral: #6b7280;            /* Gris */
```

### Typographie

```css
h1: 2rem, weight: 300       /* Ultra léger */
h2: 1.5rem, weight: 300
h3: 1.25rem, weight: 400
body: 1rem, weight: 400
small: 0.875rem, weight: 400
```

---

## 📁 Structure Fichiers

```
meteo-trader/
├── app_final.py                    # ✨ Nouvelle app unifiée
├── src/
│   ├── predictions/
│   │   ├── __init__.py
│   │   ├── france.py              # Prédictions FR (modèle ML)
│   │   ├── europe.py              # Prédictions autres pays (formules)
│   │   └── weather.py             # Météo multi-villes
│   ├── arbitrage/
│   │   ├── __init__.py
│   │   ├── engine.py              # Moteur d'arbitrage
│   │   ├── interconnections.py   # Données interconnexions
│   │   └── opportunities.py      # Calcul opportunités
│   └── trading/
│       └── recommendations.py     # Recommandations (déjà existant)
└── data/
    └── meteotrader.db             # SQLite
```

---

## 🚀 Plan d'Implémentation (Ce Soir - 3h)

### Phase 1 : Prédictions Multi-Pays (1h)
- [ ] Module `europe.py` avec formules simplifiées
- [ ] Météo pour 5 capitales (Open-Meteo)
- [ ] DataFrames prédictions par pays (48h)

### Phase 2 : Moteur d'Arbitrage (45min)
- [ ] Module `arbitrage/engine.py`
- [ ] Calcul spreads entre tous les pays
- [ ] Top 5 opportunités
- [ ] Recommandation principale

### Phase 3 : UI Unifiée (1h)
- [ ] 1 page, 4 sections
- [ ] Carte Europe (visuelle)
- [ ] Graphique comparaison 5 pays
- [ ] Top opportunités (table)

### Phase 4 : Tests (15min)
- [ ] Test prédictions
- [ ] Test arbitrage
- [ ] Test UI

---

## 🎯 Résultat Final

**Une seule app** qui :
✅ Prédit prix dans 5 pays européens
✅ Compare les marchés en temps réel
✅ Recommande où acheter et à qui vendre
✅ Calcule marges d'arbitrage
✅ Interface minimaliste et élégante
✅ Dark mode avec texte blanc

**Pour un trader :**
- Vision globale du marché européen
- Opportunités d'arbitrage identifiées
- Marges calculées automatiquement
- Recommandations actionnables

---

## 💬 Questions pour Validation

1. **Les 5 pays** (FR, DE, ES, IT, UK) te conviennent ?
2. **Prédictions simplifiées** (formules) OK pour ce soir ? (vs attendre ENTSOE-E)
3. **Design** : 1 page avec 4 sections, ça te va ?
4. **Nom final** : `app_final.py` ou autre idée ?

**Si OK → Je code directement ! 🚀**

