"""
Test rapide de la nouvelle application trading
Vérifie que tous les composants fonctionnent
"""

import sys
sys.path.append('.')

print("🧪 Test MétéoTrader Pro - Version Trading\n")
print("="*60)

# Test 1: Import database
print("\n1️⃣ Test Database...")
try:
    from src.data.database import PriceDatabase
    db = PriceDatabase('data/test_trading_app.db')
    print("   ✅ Database OK")
    
    # Test ajout contrat
    contract_id = db.add_contract(
        client_name="Test Client",
        volume_mwh=100,
        guaranteed_price=85,
        start_date="2025-01-01",
        end_date="2025-12-31"
    )
    print(f"   ✅ Contrat créé (ID: {contract_id})")
    
    # Test récupération contrats
    contracts = db.get_active_contracts()
    print(f"   ✅ Contrats actifs: {len(contracts)}")
    
except Exception as e:
    print(f"   ❌ ERREUR: {e}")
    sys.exit(1)

# Test 2: Import recommendations
print("\n2️⃣ Test Recommandations...")
try:
    from src.trading.recommendations import RecommendationEngine
    import pandas as pd
    from datetime import datetime
    
    engine = RecommendationEngine(db)
    
    # Données de test
    predictions = pd.DataFrame({
        'timestamp': pd.date_range(start=datetime.now(), periods=48, freq='h'),
        'predicted_price': [75 + i * 0.5 for i in range(48)]
    })
    
    contracts_df = db.get_active_contracts()
    
    reco = engine.generate_recommendation(
        current_price=80,
        predicted_prices=predictions,
        contracts_df=contracts_df
    )
    
    print(f"   ✅ Recommandation générée: {reco['action']}")
    print(f"   ✅ Score: {reco['score']}/100")
    print(f"   ✅ Volume: {reco['volume_mwh']:.1f} MWh")
    print(f"   ✅ Gain attendu: {reco['expected_gain']:.0f}€")
    
except Exception as e:
    print(f"   ❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Import alertes
print("\n3️⃣ Test Alertes...")
try:
    alerts = engine.check_and_create_alerts(
        current_price=80,
        predicted_prices=predictions,
        contracts_df=contracts_df
    )
    
    print(f"   ✅ Alertes créées: {len(alerts)}")
    
    active_alerts = db.get_active_alerts()
    print(f"   ✅ Alertes actives: {len(active_alerts)}")
    
except Exception as e:
    print(f"   ❌ ERREUR: {e}")
    sys.exit(1)

# Test 4: Import app components
print("\n4️⃣ Test Composants App...")
try:
    import streamlit
    import plotly
    print("   ✅ Streamlit OK")
    print("   ✅ Plotly OK")
    
except Exception as e:
    print(f"   ❌ ERREUR: {e}")
    sys.exit(1)

# Cleanup
db.close()

print("\n" + "="*60)
print("✅ TOUS LES TESTS RÉUSSIS!")
print("\n🚀 Lancement possible:")
print("   ./run_trading.sh")
print("   ou")
print("   streamlit run app_trading.py")
print("="*60)

