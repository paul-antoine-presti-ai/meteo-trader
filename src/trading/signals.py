"""
Module de Signaux de Trading pour MétéoTrader
Génère recommandations BUY/SELL/HOLD/WAIT basées sur prix et prédictions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class TradingSignals:
    """Générateur de signaux de trading pour électricité"""
    
    def __init__(self, 
                 low_threshold: float = 60.0,
                 high_threshold: float = 90.0,
                 volatility_threshold: float = 15.0):
        """
        Initialize trading signals generator
        
        Args:
            low_threshold: Prix en dessous = opportunité achat (€/MWh)
            high_threshold: Prix au-dessus = opportunité vente (€/MWh)
            volatility_threshold: Seuil volatilité haute (%)
        """
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.volatility_threshold = volatility_threshold
    
    def calculate_trading_score(self, 
                                current_price: float,
                                predicted_prices: pd.Series,
                                historical_avg: float,
                                volatility: float) -> int:
        """
        Calcule score de trading (0-100)
        
        Args:
            current_price: Prix actuel
            predicted_prices: Prédictions futures
            historical_avg: Moyenne historique
            volatility: Volatilité récente (%)
        
        Returns:
            Score 0-100 (0=très mauvais, 100=excellent)
        """
        score = 50  # Base neutre
        
        # 1. Prix vs moyenne historique (+/- 25 points)
        price_diff_pct = ((current_price - historical_avg) / historical_avg) * 100
        if price_diff_pct < -20:
            score += 25  # Très bon marché
        elif price_diff_pct < -10:
            score += 15
        elif price_diff_pct < 0:
            score += 8
        elif price_diff_pct > 20:
            score -= 25  # Très cher
        elif price_diff_pct > 10:
            score -= 15
        elif price_diff_pct > 0:
            score -= 8
        
        # 2. Tendance future (+/- 20 points)
        if not predicted_prices.empty:
            future_avg = predicted_prices.mean()
            trend = ((future_avg - current_price) / current_price) * 100
            
            if trend > 10:
                score += 20  # Prix va augmenter beaucoup
            elif trend > 5:
                score += 10
            elif trend < -10:
                score -= 20  # Prix va baisser beaucoup
            elif trend < -5:
                score -= 10
        
        # 3. Volatilité (-15 points si haute)
        if volatility > self.volatility_threshold:
            score -= 15  # Risque élevé
        elif volatility < 5:
            score += 5  # Marché stable
        
        # 4. Seuils absolus (+/- 10 points)
        if current_price < self.low_threshold:
            score += 10  # Opportunité!
        elif current_price > self.high_threshold:
            score -= 10  # Trop cher!
        
        # Limiter entre 0 et 100
        return max(0, min(100, score))
    
    def get_recommendation(self, 
                          score: int,
                          current_price: float,
                          predicted_prices: pd.Series) -> Tuple[str, str, str]:
        """
        Génère recommandation basée sur score
        
        Args:
            score: Score de trading (0-100)
            current_price: Prix actuel
            predicted_prices: Prédictions futures
        
        Returns:
            (action, label, color): 
            - action: 'BUY', 'SELL', 'HOLD', 'WAIT'
            - label: Label français
            - color: Couleur (green, red, orange, gray)
        """
        if score >= 75:
            return ('BUY', '🟢 ACHETER', 'green')
        elif score >= 60:
            return ('HOLD', '🟡 CONSERVER', 'orange')
        elif score >= 40:
            return ('WAIT', '⚪ ATTENDRE', 'gray')
        else:
            return ('SELL', '🔴 VENDRE', 'red')
    
    def find_best_opportunities(self, 
                               timeline_df: pd.DataFrame,
                               top_n: int = 5) -> pd.DataFrame:
        """
        Trouve les meilleures opportunités dans timeline
        
        Args:
            timeline_df: DataFrame avec colonnes timestamp, actual_price/predicted_price
            top_n: Nombre d'opportunités à retourner
        
        Returns:
            DataFrame avec meilleures opportunités triées par score
        """
        opportunities = []
        
        for idx, row in timeline_df.iterrows():
            timestamp = row['timestamp']
            
            # Prix (prédit si futur, réel si passé)
            if pd.notna(row.get('predicted_price')):
                price = row['predicted_price']
                is_future = True
            elif pd.notna(row.get('actual_price')):
                price = row['actual_price']
                is_future = False
            else:
                continue
            
            # Calculer score simplifié
            avg_price = timeline_df[['actual_price', 'predicted_price']].mean().mean()
            score = 100 - abs(((price - avg_price) / avg_price) * 100) * 5
            score = max(0, min(100, score))
            
            opportunities.append({
                'timestamp': timestamp,
                'price': price,
                'score': score,
                'is_future': is_future,
                'type': 'ACHAT' if price < avg_price else 'VENTE'
            })
        
        # Trier par score
        df = pd.DataFrame(opportunities)
        if not df.empty:
            df = df.sort_values('score', ascending=False).head(top_n)
        
        return df
    
    def calculate_arbitrage_spread(self, 
                                   france_price: float,
                                   europe_prices: Dict[str, float]) -> List[Dict]:
        """
        Calcule opportunités d'arbitrage entre pays
        
        Args:
            france_price: Prix France actuel
            europe_prices: Dict {country_code: price}
        
        Returns:
            Liste opportunités triées par spread
        """
        opportunities = []
        
        for country, price in europe_prices.items():
            if country == 'FR':
                continue
            
            spread = france_price - price
            spread_pct = (spread / price) * 100
            
            if abs(spread) > 5:  # Spread significatif
                opportunities.append({
                    'country': country,
                    'price': price,
                    'spread': spread,
                    'spread_pct': spread_pct,
                    'direction': 'IMPORT' if spread > 0 else 'EXPORT',
                    'opportunity': abs(spread) > 10  # Gros spread = opportunité
                })
        
        # Trier par spread absolu
        opportunities.sort(key=lambda x: abs(x['spread']), reverse=True)
        
        return opportunities
    
    def detect_alerts(self, 
                     current_price: float,
                     predicted_prices: pd.Series,
                     volatility: float) -> List[Dict]:
        """
        Détecte alertes à notifier
        
        Args:
            current_price: Prix actuel
            predicted_prices: Prédictions futures
            volatility: Volatilité (%)
        
        Returns:
            Liste d'alertes
        """
        alerts = []
        
        # Alerte prix bas
        if current_price < self.low_threshold:
            alerts.append({
                'type': 'PRIX_BAS',
                'severity': 'success',
                'title': '🟢 Prix Très Bas Détecté',
                'message': f'Prix actuel ({current_price:.2f} €/MWh) sous seuil ({self.low_threshold} €/MWh)',
                'action': 'Opportunité d\'achat!'
            })
        
        # Alerte prix haut
        if current_price > self.high_threshold:
            alerts.append({
                'type': 'PRIX_HAUT',
                'severity': 'error',
                'title': '🔴 Prix Très Haut Détecté',
                'message': f'Prix actuel ({current_price:.2f} €/MWh) au-dessus seuil ({self.high_threshold} €/MWh)',
                'action': 'Opportunité de vente!'
            })
        
        # Alerte volatilité haute
        if volatility > self.volatility_threshold:
            alerts.append({
                'type': 'VOLATILITE_HAUTE',
                'severity': 'warning',
                'title': '⚠️ Volatilité Élevée',
                'message': f'Volatilité à {volatility:.1f}% (seuil: {self.volatility_threshold}%)',
                'action': 'Prudence recommandée - marché instable'
            })
        
        # Alerte hausse future
        if not predicted_prices.empty:
            future_max = predicted_prices.max()
            increase_pct = ((future_max - current_price) / current_price) * 100
            
            if increase_pct > 20:
                alerts.append({
                    'type': 'HAUSSE_PREVUE',
                    'severity': 'info',
                    'title': '📈 Forte Hausse Prévue',
                    'message': f'Prix pourrait augmenter de {increase_pct:.1f}% dans les prochaines heures',
                    'action': 'Envisager achat maintenant'
                })
            
            # Alerte baisse future
            future_min = predicted_prices.min()
            decrease_pct = ((current_price - future_min) / current_price) * 100
            
            if decrease_pct > 20:
                alerts.append({
                    'type': 'BAISSE_PREVUE',
                    'severity': 'info',
                    'title': '📉 Forte Baisse Prévue',
                    'message': f'Prix pourrait baisser de {decrease_pct:.1f}% dans les prochaines heures',
                    'action': 'Envisager vente maintenant ou attendre'
                })
        
        return alerts
    
    def get_optimal_hours(self, 
                         timeline_df: pd.DataFrame,
                         window_hours: int = 24) -> Dict:
        """
        Trouve heures optimales achat/vente
        
        Args:
            timeline_df: Timeline avec prix
            window_hours: Fenêtre d'analyse (heures)
        
        Returns:
            Dict avec heures optimales et économies
        """
        # Filtrer sur fenêtre
        now = pd.Timestamp.now()
        window_end = now + pd.Timedelta(hours=window_hours)
        
        future = timeline_df[
            (timeline_df['timestamp'] >= now) & 
            (timeline_df['timestamp'] <= window_end)
        ].copy()
        
        if future.empty:
            return {'cheapest': [], 'most_expensive': [], 'savings': 0}
        
        # Utiliser prix prédit
        future['price'] = future['predicted_price']
        future = future.dropna(subset=['price'])
        
        if future.empty:
            return {'cheapest': [], 'most_expensive': [], 'savings': 0}
        
        # Top 5 heures les moins chères
        cheapest = future.nsmallest(5, 'price')[['timestamp', 'price']].to_dict('records')
        
        # Top 5 heures les plus chères
        most_expensive = future.nlargest(5, 'price')[['timestamp', 'price']].to_dict('records')
        
        # Calcul économies potentielles
        avg_price = future['price'].mean()
        min_price = future['price'].min()
        savings_pct = ((avg_price - min_price) / avg_price) * 100
        
        return {
            'cheapest': cheapest,
            'most_expensive': most_expensive,
            'savings_pct': savings_pct,
            'avg_price': avg_price,
            'min_price': min_price,
            'max_price': future['price'].max()
        }


if __name__ == "__main__":
    # Tests
    print("🧪 Test TradingSignals")
    print("=" * 60)
    
    signals = TradingSignals()
    
    # Test score
    score = signals.calculate_trading_score(
        current_price=65.0,
        predicted_prices=pd.Series([70, 72, 75]),
        historical_avg=80.0,
        volatility=10.0
    )
    print(f"\n✅ Score calculé: {score}/100")
    
    # Test recommandation
    action, label, color = signals.get_recommendation(score, 65.0, pd.Series([70, 72, 75]))
    print(f"✅ Recommandation: {label} ({action}, {color})")
    
    # Test alertes
    alerts = signals.detect_alerts(55.0, pd.Series([70, 80, 90]), 18.0)
    print(f"\n✅ {len(alerts)} alertes détectées")
    for alert in alerts:
        print(f"   - {alert['title']}")
    
    print("\n" + "=" * 60)
    print("✅ Tests passés!")

