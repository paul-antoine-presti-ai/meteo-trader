"""
Analyse Offre/Demande (Supply & Demand Gap Analysis)
Le cœur du trading électricité
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SupplyDemandAnalyzer:
    """Analyseur de l'équilibre offre/demande"""
    
    def __init__(self):
        pass
    
    def calculate_gap(self, production_mw, load_mw):
        """
        Calcule le gap entre offre et demande
        
        Args:
            production_mw: Production totale (MW)
            load_mw: Consommation (MW)
        
        Returns:
            Gap en MW (positif = excédent, négatif = déficit)
        """
        return production_mw - load_mw
    
    def calculate_reserve_margin(self, production_mw, load_mw):
        """
        Calcule la marge de réserve (%)
        
        Args:
            production_mw: Production totale
            load_mw: Consommation
        
        Returns:
            Marge en % (positif = ok, négatif = tension)
        """
        if load_mw == 0:
            return 0
        
        return ((production_mw - load_mw) / load_mw) * 100
    
    def analyze_market_tension(self, reserve_margin):
        """
        Détermine le niveau de tension du marché
        
        Args:
            reserve_margin: Marge de réserve (%)
        
        Returns:
            Dict avec niveau et description
        """
        if reserve_margin < -5:
            return {
                'level': 'CRITICAL',
                'color': 'red',
                'emoji': '🔴',
                'description': 'Déficit critique - Risque de blackout',
                'price_impact': 'Prix va exploser (+50%+)',
                'trader_action': 'NE PAS ACHETER - Attendre retour à la normale'
            }
        elif reserve_margin < -2:
            return {
                'level': 'HIGH_TENSION',
                'color': 'orange',
                'emoji': '🟠',
                'description': 'Forte tension - Déficit important',
                'price_impact': 'Prix très élevés (+30%)',
                'trader_action': 'Acheter seulement si urgent, prix va rester élevé'
            }
        elif reserve_margin < 0:
            return {
                'level': 'TENSION',
                'color': 'yellow',
                'emoji': '🟡',
                'description': 'Léger déficit',
                'price_impact': 'Prix élevés (+10-20%)',
                'trader_action': 'Surveiller, acheter si nécessaire'
            }
        elif reserve_margin < 5:
            return {
                'level': 'BALANCED',
                'color': 'green',
                'emoji': '🟢',
                'description': 'Équilibre normal',
                'price_impact': 'Prix normaux',
                'trader_action': 'Conditions normales d\'achat'
            }
        elif reserve_margin < 10:
            return {
                'level': 'SURPLUS',
                'color': 'lightgreen',
                'emoji': '💚',
                'description': 'Excédent modéré',
                'price_impact': 'Prix favorables (-10%)',
                'trader_action': 'BON MOMENT D\'ACHAT'
            }
        else:
            return {
                'level': 'HIGH_SURPLUS',
                'color': 'blue',
                'emoji': '💙',
                'description': 'Excédent important',
                'price_impact': 'Prix très bas (-20%+), possibles prix négatifs',
                'trader_action': 'EXCELLENT MOMENT D\'ACHAT'
            }
    
    def analyze_country_market(self, production_df, load_df, prices_df=None):
        """
        Analyse complète du marché d'un pays
        
        Args:
            production_df: DataFrame avec production (timestamp, total_mw ou colonnes par type)
            load_df: DataFrame avec consommation (timestamp, load_mw)
            prices_df: DataFrame optionnel avec prix (timestamp, price_eur_mwh)
        
        Returns:
            DataFrame avec analyse complète
        """
        # Merger production et load
        if 'total_mw' in production_df.columns:
            prod_col = 'total_mw'
        elif 'total_production_gw' in production_df.columns:
            production_df['total_mw'] = production_df['total_production_gw'] * 1000
            prod_col = 'total_mw'
        else:
            # Sommer toutes les colonnes de production (en GW)
            prod_cols = [c for c in production_df.columns if c != 'timestamp']
            if prod_cols:
                production_df['total_mw'] = production_df[prod_cols].sum(axis=1) * 1000
                prod_col = 'total_mw'
            else:
                return pd.DataFrame()
        
        merged = pd.merge(
            production_df[['timestamp', prod_col]],
            load_df[['timestamp', 'load_mw']],
            on='timestamp',
            how='inner'
        )
        
        if prices_df is not None and not prices_df.empty:
            merged = pd.merge(
                merged,
                prices_df[['timestamp', 'price_eur_mwh']],
                on='timestamp',
                how='left'
            )
        
        # Calculer gap et marge
        merged['production_mw'] = merged[prod_col]
        merged['gap_mw'] = merged['production_mw'] - merged['load_mw']
        merged['reserve_margin_pct'] = ((merged['production_mw'] - merged['load_mw']) / merged['load_mw']) * 100
        
        # Analyser tension
        merged['tension_level'] = merged['reserve_margin_pct'].apply(
            lambda x: self.analyze_market_tension(x)['level']
        )
        
        merged['tension_emoji'] = merged['reserve_margin_pct'].apply(
            lambda x: self.analyze_market_tension(x)['emoji']
        )
        
        # Convertir MW en GW pour lisibilité
        merged['production_gw'] = merged['production_mw'] / 1000
        merged['load_gw'] = merged['load_mw'] / 1000
        merged['gap_gw'] = merged['gap_mw'] / 1000
        
        return merged
    
    def get_current_situation(self, analysis_df):
        """
        Récupère la situation actuelle (dernière heure)
        
        Args:
            analysis_df: DataFrame avec analyse complète
        
        Returns:
            Dict avec situation actuelle
        """
        if analysis_df.empty:
            return None
        
        now = pd.Timestamp.now()
        recent = analysis_df[analysis_df['timestamp'] <= now].sort_values('timestamp', ascending=False)
        
        if recent.empty:
            return None
        
        latest = recent.iloc[0]
        
        tension_analysis = self.analyze_market_tension(latest['reserve_margin_pct'])
        
        return {
            'timestamp': latest['timestamp'],
            'production_gw': latest['production_gw'],
            'load_gw': latest['load_gw'],
            'gap_gw': latest['gap_gw'],
            'reserve_margin_pct': latest['reserve_margin_pct'],
            'tension': tension_analysis,
            'price_eur_mwh': latest.get('price_eur_mwh', None)
        }
    
    def forecast_next_hours(self, analysis_df, forecast_load_df, hours=24):
        """
        Prévision de la tension pour les prochaines heures
        
        Args:
            analysis_df: Analyse historique
            forecast_load_df: Prévisions de consommation
            hours: Nombre d'heures à prévoir
        
        Returns:
            DataFrame avec prévisions
        """
        now = pd.Timestamp.now()
        future = now + pd.Timedelta(hours=hours)
        
        # Production future (baseline sur pattern récent)
        recent_prod = analysis_df.tail(48)['production_gw'].mean()
        
        # Prévisions load
        future_loads = forecast_load_df[
            (forecast_load_df['timestamp'] > now) &
            (forecast_load_df['timestamp'] <= future)
        ].copy()
        
        if future_loads.empty:
            return pd.DataFrame()
        
        # Estimer production future (simplifié: moyenne récente)
        future_loads['production_gw'] = recent_prod
        future_loads['load_gw'] = future_loads['forecast_load_mw'] / 1000
        future_loads['gap_gw'] = future_loads['production_gw'] - future_loads['load_gw']
        future_loads['reserve_margin_pct'] = (future_loads['gap_gw'] / future_loads['load_gw']) * 100
        
        future_loads['tension_level'] = future_loads['reserve_margin_pct'].apply(
            lambda x: self.analyze_market_tension(x)['level']
        )
        
        return future_loads[['timestamp', 'production_gw', 'load_gw', 'gap_gw', 'reserve_margin_pct', 'tension_level']]


