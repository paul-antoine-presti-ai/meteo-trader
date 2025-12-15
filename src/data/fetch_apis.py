"""
Connecteurs APIs pour données réelles
- RTE (OAuth2): Prix, Production, Consommation
- Open-Meteo: Météo
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Charger les credentials depuis .env
load_dotenv()

# Tokens RTE (base64 encoded: client_id:client_secret)
RTE_WHOLESALE_TOKEN = os.getenv('RTE_WHOLESALE_TOKEN')
RTE_GENERATION_TOKEN = os.getenv('RTE_GENERATION_TOKEN')
RTE_CONSUMPTION_TOKEN = os.getenv('RTE_CONSUMPTION_TOKEN')
RTE_FORECAST_TOKEN = os.getenv('RTE_FORECAST_TOKEN')

# ====================
# RTE APIs (OAuth2)
# ====================

RTE_BASE_URL = "https://digital.iservices.rte-france.com"
RTE_TOKEN_URL = "https://digital.iservices.rte-france.com/token/oauth/"

# Cache pour les access tokens
_access_tokens = {}

def get_rte_access_token(api_name, base64_token):
    """
    Obtient un access token OAuth2 pour une API RTE
    
    Args:
        api_name: Nom de l'API (pour le cache)
        base64_token: Token base64 (client_id:client_secret)
    
    Returns:
        Access token
    """
    # Vérifier cache (tokens valides ~1h)
    if api_name in _access_tokens:
        return _access_tokens[api_name]
    
    headers = {
        'Authorization': f'Basic {base64_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(RTE_TOKEN_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            _access_tokens[api_name] = access_token
            print(f"✅ Token OAuth2 obtenu pour {api_name}")
            return access_token
        else:
            print(f"❌ Erreur OAuth2 ({api_name}): {response.status_code}")
            print(f"   Réponse: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Erreur OAuth2: {e}")
        return None

def fetch_rte_wholesale_prices(start_date, end_date):
    """
    Récupère les prix EPEX Spot via API RTE Wholesale Market (OAuth2)
    
    Args:
        start_date: Date début (YYYY-MM-DD)
        end_date: Date fin (YYYY-MM-DD)
    
    Returns:
        DataFrame avec colonnes: timestamp, price_eur_mwh
    """
    url = f"{RTE_BASE_URL}/open_api/wholesale_market/v3/actual_market_data"
    
    # Obtenir access token OAuth2
    access_token = get_rte_access_token('wholesale', RTE_WHOLESALE_TOKEN)
    if not access_token:
        print("❌ Impossible d'obtenir le token OAuth2")
        return pd.DataFrame()
    
    params = {
        'start_date': f"{start_date}T00:00:00+01:00",
        'end_date': f"{end_date}T23:59:59+01:00"
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    print(f"🔄 Récupération prix RTE ({start_date} à {end_date})...")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parser la réponse RTE
            records = []
            if 'france_power_exchanges' in data:
                for item in data['france_power_exchanges']:
                    records.append({
                        'timestamp': pd.to_datetime(item['start_date']),
                        'price_eur_mwh': float(item.get('value', 0))
                    })
            
            df = pd.DataFrame(records)
            print(f"✅ {len(df)} prix récupérés")
            return df
        else:
            print(f"⚠️ Erreur API RTE: {response.status_code}")
            print(f"Message: {response.text[:200]}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return pd.DataFrame()


def fetch_rte_production(start_date, end_date):
    """
    Récupère la production par filière via API RTE (OAuth2)
    
    Returns:
        DataFrame avec: timestamp, nuclear_gw, wind_gw, solar_gw, etc.
    """
    url = f"{RTE_BASE_URL}/open_api/actual_generation/v1/actual_generations_per_production_type"
    
    # Obtenir access token OAuth2
    access_token = get_rte_access_token('generation', RTE_GENERATION_TOKEN)
    if not access_token:
        print("❌ Impossible d'obtenir le token OAuth2")
        return pd.DataFrame()
    
    params = {
        'start_date': f"{start_date}T00:00:00+01:00",
        'end_date': f"{end_date}T23:59:59+01:00"
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    print(f"🔄 Récupération production RTE...")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parser par type de production
            df_list = []
            if 'actual_generations_per_production_type' in data:
                for item in data['actual_generations_per_production_type']:
                    timestamp = pd.to_datetime(item['start_date'])
                    prod_type = item.get('production_type', 'unknown')
                    value_mw = float(item.get('value', 0))
                    value_gw = value_mw / 1000  # MW → GW
                    
                    df_list.append({
                        'timestamp': timestamp,
                        'production_type': prod_type,
                        'production_gw': value_gw
                    })
            
            df = pd.DataFrame(df_list)
            
            # Pivot pour avoir une colonne par type
            if not df.empty:
                df_pivot = df.pivot_table(
                    index='timestamp',
                    columns='production_type',
                    values='production_gw',
                    aggfunc='sum'
                ).reset_index()
                
                # Renommer colonnes
                rename_map = {
                    'NUCLEAR': 'nuclear_production_gw',
                    'WIND': 'wind_production_gw',
                    'SOLAR': 'solar_production_gw',
                    'HYDRO': 'hydro_production_gw',
                    'GAS': 'gas_production_gw',
                    'COAL': 'coal_production_gw',
                }
                df_pivot = df_pivot.rename(columns=rename_map)
                
                print(f"✅ {len(df_pivot)} points de production récupérés")
                return df_pivot
            else:
                return pd.DataFrame()
        else:
            print(f"⚠️ Erreur API Production: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return pd.DataFrame()


def fetch_rte_consumption(start_date, end_date):
    """
    Récupère la consommation via API RTE (OAuth2)
    
    Returns:
        DataFrame avec: timestamp, demand_gw
    """
    url = f"{RTE_BASE_URL}/open_api/consumption/v1/short_term"
    
    # Obtenir access token OAuth2
    access_token = get_rte_access_token('consumption', RTE_CONSUMPTION_TOKEN)
    if not access_token:
        print("❌ Impossible d'obtenir le token OAuth2")
        return pd.DataFrame()
    
    params = {
        'start_date': f"{start_date}T00:00:00+01:00",
        'end_date': f"{end_date}T23:59:59+01:00"
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    print(f"🔄 Récupération consommation RTE...")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            records = []
            if 'short_term' in data:
                for item in data['short_term']:
                    records.append({
                        'timestamp': pd.to_datetime(item['start_date']),
                        'demand_mw': float(item.get('value', 0))
                    })
            
            df = pd.DataFrame(records)
            if not df.empty:
                df['demand_gw'] = df['demand_mw'] / 1000  # MW → GW
                df = df[['timestamp', 'demand_gw']]
            
            print(f"✅ {len(df)} points de consommation récupérés")
            return df
        else:
            print(f"⚠️ Erreur API Consommation: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return pd.DataFrame()


# ====================
# Open-Meteo API
# ====================

def fetch_meteo_data(latitude=48.8566, longitude=2.3522, start_date=None, end_date=None):
    """
    Récupère données météo via Open-Meteo (Paris par défaut)
    GRATUIT - Aucune clé API requise!
    
    Args:
        latitude: Latitude (défaut: Paris)
        longitude: Longitude (défaut: Paris)
        start_date: Date début (YYYY-MM-DD)
        end_date: Date fin (YYYY-MM-DD)
    
    Returns:
        DataFrame avec: timestamp, temperature_c, wind_speed_kmh, solar_radiation_wm2
    """
    
    # Dates par défaut: dernier mois
    if start_date is None:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': 'temperature_2m,windspeed_10m,shortwave_radiation',
        'timezone': 'Europe/Paris'
    }
    
    print(f"🔄 Récupération météo Open-Meteo ({start_date} à {end_date})...")
    
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
            
            print(f"✅ {len(df)} points météo récupérés")
            return df
        else:
            print(f"⚠️ Erreur Open-Meteo: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return pd.DataFrame()


# ====================
# Fonction principale
# ====================

def fetch_all_data(start_date, end_date):
    """
    Récupère toutes les données et les fusionne
    
    Returns:
        DataFrame fusionné avec toutes les colonnes
    """
    print("=" * 60)
    print("📊 RÉCUPÉRATION DONNÉES RÉELLES")
    print("=" * 60)
    
    # Météo
    df_meteo = fetch_meteo_data(start_date=start_date, end_date=end_date)
    # Convertir timezone pour compatibilité merge
    df_meteo['timestamp'] = df_meteo['timestamp'].dt.tz_localize('Europe/Paris')
    time.sleep(1)  # Pause courtoise
    
    # Prix RTE
    df_prices = fetch_rte_wholesale_prices(start_date, end_date)
    time.sleep(1)
    
    # Production RTE
    df_production = fetch_rte_production(start_date, end_date)
    time.sleep(1)
    
    # Consommation RTE
    df_consumption = fetch_rte_consumption(start_date, end_date)
    
    print("\n" + "=" * 60)
    print("🔗 FUSION DES DATASETS")
    print("=" * 60)
    
    # Fusion sur timestamp
    df = df_meteo.copy()
    
    if not df_prices.empty:
        df = df.merge(df_prices, on='timestamp', how='left')
        print(f"✅ Prix fusionnés: {df['price_eur_mwh'].notna().sum()} valeurs")
    
    if not df_production.empty:
        df = df.merge(df_production, on='timestamp', how='left')
        print(f"✅ Production fusionnée")
    
    if not df_consumption.empty:
        df = df.merge(df_consumption, on='timestamp', how='left')
        print(f"✅ Consommation fusionnée: {df['demand_gw'].notna().sum()} valeurs")
    
    # Calculer total production si colonnes présentes
    prod_cols = [c for c in df.columns if 'production_gw' in c and c != 'total_production_gw']
    if prod_cols:
        df['total_production_gw'] = df[prod_cols].sum(axis=1)
    
    print(f"\n✅ Dataset final: {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"📊 Période: {df['timestamp'].min()} à {df['timestamp'].max()}")
    
    return df


if __name__ == "__main__":
    # Test
    end = datetime.now().date()
    start = end - timedelta(days=7)  # 1 semaine
    
    df = fetch_all_data(str(start), str(end))
    print("\n" + "=" * 60)
    print(df.head())
    print(df.info())

