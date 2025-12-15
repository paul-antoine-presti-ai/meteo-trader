"""
Générateur de données simulées réalistes pour MétéoTrader
Simule 1 an de données horaires avec corrélations réalistes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_realistic_data(days=365, seed=42):
    """
    Génère un dataset simulé réaliste de prix d'électricité
    avec météo et production énergétique.
    
    Corrélations intégrées:
    - Vent fort → Production éolienne ↑ → Prix ↓
    - Températures extrêmes → Demande ↑ → Prix ↑
    - Nuit/Jour → Solaire ↑/↓ → Prix varie
    - Heure de pointe (8h-20h) → Demande ↑ → Prix ↑
    
    Args:
        days: Nombre de jours à générer (default: 365)
        seed: Random seed pour reproductibilité
    
    Returns:
        pd.DataFrame avec colonnes:
        - timestamp: DateTime
        - temperature_c: Température (°C)
        - wind_speed_kmh: Vitesse vent (km/h)
        - solar_radiation_wm2: Radiation solaire (W/m²)
        - nuclear_production_gw: Production nucléaire (GW)
        - wind_production_gw: Production éolienne (GW)
        - solar_production_gw: Production solaire (GW)
        - price_eur_mwh: Prix électricité (€/MWh)
    """
    
    np.random.seed(seed)
    
    # Génération timestamps horaires
    start_date = datetime(2023, 1, 1)
    hours = days * 24
    timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
    
    # Extraction features temporelles
    df = pd.DataFrame({'timestamp': timestamps})
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_year'] = df['timestamp'].dt.dayofyear
    df['month'] = df['timestamp'].dt.month
    
    # ========== MÉTÉO ==========
    
    # Température: Cycle saisonnier + variation journalière
    seasonal_temp = 15 + 10 * np.sin(2 * np.pi * df['day_of_year'] / 365)  # 5-25°C
    daily_variation = 3 * np.sin(2 * np.pi * df['hour'] / 24)  # +/- 3°C jour/nuit
    noise_temp = np.random.normal(0, 2, hours)
    df['temperature_c'] = seasonal_temp + daily_variation + noise_temp
    
    # Vent: Variable avec tendance saisonnière (plus en hiver)
    wind_seasonal = 15 + 10 * np.sin(2 * np.pi * (df['day_of_year'] + 90) / 365)
    wind_noise = np.random.gamma(3, 3, hours)  # Distribution asymétrique
    df['wind_speed_kmh'] = np.clip(wind_seasonal + wind_noise, 0, 80)
    
    # Radiation solaire: Zéro la nuit, max selon saison
    is_day = (df['hour'] >= 6) & (df['hour'] <= 20)
    hour_factor = np.sin(np.pi * (df['hour'] - 6) / 14)  # Courbe de jour
    hour_factor = np.where(is_day, hour_factor, 0)
    seasonal_radiation = 300 + 500 * np.sin(2 * np.pi * df['day_of_year'] / 365)
    df['solar_radiation_wm2'] = np.clip(seasonal_radiation * hour_factor + np.random.normal(0, 50, hours), 0, 1200)
    
    # ========== PRODUCTION ÉNERGÉTIQUE ==========
    
    # Nucléaire: Stable avec maintenance périodique
    base_nuclear = 45  # GW
    maintenance = np.where((df['day_of_year'] % 60) < 5, -10, 0)  # Maintenance tous les 60j
    df['nuclear_production_gw'] = base_nuclear + maintenance + np.random.normal(0, 2, hours)
    
    # Éolien: Corrélé au vent (avec rendement non linéaire)
    # Seuil minimum 15 km/h, max à 60 km/h, cut-off à 80 km/h
    wind_efficiency = np.clip((df['wind_speed_kmh'] - 15) / 45, 0, 1)
    wind_efficiency = np.where(df['wind_speed_kmh'] > 80, 0, wind_efficiency)  # Cut-off
    max_wind_capacity = 20  # GW installés
    df['wind_production_gw'] = wind_efficiency * max_wind_capacity + np.random.normal(0, 0.5, hours)
    df['wind_production_gw'] = np.clip(df['wind_production_gw'], 0, max_wind_capacity)
    
    # Solaire: Corrélé à la radiation
    solar_efficiency = df['solar_radiation_wm2'] / 1000  # 0-1.2
    max_solar_capacity = 15  # GW installés
    df['solar_production_gw'] = solar_efficiency * max_solar_capacity + np.random.normal(0, 0.3, hours)
    df['solar_production_gw'] = np.clip(df['solar_production_gw'], 0, max_solar_capacity)
    
    # Production totale
    df['total_production_gw'] = (df['nuclear_production_gw'] + 
                                   df['wind_production_gw'] + 
                                   df['solar_production_gw'])
    
    # ========== DEMANDE ==========
    
    # Demande: Cycle journalier + saisonnier + température
    base_demand = 60  # GW
    hourly_profile = np.where((df['hour'] >= 8) & (df['hour'] <= 20), 15, -5)  # Pointe jour
    seasonal_demand = 10 * (1 - np.sin(2 * np.pi * df['day_of_year'] / 365))  # Plus en hiver
    temp_impact = np.where(df['temperature_c'] < 5, 5, 0) + np.where(df['temperature_c'] > 25, 5, 0)
    df['demand_gw'] = base_demand + hourly_profile + seasonal_demand + temp_impact + np.random.normal(0, 3, hours)
    
    # ========== PRIX ==========
    
    # Prix base: Équilibre offre/demande
    base_price = 60  # €/MWh
    
    # Impact offre/demande
    balance = df['demand_gw'] - df['total_production_gw']
    price_from_balance = balance * 3  # 3€/MWh par GW de déséquilibre
    
    # Impact production renouvelable (plus de renouvelable = prix plus bas)
    renewable_share = (df['wind_production_gw'] + df['solar_production_gw']) / df['total_production_gw']
    price_renewable_impact = -20 * renewable_share  # Jusqu'à -20€/MWh
    
    # Impact heure de pointe
    peak_hour = np.where((df['hour'] >= 18) & (df['hour'] <= 20), 15, 0)
    
    # Impact température extrême (demande climatisation/chauffage)
    extreme_temp = np.where((df['temperature_c'] < 0) | (df['temperature_c'] > 30), 10, 0)
    
    # Impact maintenance nucléaire (prix monte si production nucléaire baisse)
    nuclear_impact = np.where(df['nuclear_production_gw'] < 40, 20, 0)
    
    # Prix final
    df['price_eur_mwh'] = (base_price + 
                            price_from_balance + 
                            price_renewable_impact + 
                            peak_hour + 
                            extreme_temp + 
                            nuclear_impact + 
                            np.random.normal(0, 5, hours))
    
    # Clipper prix (jamais négatif, max 200)
    df['price_eur_mwh'] = np.clip(df['price_eur_mwh'], 10, 200)
    
    # ========== NETTOYAGE ==========
    
    # Colonnes finales
    final_columns = [
        'timestamp',
        'temperature_c',
        'wind_speed_kmh',
        'solar_radiation_wm2',
        'nuclear_production_gw',
        'wind_production_gw',
        'solar_production_gw',
        'total_production_gw',
        'demand_gw',
        'price_eur_mwh'
    ]
    
    df = df[final_columns]
    
    # Arrondir pour lisibilité
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].round(2)
    
    return df


def add_lag_features(df, target='price_eur_mwh', lags=[1, 24, 168]):
    """
    Ajoute des features de lag (valeurs précédentes)
    
    Args:
        df: DataFrame avec column 'target'
        target: Nom de la colonne à lagger
        lags: Liste d'heures de lag (1h, 24h=1j, 168h=1sem)
    
    Returns:
        DataFrame avec colonnes lag ajoutées
    """
    df = df.copy()
    
    for lag in lags:
        df[f'{target}_lag_{lag}h'] = df[target].shift(lag)
    
    return df


if __name__ == "__main__":
    # Test du générateur
    print("🔄 Génération données simulées...")
    df = generate_realistic_data(days=30)  # 1 mois pour test rapide
    
    print(f"\n✅ Dataset généré: {len(df)} heures")
    print(f"\n📊 Aperçu:")
    print(df.head(10))
    
    print(f"\n📈 Statistiques:")
    print(df.describe())
    
    print(f"\n🔗 Corrélations avec prix:")
    corr_with_price = df.corr()['price_eur_mwh'].sort_values(ascending=False)
    print(corr_with_price)

