"""
Système de recommandations pour le trading d'électricité
Génère des recommandations BUY/HOLD/HEDGE basées sur prédictions et contrats
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class RecommendationEngine:
    """Moteur de recommandations trading"""
    
    def __init__(self, db):
        """
        Initialise le moteur
        
        Args:
            db: Instance PriceDatabase
        """
        self.db = db
    
    def generate_recommendation(self, current_price, predicted_prices, contracts_df, 
                              volatility_threshold=10):
        """
        Génère une recommandation basée sur les données actuelles
        
        Args:
            current_price: Prix spot actuel
            predicted_prices: DataFrame avec prédictions 48h (timestamp, predicted_price)
            contracts_df: DataFrame avec contrats actifs
            volatility_threshold: Seuil de volatilité acceptable
        
        Returns:
            Dict avec recommandation complète
        """
        # Si pas de contrats, pas de recommandation
        if contracts_df.empty:
            return {
                'action': 'HOLD',
                'score': 0,
                'volume_mwh': 0,
                'target_price': None,
                'expected_gain': 0,
                'reasoning': "Aucun contrat actif. Ajoutez des contrats clients pour obtenir des recommandations."
            }
        
        # Calculer prix garanti moyen pondéré
        total_volume = contracts_df['volume_mwh'].sum()
        weighted_guaranteed = (contracts_df['volume_mwh'] * contracts_df['guaranteed_price_eur_mwh']).sum() / total_volume
        
        # Calculer volatilité des prédictions (std sur 48h)
        volatility = predicted_prices['predicted_price'].std() if not predicted_prices.empty else 0
        
        # Trouver meilleur prix prédit dans les 48h
        if not predicted_prices.empty:
            min_predicted = predicted_prices['predicted_price'].min()
            min_predicted_time = predicted_prices.loc[predicted_prices['predicted_price'].idxmin(), 'timestamp']
        else:
            min_predicted = current_price
            min_predicted_time = datetime.now()
        
        # === LOGIQUE DE DÉCISION ===
        
        # Marge de sécurité (2€/MWh)
        safety_margin = 2
        target_buy_price = weighted_guaranteed - safety_margin
        
        # Calculer le gain potentiel
        potential_gain_per_mwh = weighted_guaranteed - min_predicted
        
        # Volume suggéré : 10% du volume total contracté (pas tout d'un coup)
        suggested_volume = total_volume * 0.1
        expected_total_gain = potential_gain_per_mwh * suggested_volume
        
        # === BUY SIGNAL ===
        if min_predicted < target_buy_price and volatility < volatility_threshold:
            score = self._calculate_buy_score(
                current_price, 
                min_predicted, 
                weighted_guaranteed, 
                volatility,
                volatility_threshold
            )
            
            # Temps jusqu'au meilleur prix
            hours_until_best = (min_predicted_time - datetime.now()).total_seconds() / 3600
            hours_until_best = max(0, hours_until_best)
            
            reasoning = (
                f"💰 OPPORTUNITÉ D'ACHAT\n\n"
                f"Prix actuel: {current_price:.1f}€/MWh\n"
                f"Prix prédit optimal: {min_predicted:.1f}€/MWh (dans {hours_until_best:.0f}h)\n"
                f"Prix garanti clients: {weighted_guaranteed:.1f}€/MWh\n"
                f"Marge potentielle: {potential_gain_per_mwh:.1f}€/MWh\n\n"
                f"Volatilité: {'Basse ✓' if volatility < volatility_threshold else 'Élevée ⚠️'}\n"
                f"Gain total attendu: {expected_total_gain:.0f}€"
            )
            
            return {
                'action': 'BUY',
                'score': score,
                'volume_mwh': suggested_volume,
                'target_price': min_predicted,
                'expected_gain': expected_total_gain,
                'reasoning': reasoning,
                'best_time': min_predicted_time
            }
        
        # === HEDGE SIGNAL ===
        elif current_price > weighted_guaranteed or min_predicted > weighted_guaranteed:
            score = 80  # Hedge = important
            
            reasoning = (
                f"⚠️ RISQUE DE PERTE\n\n"
                f"Prix actuel: {current_price:.1f}€/MWh\n"
                f"Prix garanti clients: {weighted_guaranteed:.1f}€/MWh\n"
                f"Risque: {'Prix actuel > garanti' if current_price > weighted_guaranteed else 'Prix va monter'}\n\n"
                f"💡 Recommandation: Couvrir votre exposition avec des contrats futures\n"
                f"ou réduire votre risque en achetant maintenant."
            )
            
            return {
                'action': 'HEDGE',
                'score': score,
                'volume_mwh': suggested_volume,
                'target_price': current_price,
                'expected_gain': 0,  # Hedge = protection, pas de gain
                'reasoning': reasoning,
                'best_time': datetime.now()
            }
        
        # === HOLD SIGNAL ===
        else:
            score = 50
            
            reasoning = (
                f"⏸️ ATTENDRE UN MEILLEUR MOMENT\n\n"
                f"Prix actuel: {current_price:.1f}€/MWh\n"
                f"Prix minimum prédit: {min_predicted:.1f}€/MWh\n"
                f"Prix cible d'achat: {target_buy_price:.1f}€/MWh\n\n"
                f"{'Volatilité élevée: attendre stabilisation' if volatility >= volatility_threshold else 'Prix pas encore optimal'}\n"
                f"Marge actuelle insuffisante: {potential_gain_per_mwh:.1f}€/MWh"
            )
            
            return {
                'action': 'HOLD',
                'score': score,
                'volume_mwh': 0,
                'target_price': target_buy_price,
                'expected_gain': 0,
                'reasoning': reasoning,
                'best_time': min_predicted_time
            }
    
    def _calculate_buy_score(self, current_price, predicted_price, guaranteed_price, 
                           volatility, volatility_threshold):
        """
        Calcule un score de 0 à 100 pour le signal BUY
        
        Args:
            current_price: Prix actuel
            predicted_price: Prix prédit minimum
            guaranteed_price: Prix garanti moyen
            volatility: Volatilité des prédictions
            volatility_threshold: Seuil de volatilité
        
        Returns:
            Score 0-100
        """
        # Score basé sur la marge potentielle
        margin = guaranteed_price - predicted_price
        margin_score = min(100, (margin / guaranteed_price) * 200)  # 10% marge = 20 points
        
        # Score basé sur la volatilité (moins c'est volatile, mieux c'est)
        volatility_score = max(0, 100 - (volatility / volatility_threshold * 100))
        
        # Score basé sur l'écart entre prix actuel et prix prédit
        price_improvement = current_price - predicted_price
        improvement_score = min(50, price_improvement * 5)  # 10€ d'amélioration = 50 points
        
        # Score final (pondéré)
        final_score = (
            margin_score * 0.5 +      # 50% poids sur la marge
            volatility_score * 0.3 +   # 30% poids sur la volatilité
            improvement_score * 0.2    # 20% poids sur l'amélioration
        )
        
        return int(min(100, max(0, final_score)))
    
    def check_and_create_alerts(self, current_price, predicted_prices, contracts_df, 
                               price_threshold=100):
        """
        Vérifie les conditions et crée des alertes si nécessaire
        
        Args:
            current_price: Prix actuel
            predicted_prices: DataFrame prédictions
            contracts_df: DataFrame contrats
            price_threshold: Seuil prix élevé
        
        Returns:
            Liste des alertes créées
        """
        alerts = []
        
        # Alerte prix élevé
        if current_price > price_threshold:
            self.db.create_alert(
                alert_type='price',
                severity='high',
                message=f"⚠️ Prix spot élevé: {current_price:.1f}€/MWh (seuil: {price_threshold}€)"
            )
            alerts.append('price_high')
        
        # Alerte risque de perte
        if not contracts_df.empty:
            weighted_guaranteed = (contracts_df['volume_mwh'] * contracts_df['guaranteed_price_eur_mwh']).sum() / contracts_df['volume_mwh'].sum()
            
            if current_price > weighted_guaranteed:
                self.db.create_alert(
                    alert_type='risk',
                    severity='high',
                    message=f"🔴 RISQUE: Prix spot ({current_price:.1f}€) > Prix garanti ({weighted_guaranteed:.1f}€)"
                )
                alerts.append('loss_risk')
        
        # Alerte opportunité forte
        if not predicted_prices.empty and not contracts_df.empty:
            min_predicted = predicted_prices['predicted_price'].min()
            weighted_guaranteed = (contracts_df['volume_mwh'] * contracts_df['guaranteed_price_eur_mwh']).sum() / contracts_df['volume_mwh'].sum()
            margin = weighted_guaranteed - min_predicted
            
            if margin > 10:  # Marge > 10€/MWh
                self.db.create_alert(
                    alert_type='opportunity',
                    severity='medium',
                    message=f"💰 OPPORTUNITÉ: Prix prédit {min_predicted:.1f}€, marge {margin:.1f}€/MWh possible"
                )
                alerts.append('opportunity')
        
        return alerts


if __name__ == "__main__":
    # Test
    print("🧪 Test moteur de recommandations...")
    
    from src.data.database import PriceDatabase
    
    db = PriceDatabase('data/test_recommendations.db')
    engine = RecommendationEngine(db)
    
    # Test avec données simulées
    contracts = pd.DataFrame({
        'id': [1, 2],
        'client_name': ['Hôpital Nord', 'Université Paris'],
        'volume_mwh': [100, 50],
        'guaranteed_price_eur_mwh': [85, 82],
        'status': ['active', 'active']
    })
    
    predictions = pd.DataFrame({
        'timestamp': pd.date_range(start=datetime.now(), periods=48, freq='h'),
        'predicted_price': [75 + i * 0.5 for i in range(48)]
    })
    
    current_price = 80
    
    # Générer recommandation
    reco = engine.generate_recommendation(
        current_price=current_price,
        predicted_prices=predictions,
        contracts_df=contracts
    )
    
    print(f"\n🎯 RECOMMANDATION:")
    print(f"Action: {reco['action']}")
    print(f"Score: {reco['score']}/100")
    print(f"Volume: {reco['volume_mwh']:.1f} MWh")
    print(f"Prix cible: {reco['target_price']:.1f}€/MWh")
    print(f"Gain attendu: {reco['expected_gain']:.0f}€")
    print(f"\nRaisonnement:\n{reco['reasoning']}")
    
    # Test alertes
    alerts = engine.check_and_create_alerts(current_price, predictions, contracts)
    print(f"\n⚠️ Alertes créées: {len(alerts)}")
    
    db.close()
    print("\n✅ Tests réussis!")

