"""Test des nouvelles APIs ENTSOE-E"""

import sys
sys.path.append('.')

from src.data.entsoe_api import EntsoeClient
from datetime import datetime, timedelta

print("🧪 Test nouvelles APIs ENTSOE-E\n")

client = EntsoeClient()

start = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
end = datetime.now().strftime('%Y-%m-%d')

# Test 1: Consommation France
print("1️⃣ Test Consommation (Load) France...")
load_fr = client.get_actual_load('FR', start, end)

if not load_fr.empty:
    print(f"   ✅ {len(load_fr)} heures récupérées")
    print(f"   Conso moyenne: {load_fr['load_mw'].mean():.0f} MW ({load_fr['load_mw'].mean()/1000:.1f} GW)")
    print(f"   Min: {load_fr['load_mw'].min():.0f} MW")
    print(f"   Max: {load_fr['load_mw'].max():.0f} MW")
else:
    print("   ❌ Aucune donnée")

# Test 2: Prévisions consommation
print("\n2️⃣ Test Prévisions Consommation France...")
forecast_fr = client.get_load_forecast('FR', start, end)

if not forecast_fr.empty:
    print(f"   ✅ {len(forecast_fr)} heures prévues")
    print(f"   Conso prévue moyenne: {forecast_fr['forecast_load_mw'].mean():.0f} MW")
else:
    print("   ❌ Aucune donnée")

# Test 3: Unavailability
print("\n3️⃣ Test Unavailability (Pannes) France...")
unavail_fr = client.get_unavailability('FR', start, end)

if not unavail_fr.empty:
    print(f"   ✅ {len(unavail_fr)} événements trouvés")
    print("\n   Principaux événements:")
    for idx, row in unavail_fr.head(5).iterrows():
        print(f"   - {row['unit_name'][:30]:30} | {row['production_type']:10} | {row['capacity_mw']:.0f} MW | {row['business_type']}")
else:
    print("   ⚠️ Aucun événement (normal si pas de panne)")

# Test 4: Production Allemagne
print("\n4️⃣ Test Production Allemagne...")
prod_de = client.get_actual_generation('DE', start, end)

if not prod_de.empty:
    print(f"   ✅ {len(prod_de)} heures récupérées")
    print(f"   Colonnes: {list(prod_de.columns)[:5]}...")
else:
    print("   ❌ Aucune donnée")

print("\n✅ Tests terminés!")

