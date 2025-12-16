"""
Moteur d'arbitrage électricité européen
Calcule opportunités cross-border pour maximiser marge
"""

import pandas as pd
import numpy as np
from datetime import datetime


# Interconnexions et coûts (données simplifiées)
INTERCONNECTIONS = {
    # (From, To): Capacité max (MW), Coût transport (€/MWh)
    ('FR', 'DE'): {'capacity': 3000, 'cost': 2.5},
    ('FR', 'ES'): {'capacity': 2800, 'cost': 3.0},
    ('FR', 'IT'): {'capacity': 3200, 'cost': 3.5},
    ('FR', 'GB'): {'capacity': 2000, 'cost': 4.0},
    ('DE', 'FR'): {'capacity': 3000, 'cost': 2.5},
    ('ES', 'FR'): {'capacity': 2800, 'cost': 3.0},
    ('IT', 'FR'): {'capacity': 3200, 'cost': 3.5},
    ('GB', 'FR'): {'capacity': 2000, 'cost': 4.0},
    # Autres connexions directes (simplifiées)
    ('DE', 'ES'): {'capacity': 0, 'cost': 10},  # Via FR
    ('DE', 'IT'): {'capacity': 0, 'cost': 10},  # Via FR/AT
    ('ES', 'IT'): {'capacity': 0, 'cost': 10},  # Via FR
    ('ES', 'GB'): {'capacity': 0, 'cost': 10},  # Via FR
    ('IT', 'GB'): {'capacity': 0, 'cost': 10},  # Via FR
    ('GB', 'DE'): {'capacity': 0, 'cost': 10},  # Via FR/NL
}

# Compléter matrice (réciproques)
keys_to_add = {}
for (from_c, to_c), values in list(INTERCONNECTIONS.items()):
    if (to_c, from_c) not in INTERCONNECTIONS:
        keys_to_add[(to_c, from_c)] = values

INTERCONNECTIONS.update(keys_to_add)


