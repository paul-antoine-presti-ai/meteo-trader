"""
Backtesting ML basé sur train/test split des données historiques APIs
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_ml_backtest(df_full, model, features, test_size=0.3):
    """
    Calcule le P&L en backtesting ML sur l'ensemble de test
    
    Args:
        df_full: DataFrame avec toutes les données historiques
        model: Modèle ML entraîné
        features: Liste des features utilisées
        test_size: Proportion de données pour le test (default 0.3 = 30%)
    
    Returns:
        dict avec résultats backtesting ML
    """
    try:
        # Préparer les données
        df = df_full.copy()
        
        if 'price_eur_mwh' not in df.columns or len(df) < 100:
            return {
                'available': False,
                'message': f"Pas assez de données ({len(df)} heures). Minimum 100h requis."
            }
        
        # Supprimer les NaN
        df = df.dropna(subset=['price_eur_mwh'] + features)
        
        if len(df) < 100:
            return {
                'available': False,
                'message': "Pas assez de données après nettoyage."
            }
        
        # Split temporel (pas random, pour respecter la chronologie)
        split_idx = int(len(df) * (1 - test_size))
        
        df_train = df.iloc[:split_idx].copy()
        df_test = df.iloc[split_idx:].copy()
        
        if len(df_test) < 24:
            return {
                'available': False,
                'message': f"Ensemble test trop petit ({len(df_test)}h). Besoin minimum 24h."
            }
        
        # Prédictions sur le test set
        X_test = df_test[features]
        y_test = df_test['price_eur_mwh']
        y_pred = model.predict(X_test)
        
        df_test['predicted_price'] = y_pred
        df_test['actual_price'] = y_test
        
        # Ajouter date pour grouper par jour
        df_test['date'] = df_test['timestamp'].dt.date
        
        # Pour chaque jour, simuler trading
        daily_pnl = []
        daily_details = []
        
        for date in df_test['date'].unique():
            day_data = df_test[df_test['date'] == date].copy()
            
            if len(day_data) < 10:  # Besoin de 10h minimum pour top 10
                continue
            
            # Top 5 ACHAT (heures prédites les moins chères)
            top_buy = day_data.nsmallest(5, 'predicted_price')
            
            # Top 5 VENTE (heures prédites les plus chères)
            top_sell = day_data.nlargest(5, 'predicted_price')
            
            # Prix moyen réel du jour (benchmark)
            day_avg = day_data['actual_price'].mean()
            
            # P&L des achats
            buy_pnl = 0
            for _, row in top_buy.iterrows():
                # Gain = on achète quand c'est prédit bas, profit si réel bas aussi
                gain = day_avg - row['actual_price']
                buy_pnl += gain
                
                daily_details.append({
                    'date': date,
                    'timestamp': row['timestamp'],
                    'action': 'ACHAT',
                    'predicted': row['predicted_price'],
                    'actual': row['actual_price'],
                    'pnl': gain,
                    'success': gain > 0
                })
            
            # P&L des ventes
            sell_pnl = 0
            for _, row in top_sell.iterrows():
                # Gain = on vend quand c'est prédit haut, profit si réel haut aussi
                gain = row['actual_price'] - day_avg
                sell_pnl += gain
                
                daily_details.append({
                    'date': date,
                    'timestamp': row['timestamp'],
                    'action': 'VENTE',
                    'predicted': row['predicted_price'],
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
                'n_actions': min(10, len(day_data))
            })
        
        if not daily_pnl:
            return {
                'available': False,
                'message': "Pas assez de jours complets dans le test set."
            }
        
        # Créer DataFrames résultats
        df_daily = pd.DataFrame(daily_pnl)
        df_details = pd.DataFrame(daily_details)
        
        # Métriques globales
        total_pnl = df_daily['pnl'].sum()
        cumulative_pnl = df_daily['pnl'].cumsum().tolist()
        
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
        
        # Erreur de prédiction moyenne
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        return {
            'available': True,
            'total_pnl': total_pnl,
            'cumulative_pnl': cumulative_pnl,
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
            'details': df_details.tail(10).to_dict('records'),  # 10 dernières
            'best_day': df_daily.nlargest(1, 'pnl').iloc[0].to_dict() if not df_daily.empty else None,
            'worst_day': df_daily.nsmallest(1, 'pnl').iloc[0].to_dict() if not df_daily.empty else None,
            # Métriques ML
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'test_size': len(df_test),
            'train_size': len(df_train),
            'total_hours': len(df),
        }
    
    except Exception as e:
        return {
            'available': False,
            'message': f"Erreur backtesting: {str(e)}"
        }

