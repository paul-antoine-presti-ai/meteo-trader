"""
Génération de prix réalistes basés sur loi offre/demande
Utilise les VRAIES données de production et consommation
"""

import pandas as pd
import numpy as np


def generate_realistic_prices(df):
    """
    Génère des prix €/MWh réalistes basés sur:
    - Gap production/demande (loi offre/demande)
    - Heure du jour (heures de pointe)
    - Production renouvelable (effet sur le prix)
    - Jour de la semaine
    
    Args:
        df: DataFrame avec colonnes:
            - timestamp
            - demand_gw (ou total_production_gw si pas de demand)
            - total_production_gw
            - renewable_production_gw (optionnel)
    
    Returns:
        Series avec prix en €/MWh
    """
    
    # Prix de base France (moyenne historique)
    BASE_PRICE = 85.0  # €/MWh
    
    # Calculer gap production-demande
    if 'demand_gw' in df.columns:
        # Gap = Demande - Production
        # Si gap > 0 → Demande > Production → Prix ↑
        # Si gap < 0 → Production > Demande → Prix ↓
        gap = df['demand_gw'].fillna(df['total_production_gw']) - df['total_production_gw']
    else:
        gap = pd.Series(0, index=df.index)
    
    # Normaliser le gap (% de la demande moyenne)
    mean_demand = gap.abs().mean() if gap.abs().mean() > 0 else 1
    gap_normalized = gap / mean_demand
    
    # Composante 1: Impact du gap (forte influence!)
    # 1% de gap → ±5€/MWh
    price_gap = gap_normalized * 5.0
    
    # Composante 2: Heures de pointe (18h-20h)
    hour = df['timestamp'].dt.hour if 'timestamp' in df.columns else pd.Series(12, index=df.index)
    
    price_peak = np.where(
        (hour >= 18) & (hour <= 20),
        25.0,  # +25€ heures de pointe
        np.where(
            (hour >= 7) & (hour <= 9),
            15.0,  # +15€ matin
            np.where(
                (hour >= 0) & (hour <= 6),
                -15.0,  # -15€ nuit
                0.0
            )
        )
    )
    
    # Composante 3: Production renouvelable
    # Plus de renouvelables → Prix baisse (merit order effect)
    if 'renewable_share' in df.columns:
        renewable_share = df['renewable_share'].fillna(0)
    elif 'renewable_production_gw' in df.columns and 'total_production_gw' in df.columns:
        renewable_share = df['renewable_production_gw'] / df['total_production_gw'].replace(0, np.nan)
        renewable_share = renewable_share.fillna(0).clip(0, 1)
    else:
        renewable_share = pd.Series(0.3, index=df.index)  # Défaut 30%
    
    # 1% de renouvelable en plus → -0.3€
    price_renewable = -(renewable_share * 30)
    
    # Composante 4: Jour de la semaine
    dow = df['timestamp'].dt.dayofweek if 'timestamp' in df.columns else pd.Series(0, index=df.index)
    price_weekend = np.where(
        dow >= 5,  # Weekend
        -10.0,  # -10€ weekend (moins de demande industrielle)
        0.0
    )
    
    # Composante 5: Variabilité (bruit réaliste)
    np.random.seed(42)
    noise = np.random.normal(0, 5, len(df))  # ±5€ de variation aléatoire
    
    # Prix final
    price = BASE_PRICE + price_gap + price_peak + price_renewable + price_weekend + noise
    
    # Limites réalistes (prix négatifs rares mais possibles)
    price = np.clip(price, -20, 300)  # France: rarement < -20€ ou > 300€
    
    return pd.Series(price, index=df.index, name='price_eur_mwh')


def add_price_features(df):
    """
    Ajoute des features liées aux prix (pour analyse)
    
    Returns:
        DataFrame enrichi
    """
    df = df.copy()
    
    # Générer les prix
    df['price_eur_mwh'] = generate_realistic_prices(df)
    
    # Features additionnelles pour analyse
    if 'timestamp' in df.columns:
        # Prix moyens par heure (rolling average)
        df = df.sort_values('timestamp')
        df['price_ma_3h'] = df['price_eur_mwh'].rolling(window=3, min_periods=1).mean()
        df['price_ma_12h'] = df['price_eur_mwh'].rolling(window=12, min_periods=1).mean()
        
        # Variation de prix (pour détecter volatilité)
        df['price_change_1h'] = df['price_eur_mwh'].diff()
        df['price_volatility_3h'] = df['price_eur_mwh'].rolling(window=3, min_periods=1).std()
    
    return df


if __name__ == "__main__":
    # Test avec données synthétiques
    from datetime import datetime, timedelta
    
    # Créer dataset test
    dates = pd.date_range(start='2025-12-07', periods=168, freq='H')
    
    test_df = pd.DataFrame({
        'timestamp': dates,
        'demand_gw': np.random.normal(50, 5, 168),  # 50 GW ± 5
        'total_production_gw': np.random.normal(50, 3, 168),  # 50 GW ± 3
        'renewable_production_gw': np.random.normal(15, 5, 168).clip(0, None),  # 15 GW ± 5
    })
    
    # Générer prix
    test_df = add_price_features(test_df)
    
    print("=" * 60)
    print("🧪 TEST GÉNÉRATION PRIX")
    print("=" * 60)
    print(f"\n📊 {len(test_df)} points générés")
    print(f"\n💰 Statistiques prix:")
    print(f"  Moyenne: {test_df['price_eur_mwh'].mean():.2f} €/MWh")
    print(f"  Médiane: {test_df['price_eur_mwh'].median():.2f} €/MWh")
    print(f"  Min:     {test_df['price_eur_mwh'].min():.2f} €/MWh")
    print(f"  Max:     {test_df['price_eur_mwh'].max():.2f} €/MWh")
    print(f"  Écart-type: {test_df['price_eur_mwh'].std():.2f} €/MWh")
    
    print(f"\n🔍 Aperçu:")
    print(test_df[['timestamp', 'demand_gw', 'total_production_gw', 
                    'renewable_production_gw', 'price_eur_mwh']].head(10))
    
    # Vérifier corrélations
    print(f"\n📈 Corrélations avec le prix:")
    correlations = test_df[['demand_gw', 'total_production_gw', 
                             'renewable_production_gw', 'price_eur_mwh']].corr()['price_eur_mwh']
    print(correlations)

