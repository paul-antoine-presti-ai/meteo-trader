"""
Système de recommandations avancées basé sur ML et analyse du marché
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AdvancedTradingAdvisor:
    """
    Conseiller trading avancé utilisant ML + règles métier
    """
    
    def __init__(self, model, features):
        """
        Args:
            model: Modèle ML entraîné (Random Forest ou XGBoost)
            features: Liste des features utilisées par le modèle
        """
        self.model = model
        self.features = features
    
    def generate_recommendation(self, df_historical, df_future_predictions, contracts=None):
        """
        Génère une recommandation complète basée sur:
        - Prédictions ML
        - Historique des prix
        - Tendances météo
        - Contrats actifs (optionnel)
        
        Returns:
            dict: {
                'action': 'BUY'|'SELL'|'HOLD'|'WAIT',
                'confiance': float (0-1),
                'raison': str,
                'impact_eur_mwh': float,
                'horizon': str ('immediate', 'next_6h', 'next_24h'),
                'details': dict
            }
        """
        
        # Extraire les dernières données historiques
        recent_prices = df_historical['price_eur_mwh'].tail(24).values if 'price_eur_mwh' in df_historical.columns else []
        
        # Prédictions futures
        if isinstance(df_future_predictions, pd.Series):
            future_prices = df_future_predictions.values
        elif isinstance(df_future_predictions, pd.DataFrame) and 'predicted_price' in df_future_predictions.columns:
            future_prices = df_future_predictions['predicted_price'].values
        else:
            # Si c'est juste un array
            future_prices = df_future_predictions if isinstance(df_future_predictions, np.ndarray) else []
        
        # Si pas assez de données
        if len(recent_prices) == 0 or len(future_prices) == 0:
            return {
                'action': 'WAIT',
                'confiance': 0.3,
                'raison': "Données insuffisantes pour une recommandation fiable.",
                'impact_eur_mwh': 0.0,
                'horizon': 'immediate',
                'details': {}
            }
        
        # === ANALYSE ===
        
        # Prix actuel et moyennes
        current_price = recent_prices[-1]
        avg_24h = np.mean(recent_prices)
        std_24h = np.std(recent_prices)
        
        # Prédictions
        avg_next_6h = np.mean(future_prices[:min(6, len(future_prices))])
        avg_next_24h = np.mean(future_prices[:min(24, len(future_prices))])
        min_next_24h = np.min(future_prices[:min(24, len(future_prices))])
        max_next_24h = np.max(future_prices[:min(24, len(future_prices))])
        
        # Tendance
        price_trend_6h = avg_next_6h - current_price
        price_trend_24h = avg_next_24h - current_price
        price_trend_pct_6h = (price_trend_6h / current_price) * 100
        price_trend_pct_24h = (price_trend_24h / current_price) * 100
        
        # Volatilité
        volatility_predicted = np.std(future_prices[:min(24, len(future_prices))])
        volatility_ratio = volatility_predicted / std_24h if std_24h > 0 else 1.0
        
        # Position par rapport à la moyenne
        position_vs_avg = (current_price - avg_24h) / avg_24h if avg_24h > 0 else 0
        
        # === RÈGLES DE DÉCISION ===
        
        action = 'HOLD'
        confiance = 0.5
        raison = ""
        impact = 0.0
        horizon = 'next_6h'
        
        # RÈGLE 1: Prix bas + hausse prévue → BUY
        if current_price < avg_24h - 0.5 * std_24h and price_trend_6h > 2:
            action = 'BUY'
            confiance = min(0.9, 0.6 + abs(price_trend_pct_6h) / 20)
            raison = f"Prix actuel ({current_price:.2f} €/MWh) inférieur à la moyenne 24h (-{abs(position_vs_avg)*100:.1f}%). Hausse de {price_trend_pct_6h:+.1f}% prévue dans les 6h. **Opportunité d'achat**."
            impact = price_trend_6h
            horizon = 'next_6h'
        
        # RÈGLE 2: Prix élevé + baisse prévue → SELL
        elif current_price > avg_24h + 0.5 * std_24h and price_trend_6h < -2:
            action = 'SELL'
            confiance = min(0.9, 0.6 + abs(price_trend_pct_6h) / 20)
            raison = f"Prix actuel ({current_price:.2f} €/MWh) supérieur à la moyenne 24h (+{abs(position_vs_avg)*100:.1f}%). Baisse de {price_trend_pct_6h:.1f}% prévue dans les 6h. **Opportunité de vente/couverture**."
            impact = abs(price_trend_6h)
            horizon = 'next_6h'
        
        # RÈGLE 3: Forte hausse prévue (peu importe le prix actuel) → BUY
        elif price_trend_pct_6h > 8:
            action = 'BUY'
            confiance = min(0.85, 0.55 + price_trend_pct_6h / 30)
            raison = f"Forte hausse prévue: **+{price_trend_pct_6h:.1f}%** dans les 6h ({current_price:.2f} → {avg_next_6h:.2f} €/MWh). Signal haussier puissant."
            impact = price_trend_6h
            horizon = 'immediate'
        
        # RÈGLE 4: Forte baisse prévue → SELL
        elif price_trend_pct_6h < -8:
            action = 'SELL'
            confiance = min(0.85, 0.55 + abs(price_trend_pct_6h) / 30)
            raison = f"Forte baisse prévue: **{price_trend_pct_6h:.1f}%** dans les 6h ({current_price:.2f} → {avg_next_6h:.2f} €/MWh). Signal baissier puissant."
            impact = abs(price_trend_6h)
            horizon = 'immediate'
        
        # RÈGLE 5: Prix stable + volatilité faible → HOLD
        elif abs(price_trend_pct_6h) < 3 and volatility_ratio < 1.2:
            action = 'HOLD'
            confiance = 0.7
            raison = f"Marché stable. Variation prévue: {price_trend_pct_6h:+.1f}% dans les 6h. Volatilité faible. **Maintenir les positions actuelles**."
            impact = 0.0
            horizon = 'next_6h'
        
        # RÈGLE 6: Forte volatilité prévue → WAIT (risque élevé)
        elif volatility_ratio > 1.8:
            action = 'WAIT'
            confiance = 0.65
            raison = f"Volatilité élevée prévue (×{volatility_ratio:.1f}). Écart attendu: {min_next_24h:.2f} - {max_next_24h:.2f} €/MWh. **Attendre clarification du marché**."
            impact = max_next_24h - min_next_24h
            horizon = 'next_24h'
        
        # RÈGLE 7: Opportunité d'arbitrage 24h (achat maintenant, vente plus tard)
        elif max_next_24h - current_price > 10:
            action = 'BUY'
            confiance = min(0.8, 0.5 + (max_next_24h - current_price) / 40)
            raison = f"Arbitrage intraday détecté. Pic à {max_next_24h:.2f} €/MWh prévu dans les 24h (vs {current_price:.2f} actuellement). Gain potentiel: **+{max_next_24h - current_price:.2f} €/MWh**."
            impact = max_next_24h - current_price
            horizon = 'next_24h'
        
        # RÈGLE 8: Tendance haussière modérée → BUY avec prudence
        elif 3 <= price_trend_pct_6h <= 8:
            action = 'BUY'
            confiance = 0.6
            raison = f"Tendance haussière modérée: +{price_trend_pct_6h:.1f}% dans les 6h. Prix stable autour de {current_price:.2f} €/MWh. Opportunité limitée mais favorable."
            impact = price_trend_6h
            horizon = 'next_6h'
        
        # RÈGLE 9: Tendance baissière modérée → SELL avec prudence
        elif -8 <= price_trend_pct_6h <= -3:
            action = 'SELL'
            confiance = 0.6
            raison = f"Tendance baissière modérée: {price_trend_pct_6h:.1f}% dans les 6h. Envisager de couvrir les positions ou réduire l'exposition."
            impact = abs(price_trend_6h)
            horizon = 'next_6h'
        
        # Défaut
        else:
            action = 'HOLD'
            confiance = 0.5
            raison = f"Marché équilibré. Prix actuel: {current_price:.2f} €/MWh. Variation prévue: {price_trend_pct_6h:+.1f}% (6h), {price_trend_pct_24h:+.1f}% (24h). **Maintenir surveillance**."
            impact = 0.0
            horizon = 'next_6h'
        
        # Détails supplémentaires
        details = {
            'current_price': float(current_price),
            'avg_24h': float(avg_24h),
            'avg_next_6h': float(avg_next_6h),
            'avg_next_24h': float(avg_next_24h),
            'min_next_24h': float(min_next_24h),
            'max_next_24h': float(max_next_24h),
            'trend_6h_pct': float(price_trend_pct_6h),
            'trend_24h_pct': float(price_trend_pct_24h),
            'volatility_ratio': float(volatility_ratio),
            'position_vs_avg_pct': float(position_vs_avg * 100)
        }
        
        return {
            'action': action,
            'confiance': confiance,
            'raison': raison,
            'impact_eur_mwh': float(impact),
            'horizon': horizon,
            'details': details
        }
    
    def find_optimal_trading_windows(self, df_predictions, window_hours=6):
        """
        Trouve les meilleurs moments pour acheter/vendre sur les prochaines 48h
        
        Returns:
            dict: {
                'best_buy_times': [(timestamp, price, score), ...],
                'best_sell_times': [(timestamp, price, score), ...],
                'arbitrage_opportunities': [(buy_time, sell_time, gain), ...]
            }
        """
        if df_predictions.empty or len(df_predictions) < window_hours:
            return {
                'best_buy_times': [],
                'best_sell_times': [],
                'arbitrage_opportunities': []
            }
        
        prices = df_predictions['predicted_price'].values if 'predicted_price' in df_predictions.columns else df_predictions.values
        timestamps = df_predictions.index if hasattr(df_predictions, 'index') else list(range(len(prices)))
        
        # Trouver les mins et maxs locaux
        best_buys = []
        best_sells = []
        
        for i in range(1, len(prices) - 1):
            # Minimum local (opportunité d'achat)
            if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                score = (max(prices) - prices[i]) / max(prices) if max(prices) > 0 else 0
                best_buys.append((timestamps[i], prices[i], score))
            
            # Maximum local (opportunité de vente)
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                score = (prices[i] - min(prices)) / prices[i] if prices[i] > 0 else 0
                best_sells.append((timestamps[i], prices[i], score))
        
        # Trier par score
        best_buys.sort(key=lambda x: x[2], reverse=True)
        best_sells.sort(key=lambda x: x[2], reverse=True)
        
        # Opportunités d'arbitrage (acheter bas, vendre haut)
        arbitrage_opps = []
        for buy_time, buy_price, _ in best_buys[:5]:
            for sell_time, sell_price, _ in best_sells[:5]:
                # Vérifier que la vente est après l'achat
                if sell_time > buy_time:
                    gain = sell_price - buy_price
                    if gain > 5:  # Gain minimum de 5 €/MWh
                        arbitrage_opps.append((buy_time, sell_time, gain))
        
        # Trier les arbitrages par gain
        arbitrage_opps.sort(key=lambda x: x[2], reverse=True)
        
        return {
            'best_buy_times': best_buys[:5],
            'best_sell_times': best_sells[:5],
            'arbitrage_opportunities': arbitrage_opps[:5]
        }