def calculate_historical_spreads(prices_dict, days=7):
    """
    Calcule les spreads historiques entre pays
    
    Args:
        prices_dict: Dict {country: DataFrame avec prices}
        days: Nombre de jours d'historique
    
    Returns:
        Dict avec spreads historiques
    """
    spreads = {}
    countries = list(prices_dict.keys())
    
    for from_country in countries:
        for to_country in countries:
            if from_country == to_country:
                continue
            
            df_from = prices_dict[from_country]
            df_to = prices_dict[to_country]
            
            # Merger
            merged = pd.merge(
                df_from[['timestamp', 'price_eur_mwh']],
                df_to[['timestamp', 'price_eur_mwh']],
                on='timestamp',
                suffixes=('_from', '_to')
            )
            
            if merged.empty:
                continue
            
            # Calculer spread
            merged['spread'] = merged['price_eur_mwh_to'] - merged['price_eur_mwh_from']
            
            # Stats
            key = f"{from_country}_{to_country}"
            spreads[key] = {
                'mean': merged['spread'].mean(),
                'std': merged['spread'].std(),
                'min': merged['spread'].min(),
                'max': merged['spread'].max(),
                'median': merged['spread'].median(),
                'p25': merged['spread'].quantile(0.25),
                'p75': merged['spread'].quantile(0.75),
                'p90': merged['spread'].quantile(0.90),
                'count': len(merged)
            }
    
    return spreads


def get_spread_percentile(current_spread, historical_stats):
    """
    Calcule le percentile du spread actuel vs historique
    
    Args:
        current_spread: Spread actuel
        historical_stats: Dict avec stats historiques
    
    Returns:
        Percentile (0-100) et qualité
    """
    if not historical_stats or historical_stats['count'] == 0:
        return 50, 'Unknown'
    
    mean = historical_stats['mean']
    std = historical_stats['std']
    
    if std == 0:
        return 50, 'Normal'
    
    # Z-score
    z_score = (current_spread - mean) / std
    
    # Percentile approximatif
    if z_score < -2:
        percentile = 2
    elif z_score < -1:
        percentile = 16
    elif z_score < 0:
        percentile = 40
    elif z_score < 1:
        percentile = 60
    elif z_score < 2:
        percentile = 84
    else:
        percentile = 98
    
    # Qualité
    if percentile >= 90:
        quality = '🔥 Exceptionnel (Top 10%)'
    elif percentile >= 75:
        quality = '💰 Très bon (Top 25%)'
    elif percentile >= 50:
        quality = '✅ Au-dessus de la moyenne'
    elif percentile >= 25:
        quality = '⚪ Normal'
    else:
        quality = '⚠️ En-dessous de la moyenne'
    
    return percentile, quality


if __name__ == "__main__":
    # Test
    print("🧪 Test analyse offre/demande\n")
    
    analyzer = SupplyDemandAnalyzer()
    
    # Test tensions
    scenarios = [
        (-10, "Déficit critique"),
        (-3, "Forte tension"),
        (-1, "Léger déficit"),
        (2, "Équilibre"),
        (7, "Excédent modéré"),
        (15, "Excédent important")
    ]
    
    print("📊 Niveaux de tension:\n")
    for margin, description in scenarios:
        analysis = analyzer.analyze_market_tension(margin)
        print(f"{analysis['emoji']} {margin:+.0f}% - {analysis['level']}")
        print(f"   {analysis['description']}")
        print(f"   Prix: {analysis['price_impact']}")
        print(f"   Action: {analysis['trader_action']}\n")
    
    print("✅ Tests terminés!")

