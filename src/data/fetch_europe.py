"""
Récupération données multi-pays européens
Combine ENTSOE-E + Open-Meteo pour prédictions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data.entsoe_api import EntsoeClient
import requests


def fetch_european_prices(countries=['FR', 'DE', 'ES', 'IT', 'GB'], days=7):
    """
    Récupère prix spot pour plusieurs pays européens
    
    Args:
        countries: Liste codes pays
        days: Nombre de jours d'historique
    
    Returns:
        Dict {country_code: DataFrame}
    """
    client = EntsoeClient()
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    results = {}
    
    for country in countries:
        print(f"📊 Récupération {EntsoeClient.COUNTRY_NAMES[country]}...")
        
        try:
            df = client.get_day_ahead_prices(
                country_code=country,
                start_date=str(start_date),
                end_date=str(end_date)
            )
            
            if not df.empty:
                # Agréger par heure (moyenne si résolution 15min)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.groupby(df['timestamp'].dt.floor('h')).agg({
                    'price_eur_mwh': 'mean'
                }).reset_index()
                
                df['country'] = country
                results[country] = df
                print(f"   ✅ {len(df)} heures récupérées")
            else:
                print(f"   ⚠️ Aucune donnée disponible")
                # Fallback: prix simulés basés sur moyennes
                results[country] = generate_fallback_prices(country, start_date, end_date)
        
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            results[country] = generate_fallback_prices(country, start_date, end_date)
    
    return results


def generate_fallback_prices(country, start_date, end_date):
    """
    Génère prix simulés si ENTSOE-E ne répond pas
    Basé sur moyennes réalistes par pays
    """
    # Prix de base moyens (€/MWh)
    BASE_PRICES = {
        'FR': 75,   # France: stable, nucléaire
        'DE': 72,   # Allemagne: volatile, renouvelables
        'ES': 78,   # Espagne: moyen, solaire
        'IT': 85,   # Italie: élevé, dépendance gaz
        'GB': 82,   # UK: élevé, gaz + éolien
    }
    
    base = BASE_PRICES.get(country, 75)
    
    # Générer timestamps
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) + timedelta(days=1)
    timestamps = pd.date_range(start, end, freq='h')
    
    # Simuler variations
    np.random.seed(hash(country) % 10000)  # Seed basé sur pays pour cohérence
    
    # Pattern journalier
    hours = timestamps.hour
    daily_pattern = np.sin((hours - 6) * np.pi / 12) * 10  # Peak 18h
    
    # Noise
    noise = np.random.randn(len(timestamps)) * 5
    
    # Prix final
    prices = base + daily_pattern + noise
    prices = np.maximum(prices, 20)  # Min 20€
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'price_eur_mwh': prices,
        'country': country
    })
    
    print(f"   ⚠️ Utilisation prix simulés (moyenne {base}€/MWh)")
    
    return df


def fetch_weather_multi_cities():
    """
    Récupère météo pour capitales européennes
    
    Returns:
        Dict {country: DataFrame}
    """
    # Coordonnées capitales
    CITIES = {
        'FR': {'lat': 48.8566, 'lon': 2.3522, 'name': 'Paris'},
        'DE': {'lat': 52.5200, 'lon': 13.4050, 'name': 'Berlin'},
        'ES': {'lat': 40.4168, 'lon': -3.7038, 'name': 'Madrid'},
        'IT': {'lat': 41.9028, 'lon': 12.4964, 'name': 'Rome'},
        'GB': {'lat': 51.5074, 'lon': -0.1278, 'name': 'Londres'},
    }
    
    weather_data = {}
    
    for country, city in CITIES.items():
        try:
            # Historique 7 jours
            url_historical = "https://api.open-meteo.com/v1/forecast"
            params_hist = {
                'latitude': city['lat'],
                'longitude': city['lon'],
                'hourly': 'temperature_2m,windspeed_10m,shortwave_radiation',
                'past_days': 7,
                'forecast_days': 0,
                'timezone': 'Europe/Paris'
            }
            
            response = requests.get(url_historical, params=params_hist, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                hourly = data.get('hourly', {})
                
                df = pd.DataFrame({
                    'timestamp': pd.to_datetime(hourly['time']),
                    'temperature_c': hourly['temperature_2m'],
                    'wind_speed_kmh': hourly['windspeed_10m'],
                    'solar_radiation_wm2': hourly['shortwave_radiation']
                })
                
                df['country'] = country
                weather_data[country] = df
                print(f"✅ Météo {city['name']}: {len(df)} heures")
            
        except Exception as e:
            print(f"❌ Météo {city['name']}: {e}")
    
    return weather_data


def predict_prices_europe(historical_prices, weather_data, forecast_hours=48):
    """
    Prédit prix futurs pour chaque pays
    Utilise formules simplifiées basées sur mix énergétique
    
    Args:
        historical_prices: Dict {country: DataFrame prix historiques}
        weather_data: Dict {country: DataFrame météo}
        forecast_hours: Heures à prédire
    
    Returns:
        Dict {country: DataFrame avec prédictions}
    """
    predictions = {}
    
    # Récupérer prévisions météo futures
    for country in historical_prices.keys():
        try:
            # Météo future
            weather_forecast = fetch_weather_forecast(country, days=2)
            
            if weather_forecast.empty:
                continue
            
            # Prix historique récent (pour baseline)
            recent_prices = historical_prices[country].tail(48)
            avg_price = recent_prices['price_eur_mwh'].mean()
            
            # Prédire en fonction du mix énergétique du pays
            predicted_prices = []
            
            for idx, row in weather_forecast.iterrows():
                wind = row['wind_speed_kmh']
                solar = row['solar_radiation_wm2']
                temp = row['temperature_c']
                hour = row['timestamp'].hour
                
                # Formules spécifiques par pays
                if country == 'FR':
                    # France: stable, peu sensible météo, pic demande 18-20h
                    price = avg_price
                    if hour >= 18 and hour <= 20:
                        price += 10  # Peak hours
                    if temp < 5 or temp > 30:
                        price += 5  # Température extrême
                
                elif country == 'DE':
                    # Allemagne: très sensible vent (éolien++)
                    price = avg_price - (wind - 15) * 1.5
                    price -= (solar / 200)  # Solaire aussi
                    if hour >= 18 and hour <= 20:
                        price += 8
                
                elif country == 'ES':
                    # Espagne: très sensible soleil
                    price = avg_price - (solar / 150)
                    if hour >= 12 and hour <= 16:
                        price -= 10  # Pic solaire
                    if hour >= 20 and hour <= 22:
                        price += 12  # Pic demande soir
                
                elif country == 'IT':
                    # Italie: prix élevés, peu de production propre
                    price = avg_price + 5  # Toujours un peu plus cher
                    if hour >= 18 and hour <= 21:
                        price += 15  # Forte demande soir
                
                elif country == 'GB':
                    # UK: sensible vent offshore
                    price = avg_price - (wind - 12) * 1.2
                    if hour >= 17 and hour <= 19:
                        price += 10
                
                else:
                    price = avg_price
                
                # Limites
                price = max(20, min(200, price))
                predicted_prices.append(price)
            
            weather_forecast['predicted_price'] = predicted_prices
            weather_forecast['confidence_lower'] = weather_forecast['predicted_price'] * 0.9
            weather_forecast['confidence_upper'] = weather_forecast['predicted_price'] * 1.1
            
            predictions[country] = weather_forecast[['timestamp', 'predicted_price', 'confidence_lower', 'confidence_upper']]
            
        except Exception as e:
            print(f"❌ Prédiction {country}: {e}")
    
    return predictions


def fetch_weather_forecast(country, days=2):
    """Récupère prévisions météo futures pour un pays"""
    CITIES = {
        'FR': {'lat': 48.8566, 'lon': 2.3522},
        'DE': {'lat': 52.5200, 'lon': 13.4050},
        'ES': {'lat': 40.4168, 'lon': -3.7038},
        'IT': {'lat': 41.9028, 'lon': 12.4964},
        'GB': {'lat': 51.5074, 'lon': -0.1278},
    }
    
    city = CITIES.get(country)
    if not city:
        return pd.DataFrame()
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': city['lat'],
        'longitude': city['lon'],
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
    
    except Exception as e:
        print(f"❌ Météo forecast {country}: {e}")
    
    return pd.DataFrame()


if __name__ == "__main__":
    print("🧪 Test récupération données européennes\n")
    
    # Test prix multi-pays
    print("📊 Récupération prix européens (7 derniers jours)...")
    prices = fetch_european_prices(countries=['FR', 'DE', 'ES'], days=7)
    
    print(f"\n✅ {len(prices)} pays récupérés\n")
    
    for country, df in prices.items():
        if not df.empty:
            print(f"{EntsoeClient.COUNTRY_NAMES[country]}:")
            print(f"  Prix moyen: {df['price_eur_mwh'].mean():.2f}€/MWh")
            print(f"  Min: {df['price_eur_mwh'].min():.2f}€")
            print(f"  Max: {df['price_eur_mwh'].max():.2f}€")
            print()
    
    # Test prédictions
    print("\n🔮 Génération prédictions futures...")
    weather = {}  # Vide pour ce test
    predictions = predict_prices_europe(prices, weather, forecast_hours=48)
    
    print(f"✅ Prédictions pour {len(predictions)} pays")
    
    for country, df in predictions.items():
        if not df.empty:
            print(f"{EntsoeClient.COUNTRY_NAMES[country]}: {len(df)} heures prédites")

