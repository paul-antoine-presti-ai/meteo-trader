"""
Connecteurs APIs pour données réelles avec OAuth2
- RTE (OAuth2 authentifié): Prix, Production, Consommation
- Open-Meteo: Météo
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Charger les credentials
load_dotenv()

# ====================
# RTE APIs (OAuth2)
# ====================

RTE_BASE_URL = "https://digital.iservices.rte-france.com"

# Credentials (Base64 encodé: client_id:client_secret)
RTE_CREDENTIALS = {
    'wholesale': os.getenv('RTE_WHOLESALE_CREDENTIALS'),
    'generation': os.getenv('RTE_GENERATION_CREDENTIALS'),
    'consumption': os.getenv('RTE_CONSUMPTION_CREDENTIALS'),
    'forecast': os.getenv('RTE_FORECAST_CREDENTIALS'),
}

def get_oauth_token(credential_base64):
    """
    Obtient un token OAuth2 avec les credentials Base64
    
    Args:
        credential_base64: Credentials en base64 (client_id:client_secret)
    
    Returns:
        Token d'accès ou None si erreur
    """
    url = "https://digital.iservices.rte-france.com/token/oauth/"
    
    headers = {
        'Authorization': f'Basic {credential_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"⚠️ Erreur OAuth: {response.status_code}")
            print(f"Message: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Erreur OAuth: {e}")
        return None


def fetch_rte_wholesale_prices(start_date, end_date):
    """
    Récupère les prix EPEX Spot via API RTE avec OAuth2
    
    Args:
        start_date: Date début (YYYY-MM-DD)
        end_date: Date fin (YYYY-MM-DD)
    
    Returns:
        DataFrame avec colonnes: timestamp, price_eur_mwh
    """
    print(f"🔄 Récupération prix RTE ({start_date} à {end_date})...")
    
    # Obtenir token
    token = get_oauth_token(RTE_CREDENTIALS['wholesale'])
    if not token:
        print("❌ Impossible d'obtenir le token OAuth")
        return pd.DataFrame()
    
    url = f"{RTE_BASE_URL}/open_api/wholesale_market/v3/france_power_exchanges"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'start_date': f'{start_date}T00:00:00+00:00',
        'end_date': f'{end_date}T23:59:59+00:00'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parser la réponse RTE (structure imbriquée avec 'values')
            records = []
            if 'france_power_exchanges' in data:
                for item in data['france_power_exchanges']:
                    # Chaque item contient un array 'values' avec données 15min
                    if 'values' in item:
                        for value_item in item['values']:
                            records.append({
                                'timestamp': pd.to_datetime(value_item['start_date']),
                                'price_eur_mwh': float(value_item.get('price', 0))
                            })
            
            df = pd.DataFrame(records)
            
            # Agréger par heure (moyenne des 4 tranches de 15min)
            if not df.empty:
                df['timestamp'] = df['timestamp'].dt.floor('H')  # Arrondir à l'heure
                df = df.groupby('timestamp').agg({'price_eur_mwh': 'mean'}).reset_index()
            
            print(f"✅ {len(df)} prix horaires récupérés")
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
    Récupère la production par filière via API RTE avec OAuth2
    
    Returns:
        DataFrame avec: timestamp, nuclear_gw, wind_gw, solar_gw, etc.
    """
    print(f"🔄 Récupération production RTE...")
    
    # Obtenir token
    token = get_oauth_token(RTE_CREDENTIALS['generation'])
    if not token:
        print("❌ Impossible d'obtenir le token OAuth")
        return pd.DataFrame()
    
    url = f"{RTE_BASE_URL}/open_api/actual_generation/v1/actual_generations_per_production_type"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'start_date': f'{start_date}T00:00:00+00:00',
        'end_date': f'{end_date}T23:59:59+00:00'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parser par type de production (structure imbriquée)
            df_list = []
            if 'actual_generations_per_production_type' in data:
                for item in data['actual_generations_per_production_type']:
                    prod_type = item.get('production_type', 'unknown')
                    
                    # Chaque item contient un array 'values'
                    if 'values' in item:
                        for value_item in item['values']:
                            timestamp = pd.to_datetime(value_item['start_date'])
                            value_mw = float(value_item.get('value', 0))
                            value_gw = value_mw / 1000  # MW → GW
                            
                            df_list.append({
                                'timestamp': timestamp,
                                'production_type': prod_type,
                                'production_gw': value_gw
                            })
            
            df = pd.DataFrame(df_list)
            
            # Pivot pour avoir une colonne par type
            if not df.empty:
                # Arrondir à l'heure et agréger
                df['timestamp'] = df['timestamp'].dt.floor('H')
                
                df_pivot = df.pivot_table(
                    index='timestamp',
                    columns='production_type',
                    values='production_gw',
                    aggfunc='mean'  # Moyenne des 4 tranches de 15min
                ).reset_index()
                
                # Renommer TOUTES les colonnes de production
                rename_map = {
                    'NUCLEAR': 'nuclear_production_gw',
                    'WIND': 'wind_production_gw',
                    'SOLAR': 'solar_production_gw',
                    'HYDRO': 'hydro_production_gw',
                    'GAS': 'gas_production_gw',
                    'COAL': 'coal_production_gw',
                    'BIOMASS': 'biomass_production_gw',
                    'FOSSIL_GAS': 'gas_production_gw',
                    'FOSSIL_HARD_COAL': 'coal_production_gw',
                    'FOSSIL_OIL': 'oil_production_gw',
                    'HYDRO_PUMPED_STORAGE': 'hydro_pumped_production_gw',
                    'HYDRO_RUN_OF_RIVER_AND_POUNDAGE': 'hydro_river_production_gw',
                    'HYDRO_WATER_RESERVOIR': 'hydro_reservoir_production_gw',
                    'WASTE': 'waste_production_gw',
                    'WIND_OFFSHORE': 'wind_offshore_production_gw',
                    'WIND_ONSHORE': 'wind_onshore_production_gw',
                    'TOTAL': 'total_rte_production_gw',
                }
                df_pivot = df_pivot.rename(columns=rename_map)
                
                print(f"✅ {len(df_pivot)} points de production récupérés")
                return df_pivot
            else:
                return pd.DataFrame()
        else:
            print(f"⚠️ Erreur API Production: {response.status_code}")
            print(f"Message: {response.text[:200]}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return pd.DataFrame()


def fetch_rte_consumption(start_date, end_date):
    """
    Récupère la consommation via API RTE avec OAuth2
    
    Returns:
        DataFrame avec: timestamp, demand_gw
    """
    print(f"🔄 Récupération consommation RTE...")
    
    # Obtenir token
    token = get_oauth_token(RTE_CREDENTIALS['consumption'])
    if not token:
        print("❌ Impossible d'obtenir le token OAuth")
        return pd.DataFrame()
    
    url = f"{RTE_BASE_URL}/open_api/consumption/v1/short_term"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'start_date': f'{start_date}T00:00:00+00:00',
        'end_date': f'{end_date}T23:59:59+00:00'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            records = []
            if 'short_term' in data:
                for item in data['short_term']:
                    # Structure imbriquée avec 'values'
                    if 'values' in item:
                        for value_item in item['values']:
                            records.append({
                                'timestamp': pd.to_datetime(value_item['start_date']),
                                'demand_mw': float(value_item.get('value', 0))
                            })
            
            df = pd.DataFrame(records)
            if not df.empty:
                df['demand_gw'] = df['demand_mw'] / 1000  # MW → GW
                df = df[['timestamp', 'demand_gw']]
                
                # Agréger par heure
                df['timestamp'] = df['timestamp'].dt.floor('H')
                df = df.groupby('timestamp').agg({'demand_gw': 'mean'}).reset_index()
            
            print(f"✅ {len(df)} points horaires de consommation récupérés")
            return df
        else:
            print(f"⚠️ Erreur API Consommation: {response.status_code}")
            print(f"Message: {response.text[:200]}")
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
    print("📊 RÉCUPÉRATION DONNÉES RÉELLES (OAuth2)")
    print("=" * 60)
    
    # Météo
    df_meteo = fetch_meteo_data(start_date=start_date, end_date=end_date)
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
    
    # Normaliser les timezones pour le merge
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    
    if not df_prices.empty:
        df_prices['timestamp'] = pd.to_datetime(df_prices['timestamp']).dt.tz_localize(None)
        df = df.merge(df_prices, on='timestamp', how='left')
        print(f"✅ Prix fusionnés: {df['price_eur_mwh'].notna().sum()} valeurs")
    
    if not df_production.empty:
        df_production['timestamp'] = pd.to_datetime(df_production['timestamp']).dt.tz_localize(None)
        df = df.merge(df_production, on='timestamp', how='left')
        print(f"✅ Production fusionnée")
    
    if not df_consumption.empty:
        df_consumption['timestamp'] = pd.to_datetime(df_consumption['timestamp']).dt.tz_localize(None)
        df = df.merge(df_consumption, on='timestamp', how='left')
        print(f"✅ Consommation fusionnée: {df['demand_gw'].notna().sum()} valeurs")
    
    # Calculer total production si colonnes présentes
    prod_cols = [c for c in df.columns if 'production_gw' in c and c != 'total_production_gw']
    if prod_cols:
        df['total_production_gw'] = df[prod_cols].sum(axis=1)
    
    # GÉNÉRER LES PRIX si pas présents ou incomplets
    if 'price_eur_mwh' not in df.columns or df['price_eur_mwh'].notna().sum() < len(df) * 0.5:
        print("\n💰 Génération prix réalistes (basés sur offre/demande)...")
        try:
            from src.features.generate_prices import generate_realistic_prices
        except ImportError:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent.parent))
            from src.features.generate_prices import generate_realistic_prices
        
        df['price_eur_mwh'] = generate_realistic_prices(df)
        print(f"✅ {df['price_eur_mwh'].notna().sum()} prix générés")
        print(f"   Moyenne: {df['price_eur_mwh'].mean():.2f} €/MWh")
        print(f"   Min/Max: {df['price_eur_mwh'].min():.2f} / {df['price_eur_mwh'].max():.2f} €/MWh")
    
    print(f"\n✅ Dataset final: {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"📊 Période: {df['timestamp'].min()} à {df['timestamp'].max()}")
    
    return df


if __name__ == "__main__":
    # Test
    end = datetime.now().date() - timedelta(days=1)  # Hier
    start = end - timedelta(days=7)  # 1 semaine
    
    df = fetch_all_data(str(start), str(end))
    print("\n" + "=" * 60)
    print(df.head())
    print("\n" + "=" * 60)
    print(df.info())