class ArbitrageEngine:
    """Moteur de calcul d'opportunités d'arbitrage"""
    
    def __init__(self, predictions_dict):
        """
        Initialise le moteur
        
        Args:
            predictions_dict: Dict {country_code: DataFrame avec predicted_price}
        """
        self.predictions = predictions_dict
        self.opportunities = []
    
    def calculate_all_opportunities(self, max_volume_per_trade=100):
        """
        Calcule toutes les opportunités d'arbitrage possibles
        
        Args:
            max_volume_per_trade: Volume max par transaction (MWh)
        
        Returns:
            DataFrame avec toutes les opportunités
        """
        opportunities = []
        
        # Pour chaque paire de pays
        countries = list(self.predictions.keys())
        
        for from_country in countries:
            for to_country in countries:
                if from_country == to_country:
                    continue
                
                # Vérifier si interconnexion existe
                interconnection = INTERCONNECTIONS.get((from_country, to_country))
                
                if not interconnection or interconnection['capacity'] == 0:
                    continue
                
                # DataFrames prix
                df_from = self.predictions[from_country]
                df_to = self.predictions[to_country]
                
                # Merger sur timestamp
                merged = pd.merge(
                    df_from[['timestamp', 'predicted_price']],
                    df_to[['timestamp', 'predicted_price']],
                    on='timestamp',
                    suffixes=('_buy', '_sell')
                )
                
                if merged.empty:
                    continue
                
                # Calculer spread
                transport_cost = interconnection['cost']
                merged['spread_gross'] = merged['predicted_price_sell'] - merged['predicted_price_buy']
                merged['spread_net'] = merged['spread_gross'] - transport_cost
                
                # Volume optimal
                capacity_limit = interconnection['capacity'] / 1000  # MW -> MWh (simplifié)
                merged['volume_optimal'] = np.minimum(capacity_limit, max_volume_per_trade)
                
                # Gain total
                merged['gain_total'] = merged['spread_net'] * merged['volume_optimal']
                
                # Score (0-100)
                merged['score'] = merged['spread_net'].apply(lambda x: 
                    0 if x < 5 else
                    50 if x < 10 else
                    75 if x < 15 else
                    100
                )
                
                # Ajouter colonnes pays
                merged['from_country'] = from_country
                merged['to_country'] = to_country
                merged['transport_cost'] = transport_cost
                
                # Filtrer opportunités positives
                merged = merged[merged['spread_net'] > 3]  # Min 3€/MWh pour être intéressant
                
                if not merged.empty:
                    opportunities.append(merged)
        
        if not opportunities:
            return pd.DataFrame()
        
        # Combiner toutes les opportunités
        all_opps = pd.concat(opportunities, ignore_index=True)
        
        # Trier par gain total décroissant
        all_opps = all_opps.sort_values('gain_total', ascending=False)
        
        self.opportunities = all_opps
        return all_opps
    
    def get_top_opportunities(self, n=5, min_score=50):
        """
        Récupère les N meilleures opportunités
        
        Args:
            n: Nombre d'opportunités
            min_score: Score minimum
        
        Returns:
            DataFrame avec top opportunités
        """
        if self.opportunities is None or len(self.opportunities) == 0:
            return pd.DataFrame()
        
        # Filtrer par score
        filtered = self.opportunities[self.opportunities['score'] >= min_score]
        
        # Top N
        return filtered.head(n)
    
    def get_best_opportunity(self):
        """
        Récupère la meilleure opportunité actuelle
        
        Returns:
            Dict avec détails de l'opportunité ou None
        """
        if self.opportunities is None or len(self.opportunities) == 0:
            return None
        
        # Prendre la meilleure (déjà trié par gain_total)
        best = self.opportunities.iloc[0]
        
        return {
            'from_country': best['from_country'],
            'to_country': best['to_country'],
            'timestamp': best['timestamp'],
            'buy_price': best['predicted_price_buy'],
            'sell_price': best['predicted_price_sell'],
            'spread_gross': best['spread_gross'],
            'transport_cost': best['transport_cost'],
            'spread_net': best['spread_net'],
            'volume_optimal': best['volume_optimal'],
            'gain_total': best['gain_total'],
            'score': best['score']
        }
    
    def calculate_potential_margin(self, hours=48):
        """
        Calcule la marge totale potentielle sur une période
        
        Args:
            hours: Nombre d'heures à considérer
        
        Returns:
            Dict avec métriques
        """
        if self.opportunities is None or len(self.opportunities) == 0:
            return {'total_margin': 0, 'num_opportunities': 0, 'avg_margin': 0}
        
        # Filtrer sur période
        now = pd.Timestamp.now()
        future = now + pd.Timedelta(hours=hours)
        
        period_opps = self.opportunities[
            (self.opportunities['timestamp'] >= now) &
            (self.opportunities['timestamp'] <= future)
        ]
        
        if period_opps.empty:
            return {'total_margin': 0, 'num_opportunities': 0, 'avg_margin': 0}
        
        # Calculer métriques
        total_margin = period_opps['gain_total'].sum()
        num_opps = len(period_opps)
        avg_margin = period_opps['spread_net'].mean()
        
        return {
            'total_margin': total_margin,
            'num_opportunities': num_opps,
            'avg_margin': avg_margin,
            'period_hours': hours
        }
    
    def get_country_stats(self):
        """
        Statistiques par pays (où acheter/vendre le plus)
        
        Returns:
            Dict avec stats
        """
        if self.opportunities is None or len(self.opportunities) == 0:
            return {}
        
        stats = {}
        
        # Pays d'achat
        buy_stats = self.opportunities.groupby('from_country').agg({
            'gain_total': 'sum',
            'spread_net': 'mean'
        }).sort_values('gain_total', ascending=False)
        
        # Pays de vente
        sell_stats = self.opportunities.groupby('to_country').agg({
            'gain_total': 'sum',
            'spread_net': 'mean'
        }).sort_values('gain_total', ascending=False)
        
        stats['best_buy_countries'] = buy_stats.to_dict()
        stats['best_sell_countries'] = sell_stats.to_dict()
        
        return stats


