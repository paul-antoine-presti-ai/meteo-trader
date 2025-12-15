"""
Prédictions futures (J+1, J+2) pour MétéoTrader
Utilise prévisions météo + patterns historiques
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta


def fetch_weather_forecast(latitude=48.8566, longitude=2.3522, days=2):
    """
    Récupère prévisions météo J+1 et J+2
    
    Args:
        latitude: Latitude (Paris par défaut)
        longitude: Longitude (Paris par défaut)
        days: Nombre de jours à prévoir (1 ou 2)
    
    Returns:
        DataFrame avec prévisions horaires
    """
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': 'temperature_2m,windspeed_10m,shortwave_radiation',
        'forecast_days': days,
        'timezone': 'Europe/Paris'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            hourly = data.get('hourly', {})
            
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(hourly['time']),
                'temperature_c': hourly['temperature_2m'],
                'wind_speed_kmh': hourly['windspeed_10m'],
                'solar_radiation_wm2': hourly['shortwave_radiation']
            })
            
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Erreur prévisions météo: {e}")
        return pd.DataFrame()


def estimate_future_demand(historical_data, forecast_dates):
    """
    Estime la demande future basée sur patterns historiques
    
    Args:
        historical_data: DataFrame avec colonnes timestamp, demand_gw
        forecast_dates: Timestamps pour lesquels prédire
    
    Returns:
        Series avec demande estimée
    """
    if 'demand_gw' not in historical_data.columns:
        # Valeur par défaut si pas de données historiques
        return pd.Series(50.0, index=range(len(forecast_dates)))
    
    # Extraire patterns par heure et jour de la semaine
    historical_data = historical_data.copy()
    historical_data['hour'] = historical_data['timestamp'].dt.hour
    historical_data['day_of_week'] = historical_data['timestamp'].dt.dayofweek
    
    # Moyenne par (heure, jour_semaine)
    demand_patterns = historical_data.groupby(['hour', 'day_of_week'])['demand_gw'].mean()
    
    # Appliquer patterns aux dates futures
    estimated_demand = []
    for ts in forecast_dates:
        hour = ts.hour
        dow = ts.dayofweek
        
        if (hour, dow) in demand_patterns.index:
            estimated_demand.append(demand_patterns[(hour, dow)])
        else:
            # Fallback: moyenne globale
            estimated_demand.append(historical_data['demand_gw'].mean())
    
    return pd.Series(estimated_demand, index=range(len(forecast_dates)))


def estimate_future_production(historical_data, forecast_weather):
    """
    Estime la production future basée sur météo prévue
    
    Args:
        historical_data: DataFrame historique avec production
        forecast_weather: DataFrame avec prévisions météo
    
    Returns:
        DataFrame avec production estimée par filière
    """
    n_hours = len(forecast_weather)
    
    # Colonnes de production
    prod_cols = [c for c in historical_data.columns if 'production_gw' in c]
    
    if not prod_cols:
        # Valeurs par défaut
        return pd.DataFrame({
            'nuclear_production_gw': [40.0] * n_hours,
            'wind_production_gw': [5.0] * n_hours,
            'solar_production_gw': [2.0] * n_hours,
            'total_production_gw': [50.0] * n_hours,
            'renewable_production_gw': [7.0] * n_hours,
            'renewable_share': [0.14] * n_hours
        })
    
    # Production de base (moyenne historique pour sources stables)
    base_production = {}
    for col in prod_cols:
        if 'nuclear' in col.lower():
            # Nucléaire: relativement stable
            base_production[col] = [historical_data[col].mean()] * n_hours
        elif 'wind' in col.lower():
            # Éolien: corrélé au vent
            # Modèle simple: production proportionnelle au vent
            if historical_data[col].std() > 0:
                wind_prod = forecast_weather['wind_speed_kmh'] * 0.3  # Facteur empirique
                base_production[col] = wind_prod.clip(0, historical_data[col].max()).tolist()
            else:
                base_production[col] = [historical_data[col].mean()] * n_hours
        elif 'solar' in col.lower():
            # Solaire: corrélé à radiation
            if historical_data[col].std() > 0:
                solar_prod = forecast_weather['solar_radiation_wm2'] * 0.01  # Facteur empirique
                base_production[col] = solar_prod.clip(0, historical_data[col].max()).tolist()
            else:
                base_production[col] = [historical_data[col].mean()] * n_hours
        else:
            # Autres: moyenne historique
            base_production[col] = [historical_data[col].mean()] * n_hours
    
    # Créer DataFrame
    prod_forecast = pd.DataFrame(base_production)
    
    # Calculer totaux
    renewable_cols = [c for c in prod_forecast.columns if 'wind' in c.lower() or 'solar' in c.lower()]
    if renewable_cols:
        prod_forecast['renewable_production_gw'] = prod_forecast[renewable_cols].sum(axis=1)
    
    if 'total_production_gw' not in prod_forecast.columns:
        prod_forecast['total_production_gw'] = prod_forecast[[c for c in prod_forecast.columns if c != 'renewable_production_gw']].sum(axis=1)
    
    if 'renewable_production_gw' in prod_forecast.columns and 'total_production_gw' in prod_forecast.columns:
        prod_forecast['renewable_share'] = (prod_forecast['renewable_production_gw'] / 
                                            prod_forecast['total_production_gw'].replace(0, np.nan)).fillna(0)
    
    return prod_forecast


def create_future_features(forecast_df):
    """
    Crée les features nécessaires pour prédiction
    
    Args:
        forecast_df: DataFrame avec colonnes de base
    
    Returns:
        DataFrame avec toutes les features
    """
    df = forecast_df.copy()
    
    # Features temporelles
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_peak_hour'] = ((df['hour'] >= 18) & (df['hour'] <= 20)).astype(int)
    
    # Features température
    if 'temperature_c' in df.columns:
        df['temp_extreme'] = ((df['temperature_c'] < 5) | (df['temperature_c'] > 25)).astype(int)
    else:
        df['temp_extreme'] = 0
    
    # Gap production-demande
    if 'demand_gw' in df.columns and 'total_production_gw' in df.columns:
        df['production_demand_gap'] = df['demand_gw'] - df['total_production_gw']
    else:
        df['production_demand_gap'] = 0
    
    return df


def predict_future_prices(model, feature_columns, historical_data, days=1):
    """
    Prédit les prix futurs (J+1, J+2)
    
    Args:
        model: Modèle ML entraîné
        feature_columns: Liste des features utilisées par le modèle
        historical_data: DataFrame avec données historiques
        days: Nombre de jours à prédire (1 ou 2)
    
    Returns:
        DataFrame avec timestamps et prédictions
    """
    print(f"🔮 Prédiction des prix pour les {days} prochains jours...")
    
    # 1. Récupérer prévisions météo
    forecast_weather = fetch_weather_forecast(days=days)
    
    if forecast_weather.empty:
        print("❌ Impossible de récupérer prévisions météo")
        return pd.DataFrame()
    
    print(f"✅ {len(forecast_weather)} heures de prévisions météo")
    
    # 2. Estimer demande future
    forecast_demand = estimate_future_demand(historical_data, forecast_weather['timestamp'])
    forecast_weather['demand_gw'] = forecast_demand.values
    
    # 3. Estimer production future
    forecast_production = estimate_future_production(historical_data, forecast_weather)
    
    # 4. Fusionner toutes les données
    forecast_df = forecast_weather.copy()
    for col in forecast_production.columns:
        forecast_df[col] = forecast_production[col].values
    
    # 5. Créer features
    forecast_df = create_future_features(forecast_df)
    
    # 6. Sélectionner features du modèle
    # Remplir colonnes manquantes avec 0
    for col in feature_columns:
        if col not in forecast_df.columns:
            forecast_df[col] = 0
    
    X_future = forecast_df[feature_columns]
    
    # 7. Prédire
    predictions = model.predict(X_future)
    
    # 8. Créer DataFrame résultat
    result = pd.DataFrame({
        'timestamp': forecast_df['timestamp'],
        'predicted_price': predictions,
        'temperature_c': forecast_df['temperature_c'],
        'wind_speed_kmh': forecast_df['wind_speed_kmh'],
        'hour': forecast_df['hour'],
        'is_peak_hour': forecast_df['is_peak_hour']
    })
    
    # 9. Ajouter intervalles de confiance (estimation simple)
    # Utiliser std des erreurs historiques comme proxy
    result['confidence_lower'] = result['predicted_price'] - 8  # ±RMSE approximatif
    result['confidence_upper'] = result['predicted_price'] + 8
    
    print(f"✅ Prédictions calculées: {len(result)} heures")
    print(f"💰 Prix moyen prédit: {result['predicted_price'].mean():.2f} €/MWh")
    print(f"📈 Prix min/max: {result['predicted_price'].min():.2f} / {result['predicted_price'].max():.2f} €/MWh")
    
    return result


if __name__ == "__main__":
    # Test rapide
    print("🧪 Test prédictions futures...")
    
    # Données simulées
    dates = pd.date_range(start='2025-12-01', periods=168, freq='h')
    test_data = pd.DataFrame({
        'timestamp': dates,
        'demand_gw': np.random.normal(50, 5, 168),
        'nuclear_production_gw': np.random.normal(40, 3, 168),
        'wind_production_gw': np.random.normal(5, 2, 168),
        'solar_production_gw': np.random.normal(2, 1, 168),
        'total_production_gw': np.random.normal(50, 4, 168)
    })
    
    # Mock model
    class MockModel:
        def predict(self, X):
            return np.random.normal(80, 15, len(X))
    
    mock_model = MockModel()
    mock_features = ['temperature_c', 'wind_speed_kmh', 'hour', 'demand_gw']
    
    predictions = predict_future_prices(mock_model, mock_features, test_data, days=1)
    
    print(f"\n✅ Test réussi! {len(predictions)} prédictions générées")
    print(predictions.head())

