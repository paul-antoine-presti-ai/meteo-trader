"""
Backtesting RÉEL basé sur les prédictions historiques de la base de données
"""

import pandas as pd
from datetime import datetime, timedelta


def calculate_real_backtest(db, days=30):
    """
    Calcule le P&L RÉEL si on avait suivi les top 10 recommandations chaque jour
    
    Args:
        db: PriceDatabase instance
        days: Nombre de jours à analyser
    
    Returns:
        dict avec résultats backtesting
    """
    # Récupérer les prédictions historiques
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Charger données depuis la DB
    timeline = db.get_unified_timeline(lookback_hours=days*24, lookahead_hours=0)
    
    if timeline.empty or 'historical_predicted_price' not in timeline.columns:
        return {
            'available': False,
            'message': "Pas encore assez de données historiques (besoin de quelques jours d'utilisation)"
        }
    
    # Filtrer données avec prédictions ET prix réels
    df = timeline[
        (timeline['historical_predicted_price'].notna()) &
        (timeline['actual_price'].notna())
    ].copy()
    
    if len(df) < 24:  # Minimum 24h de données
        return {
            'available': False,
            'message': f"Seulement {len(df)}h de données. Besoin d'au moins 24h."
        }
    
    # Ajouter date pour grouper par jour
    df['date'] = df['timestamp'].dt.date
    
    # Calculer les erreurs de prédiction
    df['error'] = df['historical_predicted_price'] - df['actual_price']
    df['error_abs'] = df['error'].abs()
    
    # Pour chaque jour, identifier les top 10 opportunités
    daily_pnl = []
    daily_details = []
    
    for date in df['date'].unique():
        day_data = df[df['date'] == date].copy()
        
        if len(day_data) < 10:  # Pas assez de données ce jour
            continue
        
        # Top 5 ACHAT (heures prédites les moins chères)
        top_buy = day_data.nsmallest(5, 'historical_predicted_price')
        
        # Top 5 VENTE (heures prédites les plus chères)
        top_sell = day_data.nlargest(5, 'historical_predicted_price')
        
        # Calculer P&L pour les achats
        # Si prédit bas et réel bas → BON (on a acheté au bon moment)
        # Gain = prix moyen du jour - prix réel à ce moment
        day_avg = day_data['actual_price'].mean()
        
        buy_pnl = 0
        for _, row in top_buy.iterrows():
            # Gain si on avait acheté à cette heure
            gain = day_avg - row['actual_price']
            buy_pnl += gain
            
            daily_details.append({
                'date': date,
                'timestamp': row['timestamp'],
                'action': 'ACHAT',
                'predicted': row['historical_predicted_price'],
                'actual': row['actual_price'],
                'pnl': gain,
                'success': gain > 0
            })
        
        # Calculer P&L pour les ventes
        # Si prédit haut et réel haut → BON (on a vendu au bon moment)
        sell_pnl = 0
        for _, row in top_sell.iterrows():
            # Gain si on avait vendu à cette heure
            gain = row['actual_price'] - day_avg
            sell_pnl += gain
            
            daily_details.append({
                'date': date,
                'timestamp': row['timestamp'],
                'action': 'VENTE',
                'predicted': row['historical_predicted_price'],
                'actual': row['actual_price'],
                'pnl': gain,
                'success': gain > 0
            })
        
        total_day_pnl = buy_pnl + sell_pnl
        daily_pnl.append({
            'date': date,
            'pnl': total_day_pnl,
            'buy_pnl': buy_pnl,
            'sell_pnl': sell_pnl,
            'n_actions': 10
        })
    
    if not daily_pnl:
        return {
            'available': False,
            'message': "Pas assez de jours complets pour le backtesting"
        }
    
    # Créer DataFrame résultats
    df_daily = pd.DataFrame(daily_pnl)
    df_details = pd.DataFrame(daily_details)
    
    # Calculer métriques globales
    total_pnl = df_daily['pnl'].sum()
    cumulative_pnl = df_daily['pnl'].cumsum()
    
    winning_days = (df_daily['pnl'] > 0).sum()
    total_days = len(df_daily)
    win_rate = (winning_days / total_days * 100) if total_days > 0 else 0
    
    avg_win = df_daily[df_daily['pnl'] > 0]['pnl'].mean() if winning_days > 0 else 0
    avg_loss = df_daily[df_daily['pnl'] < 0]['pnl'].mean() if (total_days - winning_days) > 0 else 0
    
    sharpe = (df_daily['pnl'].mean() / df_daily['pnl'].std()) if df_daily['pnl'].std() > 0 else 0
    
    # Statistiques actions
    total_actions = len(df_details)
    successful_actions = (df_details['pnl'] > 0).sum()
    action_success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
    
    return {
        'available': True,
        'total_pnl': total_pnl,
        'cumulative_pnl': cumulative_pnl.tolist(),
        'dates': df_daily['date'].tolist(),
        'daily_pnl': df_daily['pnl'].tolist(),
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'sharpe_ratio': sharpe,
        'total_days': total_days,
        'winning_days': winning_days,
        'losing_days': total_days - winning_days,
        'action_success_rate': action_success_rate,
        'total_actions': total_actions,
        'successful_actions': successful_actions,
        'details': df_details.to_dict('records')[-10:],  # 10 dernières transactions
        'best_day': df_daily.nlargest(1, 'pnl').iloc[0].to_dict() if not df_daily.empty else None,
        'worst_day': df_daily.nsmallest(1, 'pnl').iloc[0].to_dict() if not df_daily.empty else None,
    }

