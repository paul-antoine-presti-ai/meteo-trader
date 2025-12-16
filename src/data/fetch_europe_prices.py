"""
Récupération des prix européens de l'électricité
Source: ENTSO-E Transparency Platform (via EPEX Spot)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_european_prices(date=None):
    """
    Récupère prix électricité des pays européens
    
    Args:
        date: Date pour laquelle récupérer les prix (datetime ou None pour aujourd'hui)
    
    Returns:
        DataFrame avec colonnes: country_code, country_name, price_eur_mwh, latitude, longitude
    """
    if date is None:
        date = datetime.now()
    
    # Pour le MVP, génération réaliste basée sur patterns réels
    # TODO: Intégrer API ENTSO-E Transparency Platform
    
    # Prix de base France (référence)
    base_price_fr = np.random.normal(75, 15)  # Prix France ~75 €/MWh
    
    # Pays européens avec coordonnées et patterns prix
    countries_data = {
        'FR': {
            'name': 'France',
            'lat': 46.2276,
            'lon': 2.2137,
            'price_factor': 1.0,  # Référence
            'volatility': 0.1
        },
        'DE': {
            'name': 'Allemagne',
            'lat': 51.1657,
            'lon': 10.4515,
            'price_factor': 0.95,  # Souvent moins cher (renouvelables)
            'volatility': 0.15
        },
        'ES': {
            'name': 'Espagne',
            'lat': 40.4637,
            'lon': -3.7492,
            'price_factor': 1.1,  # Plus cher (moins interconnecté)
            'volatility': 0.2
        },
        'IT': {
            'name': 'Italie',
            'lat': 41.8719,
            'lon': 12.5674,
            'price_factor': 1.2,  # Plus cher (dépendance gaz)
            'volatility': 0.18
        },
        'BE': {
            'name': 'Belgique',
            'lat': 50.5039,
            'lon': 4.4699,
            'price_factor': 1.05,  # Proche France
            'volatility': 0.12
        },
        'NL': {
            'name': 'Pays-Bas',
            'lat': 52.1326,
            'lon': 5.2913,
            'price_factor': 0.92,  # Éolien offshore
            'volatility': 0.14
        },
        'GB': {
            'name': 'Royaume-Uni',
            'lat': 55.3781,
            'lon': -3.4360,
            'price_factor': 1.15,  # Brexit, moins interconnecté
            'volatility': 0.16
        },
        'CH': {
            'name': 'Suisse',
            'lat': 46.8182,
            'lon': 8.2275,
            'price_factor': 0.85,  # Hydraulique
            'volatility': 0.08
        },
        'AT': {
            'name': 'Autriche',
            'lat': 47.5162,
            'lon': 14.5501,
            'price_factor': 0.98,  # Proche Allemagne
            'volatility': 0.11
        },
        'PL': {
            'name': 'Pologne',
            'lat': 51.9194,
            'lon': 19.1451,
            'price_factor': 1.3,  # Charbon, moins interconnecté
            'volatility': 0.22
        },
        'CZ': {
            'name': 'République Tchèque',
            'lat': 49.8175,
            'lon': 15.4730,
            'price_factor': 1.05,
            'volatility': 0.13
        },
        'DK': {
            'name': 'Danemark',
            'lat': 56.2639,
            'lon': 9.5018,
            'price_factor': 0.88,  # Leader éolien
            'volatility': 0.17
        },
        'SE': {
            'name': 'Suède',
            'lat': 60.1282,
            'lon': 18.6435,
            'price_factor': 0.65,  # Hydraulique + nucléaire
            'volatility': 0.12
        },
        'NO': {
            'name': 'Norvège',
            'lat': 60.4720,
            'lon': 8.4689,
            'price_factor': 0.55,  # Hydraulique abondant
            'volatility': 0.10
        },
        'PT': {
            'name': 'Portugal',
            'lat': 39.3999,
            'lon': -8.2245,
            'price_factor': 1.12,
            'volatility': 0.19
        }
    }
    
    # Générer prix pour chaque pays
    data = []
    for code, info in countries_data.items():
        price = base_price_fr * info['price_factor']
        price += np.random.normal(0, price * info['volatility'])  # Volatilité
        price = max(0, price)  # Pas de prix négatif
        
        data.append({
            'country_code': code,
            'country_name': info['name'],
            'price_eur_mwh': round(price, 2),
            'latitude': info['lat'],
            'longitude': info['lon'],
            'diff_vs_france': round(price - base_price_fr, 2)
        })
    
    df = pd.DataFrame(data)
    
    # Trier par prix
    df = df.sort_values('price_eur_mwh')
    
    return df


def get_price_color(price, min_price, max_price):
    """
    Retourne couleur pour un prix (gradient vert → orange → rouge)
    
    Args:
        price: Prix actuel
        min_price: Prix minimum (vert)
        max_price: Prix maximum (rouge)
    
    Returns:
        Code couleur hex
    """
    if max_price == min_price:
        return '#FFA500'  # Orange par défaut
    
    # Normaliser entre 0 et 1
    normalized = (price - min_price) / (max_price - min_price)
    
    if normalized < 0.33:
        # Vert (bon marché)
        return '#10b981'
    elif normalized < 0.66:
        # Orange (moyen)
        return '#f59e0b'
    else:
        # Rouge (cher)
        return '#ef4444'


if __name__ == "__main__":
    # Test
    print("🧪 Test prix européens")
    print("=" * 60)
    
    df = get_european_prices()
    print(f"\n✅ {len(df)} pays récupérés")
    print(f"\nPrix min: {df['price_eur_mwh'].min():.2f} €/MWh ({df.iloc[0]['country_name']})")
    print(f"Prix max: {df['price_eur_mwh'].max():.2f} €/MWh ({df.iloc[-1]['country_name']})")
    print(f"\nFrance: {df[df['country_code']=='FR']['price_eur_mwh'].values[0]:.2f} €/MWh")
    
    print("\n📊 Top 5 moins chers:")
    print(df[['country_name', 'price_eur_mwh', 'diff_vs_france']].head())
    
    print("\n📊 Top 5 plus chers:")
    print(df[['country_name', 'price_eur_mwh', 'diff_vs_france']].tail())
    
    print("\n✅ Test réussi!")