def generate_recommendation(best_opportunity, country_names):
    """
    Génère une recommandation textuelle
    
    Args:
        best_opportunity: Dict avec meilleure opportunité
        country_names: Dict {code: nom}
    
    Returns:
        String avec recommandation formatée
    """
    if not best_opportunity:
        return "Aucune opportunité d'arbitrage détectée pour le moment."
    
    from_name = country_names.get(best_opportunity['from_country'], best_opportunity['from_country'])
    to_name = country_names.get(best_opportunity['to_country'], best_opportunity['to_country'])
    
    timestamp = best_opportunity['timestamp']
    if isinstance(timestamp, pd.Timestamp):
        time_str = timestamp.strftime('%H:%M le %d/%m')
    else:
        time_str = str(timestamp)
    
    # Emoji flag
    flags = {
        'FR': '🇫🇷',
        'DE': '🇩🇪',
        'ES': '🇪🇸',
        'IT': '🇮🇹',
        'GB': '🇬🇧'
    }
    
    flag_from = flags.get(best_opportunity['from_country'], '')
    flag_to = flags.get(best_opportunity['to_country'], '')
    
    # Score emoji
    score = best_opportunity['score']
    if score >= 75:
        score_emoji = '💰'
        score_text = 'ARBITRAGE FORT'
    elif score >= 50:
        score_emoji = '💵'
        score_text = 'ARBITRAGE MOYEN'
    else:
        score_emoji = '💸'
        score_text = 'ARBITRAGE FAIBLE'
    
    recommendation = f"""
{score_emoji} **{score_text}** - Score: {score:.0f}/100

**ACHETER:**  {flag_from} {from_name} @ {best_opportunity['buy_price']:.1f}€/MWh
**VENDRE:**   {flag_to} {to_name} @ {best_opportunity['sell_price']:.1f}€/MWh

**Spread brut:**    {best_opportunity['spread_gross']:.1f}€/MWh
**Coût transport:** -{best_opportunity['transport_cost']:.1f}€/MWh
**MARGE NETTE:**    **{best_opportunity['spread_net']:.1f}€/MWh**

**Volume optimal:** {best_opportunity['volume_optimal']:.0f} MWh
**GAIN TOTAL:**     **{best_opportunity['gain_total']:.0f}€**

**Moment optimal:** {time_str}
"""
    
    return recommendation.strip()


if __name__ == "__main__":
    # Test du moteur
    print("🧪 Test moteur d'arbitrage\n")
    
    # Données simulées
    from src.data.entsoe_api import EntsoeClient
    
    timestamps = pd.date_range(start=datetime.now(), periods=48, freq='h')
    
    predictions = {
        'FR': pd.DataFrame({
            'timestamp': timestamps,
            'predicted_price': [75 + np.sin(i/4) * 10 for i in range(48)]
        }),
        'DE': pd.DataFrame({
            'timestamp': timestamps,
            'predicted_price': [70 + np.sin(i/3) * 15 for i in range(48)]
        }),
        'ES': pd.DataFrame({
            'timestamp': timestamps,
            'predicted_price': [85 + np.sin(i/5) * 12 for i in range(48)]
        }),
    }
    
    # Créer moteur
    engine = ArbitrageEngine(predictions)
    
    # Calculer opportunités
    print("📊 Calcul opportunités...")
    opps = engine.calculate_all_opportunities()
    
    print(f"✅ {len(opps)} opportunités trouvées\n")
    
    # Meilleure opportunité
    best = engine.get_best_opportunity()
    
    if best:
        print("🎯 MEILLEURE OPPORTUNITÉ:")
        reco = generate_recommendation(best, EntsoeClient.COUNTRY_NAMES)
        print(reco)
    
    # Top 5
    print("\n📊 TOP 5 OPPORTUNITÉS:")
    top5 = engine.get_top_opportunities(n=5)
    
    for idx, row in top5.head(5).iterrows():
        print(f"\n{idx+1}. {row['from_country']}→{row['to_country']} | {row['spread_net']:.1f}€/MWh | {row['gain_total']:.0f}€")
    
    # Marge totale
    margin = engine.calculate_potential_margin(hours=48)
    print(f"\n💰 MARGE POTENTIELLE (48h): {margin['total_margin']:.0f}€")
    print(f"   Nombre d'opportunités: {margin['num_opportunities']}")
    print(f"   Marge moyenne: {margin['avg_margin']:.1f}€/MWh")

