"""
Client API ENTSOE-E Transparency Platform
Récupère données électricité européennes (prix, production, échanges)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()


class EntsoeClient:
    """Client pour ENTSOE-E Transparency Platform"""
    
    # Codes pays ENTSOE-E
    COUNTRY_CODES = {
        'FR': '10YFR-RTE------C',  # France
        'DE': '10Y1001A1001A83F',  # Allemagne
        'ES': '10YES-REE------0',  # Espagne
        'IT': '10YIT-GRTN-----B',  # Italie
        'GB': '10YGB----------A',  # UK (Great Britain)
    }
    
    # Noms complets
    COUNTRY_NAMES = {
        'FR': 'France',
        'DE': 'Allemagne',
        'ES': 'Espagne',
        'IT': 'Italie',
        'GB': 'Royaume-Uni',
    }
    
    # Types de production
    PRODUCTION_TYPES = {
        'B01': 'Biomass',
        'B02': 'Fossil Brown coal/Lignite',
        'B03': 'Fossil Coal-derived gas',
        'B04': 'Fossil Gas',
        'B05': 'Fossil Hard coal',
        'B06': 'Fossil Oil',
        'B09': 'Geothermal',
        'B10': 'Hydro Pumped Storage',
        'B11': 'Hydro Run-of-river and poundage',
        'B12': 'Hydro Water Reservoir',
        'B13': 'Marine',
        'B14': 'Nuclear',
        'B15': 'Other renewable',
        'B16': 'Solar',
        'B17': 'Waste',
        'B18': 'Wind Offshore',
        'B19': 'Wind Onshore',
        'B20': 'Other',
    }
    
    def __init__(self, api_token=None):
        """
        Initialise le client ENTSOE-E
        
        Args:
            api_token: Token API ENTSOE-E (ou depuis env var)
        """
        self.api_token = api_token or os.getenv('ENTSOE_API_TOKEN')
        
        if not self.api_token:
            raise ValueError("ENTSOE_API_TOKEN manquant. Ajoutez-le dans .env")
        
        self.base_url = "https://web-api.tp.entsoe.eu/api"
    
    def _make_request(self, params):
        """
        Requête générique à l'API
        
        Args:
            params: Paramètres de la requête
        
        Returns:
            Réponse XML brute
        """
        params['securityToken'] = self.api_token
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"⚠️ ENTSOE-E Error {response.status_code}: {response.text[:200]}")
                return None
        
        except Exception as e:
            print(f"❌ ENTSOE-E Request Error: {e}")
            return None
    
    def get_day_ahead_prices(self, country_code, start_date, end_date):
        """
        Récupère les prix day-ahead (marché J+1)
        
        Args:
            country_code: Code pays ('FR', 'DE', etc.)
            start_date: Date début (YYYY-MM-DD)
            end_date: Date fin (YYYY-MM-DD)
        
        Returns:
            DataFrame avec timestamp et price_eur_mwh
        """
        area_code = self.COUNTRY_CODES.get(country_code)
        
        if not area_code:
            print(f"❌ Code pays inconnu: {country_code}")
            return pd.DataFrame()
        
        # Convertir dates en format ENTSOE (YYYYMMDDHHmm)
        start_dt = pd.to_datetime(start_date).strftime('%Y%m%d0000')
        end_dt = (pd.to_datetime(end_date) + timedelta(days=1)).strftime('%Y%m%d0000')
        
        params = {
            'documentType': 'A44',  # Price Document
            'in_Domain': area_code,
            'out_Domain': area_code,
            'periodStart': start_dt,
            'periodEnd': end_dt,
        }
        
        xml_data = self._make_request(params)
        
        if not xml_data:
            return pd.DataFrame()
        
        # Parser XML
        try:
            root = ET.fromstring(xml_data)
            
            prices = []
            timestamps = []
            
            # Namespace ENTSOE
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3'}
            
            # Parcourir les TimeSeries
            for ts in root.findall('.//ns:TimeSeries', ns):
                for period in ts.findall('.//ns:Period', ns):
                    # Start time du period
                    start = period.find('ns:timeInterval/ns:start', ns).text
                    start_time = pd.to_datetime(start)
                    
                    # Resolution (ex: PT60M = 60 minutes)
                    resolution = period.find('ns:resolution', ns).text
                    
                    # Extraire durée en minutes
                    if 'PT60M' in resolution or 'PT1H' in resolution:
                        interval_minutes = 60
                    elif 'PT15M' in resolution:
                        interval_minutes = 15
                    elif 'PT30M' in resolution:
                        interval_minutes = 30
                    else:
                        interval_minutes = 60  # Default
                    
                    # Points de prix
                    for point in period.findall('.//ns:Point', ns):
                        position = int(point.find('ns:position', ns).text)
                        price = float(point.find('ns:price.amount', ns).text)
                        
                        # Calculer timestamp
                        timestamp = start_time + timedelta(minutes=interval_minutes * (position - 1))
                        
                        timestamps.append(timestamp)
                        prices.append(price)
            
            if not prices:
                return pd.DataFrame()
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'price_eur_mwh': prices
            })
            
            # Convertir en heure locale Europe/Paris
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
            
            # Trier et dédupliquer
            df = df.sort_values('timestamp').drop_duplicates(subset=['timestamp']).reset_index(drop=True)
            
            return df
        
        except Exception as e:
            print(f"❌ Erreur parsing XML ({country_code}): {e}")
            return pd.DataFrame()
    
    def get_actual_generation(self, country_code, start_date, end_date):
        """
        Récupère la production réelle par type
        
        Args:
            country_code: Code pays
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame avec timestamp et colonnes par type de production
        """
        area_code = self.COUNTRY_CODES.get(country_code)
        
        if not area_code:
            return pd.DataFrame()
        
        start_dt = pd.to_datetime(start_date).strftime('%Y%m%d0000')
        end_dt = (pd.to_datetime(end_date) + timedelta(days=1)).strftime('%Y%m%d0000')
        
        params = {
            'documentType': 'A75',  # Actual generation per type
            'processType': 'A16',   # Realised
            'in_Domain': area_code,
            'periodStart': start_dt,
            'periodEnd': end_dt,
        }
        
        xml_data = self._make_request(params)
        
        if not xml_data:
            return pd.DataFrame()
        
        # Parser XML (simplifié)
        try:
            root = ET.fromstring(xml_data)
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}
            
            all_data = []
            
            for ts in root.findall('.//ns:TimeSeries', ns):
                # Type de production
                psr_type = ts.find('.//ns:MktPSRType/ns:psrType', ns)
                prod_type = psr_type.text if psr_type is not None else 'Unknown'
                
                for period in ts.findall('.//ns:Period', ns):
                    start = period.find('ns:timeInterval/ns:start', ns).text
                    start_time = pd.to_datetime(start)
                    
                    resolution = period.find('ns:resolution', ns).text
                    interval_minutes = 60  # Default
                    
                    if 'PT60M' in resolution or 'PT1H' in resolution:
                        interval_minutes = 60
                    elif 'PT15M' in resolution:
                        interval_minutes = 15
                    
                    for point in period.findall('.//ns:Point', ns):
                        position = int(point.find('ns:position', ns).text)
                        quantity = float(point.find('ns:quantity', ns).text)
                        
                        timestamp = start_time + timedelta(minutes=interval_minutes * (position - 1))
                        
                        all_data.append({
                            'timestamp': timestamp,
                            'production_type': prod_type,
                            'quantity_mw': quantity
                        })
            
            if not all_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(all_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
            
            # Pivoter pour avoir une colonne par type
            df_pivot = df.pivot_table(
                index='timestamp',
                columns='production_type',
                values='quantity_mw',
                aggfunc='sum'
            ).reset_index()
            
            # Convertir MW en GW
            for col in df_pivot.columns:
                if col != 'timestamp':
                    df_pivot[col] = df_pivot[col] / 1000  # MW -> GW
            
            return df_pivot
        
        except Exception as e:
            print(f"❌ Erreur parsing production ({country_code}): {e}")
            return pd.DataFrame()
    
    def get_actual_load(self, country_code, start_date, end_date):
        """
        Récupère la consommation réelle (Load)
        
        Args:
            country_code: Code pays
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame avec timestamp et load_mw
        """
        area_code = self.COUNTRY_CODES.get(country_code)
        
        if not area_code:
            return pd.DataFrame()
        
        start_dt = pd.to_datetime(start_date).strftime('%Y%m%d0000')
        end_dt = (pd.to_datetime(end_date) + timedelta(days=1)).strftime('%Y%m%d0000')
        
        params = {
            'documentType': 'A65',  # Load
            'processType': 'A16',   # Realised
            'outBiddingZone_Domain': area_code,
            'periodStart': start_dt,
            'periodEnd': end_dt,
        }
        
        xml_data = self._make_request(params)
        
        if not xml_data:
            return pd.DataFrame()
        
        try:
            root = ET.fromstring(xml_data)
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}
            
            loads = []
            timestamps = []
            
            for ts in root.findall('.//ns:TimeSeries', ns):
                for period in ts.findall('.//ns:Period', ns):
                    start = period.find('ns:timeInterval/ns:start', ns).text
                    start_time = pd.to_datetime(start)
                    
                    resolution = period.find('ns:resolution', ns).text
                    interval_minutes = 60
                    if 'PT15M' in resolution:
                        interval_minutes = 15
                    
                    for point in period.findall('.//ns:Point', ns):
                        position = int(point.find('ns:position', ns).text)
                        quantity = float(point.find('ns:quantity', ns).text)
                        
                        timestamp = start_time + timedelta(minutes=interval_minutes * (position - 1))
                        
                        timestamps.append(timestamp)
                        loads.append(quantity)
            
            if not loads:
                return pd.DataFrame()
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'load_mw': loads
            })
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
            df = df.sort_values('timestamp').drop_duplicates(subset=['timestamp']).reset_index(drop=True)
            
            # Agréger par heure (moyenne)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.groupby(df['timestamp'].dt.floor('h')).agg({'load_mw': 'mean'}).reset_index()
            
            return df
        
        except Exception as e:
            print(f"❌ Erreur parsing load ({country_code}): {e}")
            return pd.DataFrame()
    
    def get_load_forecast(self, country_code, start_date, end_date):
        """
        Récupère les prévisions de consommation
        
        Args:
            country_code: Code pays
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame avec timestamp et forecast_load_mw
        """
        area_code = self.COUNTRY_CODES.get(country_code)
        
        if not area_code:
            return pd.DataFrame()
        
        start_dt = pd.to_datetime(start_date).strftime('%Y%m%d0000')
        end_dt = (pd.to_datetime(end_date) + timedelta(days=1)).strftime('%Y%m%d0000')
        
        params = {
            'documentType': 'A65',  # Load
            'processType': 'A01',   # Day ahead
            'outBiddingZone_Domain': area_code,
            'periodStart': start_dt,
            'periodEnd': end_dt,
        }
        
        xml_data = self._make_request(params)
        
        if not xml_data:
            return pd.DataFrame()
        
        try:
            root = ET.fromstring(xml_data)
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}
            
            forecasts = []
            timestamps = []
            
            for ts in root.findall('.//ns:TimeSeries', ns):
                for period in ts.findall('.//ns:Period', ns):
                    start = period.find('ns:timeInterval/ns:start', ns).text
                    start_time = pd.to_datetime(start)
                    
                    for point in period.findall('.//ns:Point', ns):
                        position = int(point.find('ns:position', ns).text)
                        quantity = float(point.find('ns:quantity', ns).text)
                        
                        timestamp = start_time + timedelta(hours=position - 1)
                        
                        timestamps.append(timestamp)
                        forecasts.append(quantity)
            
            if not forecasts:
                return pd.DataFrame()
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'forecast_load_mw': forecasts
            })
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
            
            return df.sort_values('timestamp').drop_duplicates(subset=['timestamp']).reset_index(drop=True)
        
        except Exception as e:
            print(f"❌ Erreur parsing load forecast ({country_code}): {e}")
            return pd.DataFrame()
    
    def get_unavailability(self, country_code, start_date, end_date):
        """
        Récupère les indisponibilités (pannes, maintenances)
        
        Args:
            country_code: Code pays
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame avec événements d'indisponibilité
        """
        area_code = self.COUNTRY_CODES.get(country_code)
        
        if not area_code:
            return pd.DataFrame()
        
        start_dt = pd.to_datetime(start_date).strftime('%Y%m%d0000')
        end_dt = (pd.to_datetime(end_date) + timedelta(days=7)).strftime('%Y%m%d0000')
        
        params = {
            'documentType': 'A77',  # Unavailability of generation units
            'biddingZone_Domain': area_code,
            'periodStart': start_dt,
            'periodEnd': end_dt,
        }
        
        xml_data = self._make_request(params)
        
        if not xml_data:
            return pd.DataFrame()
        
        try:
            root = ET.fromstring(xml_data)
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-4:unavailabilitydocument:3:0'}
            
            events = []
            
            for doc in root.findall('.//ns:Unavailability_TimeSeries', ns):
                # Type de business (maintenance prévue, panne, etc.)
                business_type = doc.find('ns:businessType', ns)
                business_type_text = business_type.text if business_type is not None else 'Unknown'
                
                # Unité de production concernée
                unit_name = doc.find('.//ns:registeredResource.name', ns)
                unit_name_text = unit_name.text if unit_name is not None else 'Unknown'
                
                # Type de production
                psr_type = doc.find('.//ns:MktPSRType/ns:psrType', ns)
                psr_type_text = psr_type.text if psr_type is not None else 'Unknown'
                
                # Capacité indisponible
                capacity_elem = doc.find('.//ns:quantity', ns)
                capacity = float(capacity_elem.text) if capacity_elem is not None else 0
                
                # Période
                period_start = doc.find('.//ns:timeInterval/ns:start', ns)
                period_end = doc.find('.//ns:timeInterval/ns:end', ns)
                
                if period_start is not None and period_end is not None:
                    events.append({
                        'start': pd.to_datetime(period_start.text),
                        'end': pd.to_datetime(period_end.text),
                        'unit_name': unit_name_text,
                        'production_type': psr_type_text,
                        'capacity_mw': capacity,
                        'business_type': business_type_text
                    })
            
            if not events:
                return pd.DataFrame()
            
            df = pd.DataFrame(events)
            df['start'] = pd.to_datetime(df['start'], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
            df['end'] = pd.to_datetime(df['end'], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
            
            return df.sort_values('start').reset_index(drop=True)
        
        except Exception as e:
            print(f"❌ Erreur parsing unavailability ({country_code}): {e}")
            return pd.DataFrame()
    
    def get_cross_border_flows(self, from_country, to_country, start_date, end_date):
        """
        Récupère les flux physiques entre 2 pays
        
        Args:
            from_country: Pays origine
            to_country: Pays destination
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame avec flux (MW)
        """
        from_area = self.COUNTRY_CODES.get(from_country)
        to_area = self.COUNTRY_CODES.get(to_country)
        
        if not from_area or not to_area:
            return pd.DataFrame()
        
        start_dt = pd.to_datetime(start_date).strftime('%Y%m%d0000')
        end_dt = (pd.to_datetime(end_date) + timedelta(days=1)).strftime('%Y%m%d0000')
        
        params = {
            'documentType': 'A11',  # Aggregated energy data report
            'in_Domain': to_area,
            'out_Domain': from_area,
            'periodStart': start_dt,
            'periodEnd': end_dt,
        }
        
        xml_data = self._make_request(params)
        
        if not xml_data:
            return pd.DataFrame()
        
        # Parser simplifié
        try:
            root = ET.fromstring(xml_data)
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}
            
            flows = []
            timestamps = []
            
            for ts in root.findall('.//ns:TimeSeries', ns):
                for period in ts.findall('.//ns:Period', ns):
                    start = period.find('ns:timeInterval/ns:start', ns).text
                    start_time = pd.to_datetime(start)
                    
                    for point in period.findall('.//ns:Point', ns):
                        position = int(point.find('ns:position', ns).text)
                        quantity = float(point.find('ns:quantity', ns).text)
                        
                        timestamp = start_time + timedelta(hours=position - 1)
                        
                        timestamps.append(timestamp)
                        flows.append(quantity)
            
            if not flows:
                return pd.DataFrame()
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'flow_mw': flows
            })
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
            
            return df.sort_values('timestamp').drop_duplicates(subset=['timestamp']).reset_index(drop=True)
        
        except Exception as e:
            print(f"❌ Erreur parsing flows: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    # Test du client
    print("🧪 Test ENTSOE-E API...\n")
    
    try:
        client = EntsoeClient()
        print("✅ Client initialisé\n")
        
        # Test prix France
        print("📊 Test prix France (derniers 7 jours)...")
        start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end = datetime.now().strftime('%Y-%m-%d')
        
        prices_fr = client.get_day_ahead_prices('FR', start, end)
        
        if not prices_fr.empty:
            print(f"✅ {len(prices_fr)} prix récupérés")
            print(f"   Prix moyen: {prices_fr['price_eur_mwh'].mean():.2f}€/MWh")
            print(f"   Min: {prices_fr['price_eur_mwh'].min():.2f}€")
            print(f"   Max: {prices_fr['price_eur_mwh'].max():.2f}€")
            print(f"\n   Derniers prix:")
            print(prices_fr.tail(5))
        else:
            print("❌ Aucun prix récupéré")
        
        # Test prix Allemagne
        print("\n📊 Test prix Allemagne...")
        prices_de = client.get_day_ahead_prices('DE', start, end)
        
        if not prices_de.empty:
            print(f"✅ {len(prices_de)} prix récupérés")
            print(f"   Prix moyen: {prices_de['price_eur_mwh'].mean():.2f}€/MWh")
        else:
            print("❌ Aucun prix récupéré")
        
        print("\n✅ Tests terminés!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

