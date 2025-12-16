"""
Base de données SQLite pour stocker prédictions et prix réels
Permet tracking accuracy dans le temps
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os


class PriceDatabase:
    """Gestion base de données prix électricité"""
    
    def __init__(self, db_path='data/meteotrader.db'):
        """
        Initialise connexion base de données
        
        Args:
            db_path: Chemin fichier SQLite
        """
        # Créer dossier si nécessaire
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
    
    def _create_tables(self):
        """Crée tables si elles n'existent pas"""
        cursor = self.conn.cursor()
        
        # Table prédictions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_timestamp DATETIME NOT NULL,
                target_timestamp DATETIME NOT NULL,
                predicted_price REAL NOT NULL,
                confidence_lower REAL,
                confidence_upper REAL,
                model_version TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table prix réels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actual_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME UNIQUE NOT NULL,
                price REAL NOT NULL,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table contrats clients
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                volume_mwh REAL NOT NULL,
                guaranteed_price_eur_mwh REAL NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table recommandations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                action TEXT NOT NULL,
                score INTEGER NOT NULL,
                volume_mwh REAL,
                target_price_eur_mwh REAL,
                expected_gain_eur REAL,
                reasoning TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table alertes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index pour performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_predictions_target 
            ON predictions(target_timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_actual_timestamp 
            ON actual_prices(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_contracts_status 
            ON contracts(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_alerts_active 
            ON alerts(is_active)
        ''')
        
        self.conn.commit()
    
    def store_predictions(self, predictions_df, model_version='v1'):
        """
        Stocke prédictions dans BDD
        
        Args:
            predictions_df: DataFrame avec colonnes timestamp, predicted_price
            model_version: Version du modèle
        """
        prediction_time = datetime.now()
        
        records = []
        for _, row in predictions_df.iterrows():
            records.append({
                'prediction_timestamp': str(prediction_time),
                'target_timestamp': str(row['timestamp']),
                'predicted_price': float(row['predicted_price']),
                'confidence_lower': float(row.get('confidence_lower')) if pd.notna(row.get('confidence_lower')) else None,
                'confidence_upper': float(row.get('confidence_upper')) if pd.notna(row.get('confidence_upper')) else None,
                'model_version': model_version
            })
        
        df = pd.DataFrame(records)
        df.to_sql('predictions', self.conn, if_exists='append', index=False)
        
        return len(records)
    
    def store_actual_prices(self, prices_df, source='RTE'):
        """
        Stocke prix réels dans BDD
        
        Args:
            prices_df: DataFrame avec colonnes timestamp, price_eur_mwh
            source: Source des données
        """
        records = []
        for _, row in prices_df.iterrows():
            records.append({
                'timestamp': str(row['timestamp']),
                'price': float(row['price_eur_mwh']),
                'source': source
            })
        
        df = pd.DataFrame(records)
        
        # Insert or replace (upsert)
        cursor = self.conn.cursor()
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO actual_prices (timestamp, price, source)
                VALUES (?, ?, ?)
            ''', (str(record['timestamp']), record['price'], record['source']))
        
        self.conn.commit()
        
        return len(records)
    
    def get_predictions(self, start_date=None, end_date=None, hours_ahead=None):
        """
        Récupère prédictions
        
        Args:
            start_date: Date début
            end_date: Date fin
            hours_ahead: Filtre par horizon (ex: 24 pour J+1)
        
        Returns:
            DataFrame avec prédictions
        """
        query = 'SELECT * FROM predictions WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND target_timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND target_timestamp <= ?'
            params.append(end_date)
        
        if hours_ahead:
            query += ' AND (julianday(target_timestamp) - julianday(prediction_timestamp)) * 24 <= ?'
            params.append(hours_ahead)
        
        query += ' ORDER BY target_timestamp'
        
        df = pd.read_sql_query(query, self.conn, params=params)
        df['prediction_timestamp'] = pd.to_datetime(df['prediction_timestamp'])
        df['target_timestamp'] = pd.to_datetime(df['target_timestamp'])
        
        return df
    
    def get_actual_prices(self, start_date=None, end_date=None):
        """
        Récupère prix réels
        
        Args:
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame avec prix réels
        """
        query = 'SELECT * FROM actual_prices WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        query += ' ORDER BY timestamp'
        
        df = pd.read_sql_query(query, self.conn, params=params)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def calculate_accuracy(self, period_hours=24):
        """
        Calcule accuracy sur période donnée
        
        Args:
            period_hours: Période en heures (1, 24, 168)
        
        Returns:
            Dict avec métriques accuracy
        """
        from datetime import timedelta
        
        # Période de référence
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=period_hours)
        
        # Récupérer prédictions et prix réels
        predictions = self.get_predictions(start_date=start_time, end_date=end_time)
        actuals = self.get_actual_prices(start_date=start_time, end_date=end_time)
        
        if predictions.empty or actuals.empty:
            return {
                'period_hours': period_hours,
                'n_predictions': 0,
                'mae': None,
                'rmse': None,
                'mape': None
            }
        
        # Merger sur target_timestamp
        merged = predictions.merge(
            actuals,
            left_on='target_timestamp',
            right_on='timestamp',
            how='inner'
        )
        
        if merged.empty:
            return {
                'period_hours': period_hours,
                'n_predictions': 0,
                'mae': None,
                'rmse': None,
                'mape': None
            }
        
        # Calculer métriques
        errors = merged['predicted_price'] - merged['price']
        
        mae = errors.abs().mean()
        rmse = (errors ** 2).mean() ** 0.5
        mape = (errors.abs() / merged['price']).mean() * 100
        
        return {
            'period_hours': period_hours,
            'n_predictions': len(merged),
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'start_time': start_time,
            'end_time': end_time
        }
    
    def get_historical_predictions(self, start_date=None, end_date=None):
        """
        Récupère prédictions HISTORIQUES (qui ont été faites dans le passé)
        
        Args:
            start_date: Date début
            end_date: Date fin
        
        Returns:
            DataFrame avec prédictions historiques et leurs vraies valeurs
        """
        query = '''
            SELECT 
                p.target_timestamp,
                p.predicted_price,
                p.prediction_timestamp,
                a.price as actual_price
            FROM predictions p
            LEFT JOIN actual_prices a ON p.target_timestamp = a.timestamp
            WHERE p.target_timestamp < datetime('now')
        '''
        params = []
        
        if start_date:
            query += ' AND p.target_timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND p.target_timestamp <= ?'
            params.append(end_date)
        
        query += ' ORDER BY p.target_timestamp'
        
        df = pd.read_sql_query(query, self.conn, params=params)
        
        if not df.empty:
            df['target_timestamp'] = pd.to_datetime(df['target_timestamp'])
            df['prediction_timestamp'] = pd.to_datetime(df['prediction_timestamp'])
        
        return df
    
    def get_unified_timeline(self, lookback_hours=72, lookahead_hours=48):
        """
        Récupère timeline unifiée: historique + prédictions historiques + prédictions futures
        
        Args:
            lookback_hours: Heures passées
            lookahead_hours: Heures futures
        
        Returns:
            DataFrame avec colonnes: timestamp, actual_price, predicted_price, historical_predicted_price, is_future
        """
        from datetime import timedelta
        
        now = datetime.now()
        start_time = now - timedelta(hours=lookback_hours)
        end_time = now + timedelta(hours=lookahead_hours)
        
        # Prix réels (passé)
        actuals = self.get_actual_prices(start_date=start_time, end_date=now)
        actuals = actuals.rename(columns={'price': 'actual_price'})
        actuals['is_future'] = False
        
        # Prédictions HISTORIQUES (ce qu'on avait prédit pour le passé)
        historical_preds = self.get_historical_predictions(start_date=start_time, end_date=now)
        
        # Merger prédictions historiques avec prix réels
        if not historical_preds.empty:
            # Prendre dernière prédiction pour chaque timestamp
            historical_preds = historical_preds.sort_values('prediction_timestamp').groupby('target_timestamp').last().reset_index()
            historical_preds = historical_preds.rename(columns={
                'target_timestamp': 'timestamp',
                'predicted_price': 'historical_predicted_price'
            })
            actuals = actuals.merge(
                historical_preds[['timestamp', 'historical_predicted_price']], 
                on='timestamp', 
                how='left'
            )
        else:
            actuals['historical_predicted_price'] = None
        
        # Prédictions FUTURES (ce qu'on prédit maintenant)
        predictions = self.get_predictions(start_date=now, end_date=end_time)
        
        # Prendre dernières prédictions pour chaque timestamp
        if not predictions.empty:
            predictions = predictions.sort_values('prediction_timestamp').groupby('target_timestamp').last().reset_index()
            predictions = predictions.rename(columns={
                'target_timestamp': 'timestamp',
                'predicted_price': 'predicted_price'
            })
            predictions['actual_price'] = None
            predictions['historical_predicted_price'] = None
            predictions['is_future'] = True
        
        # Combiner
        if actuals.empty and predictions.empty:
            return pd.DataFrame()
        elif actuals.empty:
            timeline = predictions[['timestamp', 'actual_price', 'predicted_price', 'historical_predicted_price', 'is_future']]
        elif predictions.empty:
            actuals['predicted_price'] = None
            timeline = actuals[['timestamp', 'actual_price', 'predicted_price', 'historical_predicted_price', 'is_future']]
        else:
            actuals['predicted_price'] = None
            timeline = pd.concat([
                actuals[['timestamp', 'actual_price', 'predicted_price', 'historical_predicted_price', 'is_future']],
                predictions[['timestamp', 'actual_price', 'predicted_price', 'historical_predicted_price', 'is_future']]
            ], ignore_index=True)
        
        timeline = timeline.sort_values('timestamp').reset_index(drop=True)
        
        return timeline
    
    # ===== GESTION CONTRATS =====
    
    def add_contract(self, client_name, volume_mwh, guaranteed_price, start_date, end_date):
        """
        Ajoute un nouveau contrat client
        
        Args:
            client_name: Nom du client
            volume_mwh: Volume total en MWh
            guaranteed_price: Prix garanti en €/MWh
            start_date: Date début
            end_date: Date fin
        
        Returns:
            ID du contrat créé
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO contracts (client_name, volume_mwh, guaranteed_price_eur_mwh, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (client_name, volume_mwh, guaranteed_price, start_date, end_date))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_active_contracts(self):
        """
        Récupère tous les contrats actifs
        
        Returns:
            DataFrame avec contrats actifs
        """
        query = '''
            SELECT * FROM contracts 
            WHERE status = 'active' 
            AND date('now') BETWEEN date(start_date) AND date(end_date)
            ORDER BY created_at DESC
        '''
        
        df = pd.read_sql_query(query, self.conn)
        if not df.empty:
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['end_date'] = pd.to_datetime(df['end_date'])
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        return df
    
    def update_contract_status(self, contract_id, status):
        """
        Met à jour le statut d'un contrat
        
        Args:
            contract_id: ID du contrat
            status: Nouveau statut (active, completed, cancelled)
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE contracts 
            SET status = ? 
            WHERE id = ?
        ''', (status, contract_id))
        
        self.conn.commit()
    
    # ===== GESTION RECOMMANDATIONS =====
    
    def store_recommendation(self, action, score, volume_mwh=None, target_price=None, 
                           expected_gain=None, reasoning=None):
        """
        Stocke une recommandation
        
        Args:
            action: BUY, HOLD, HEDGE
            score: Score 0-100
            volume_mwh: Volume recommandé
            target_price: Prix cible
            expected_gain: Gain attendu en €
            reasoning: Explication
        
        Returns:
            ID de la recommandation
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO recommendations 
            (timestamp, action, score, volume_mwh, target_price_eur_mwh, expected_gain_eur, reasoning)
            VALUES (datetime('now'), ?, ?, ?, ?, ?, ?)
        ''', (action, score, volume_mwh, target_price, expected_gain, reasoning))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_latest_recommendation(self):
        """
        Récupère la dernière recommandation
        
        Returns:
            Dict avec la recommandation ou None
        """
        query = '''
            SELECT * FROM recommendations 
            ORDER BY created_at DESC 
            LIMIT 1
        '''
        
        df = pd.read_sql_query(query, self.conn)
        
        if df.empty:
            return None
        
        return df.iloc[0].to_dict()
    
    # ===== GESTION ALERTES =====
    
    def create_alert(self, alert_type, severity, message):
        """
        Crée une nouvelle alerte
        
        Args:
            alert_type: Type (price, opportunity, risk)
            severity: Sévérité (high, medium, low)
            message: Message
        
        Returns:
            ID de l'alerte
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (timestamp, alert_type, severity, message)
            VALUES (datetime('now'), ?, ?, ?)
        ''', (alert_type, severity, message))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_active_alerts(self, limit=10):
        """
        Récupère les alertes actives
        
        Args:
            limit: Nombre max d'alertes
        
        Returns:
            DataFrame avec alertes actives
        """
        query = '''
            SELECT * FROM alerts 
            WHERE is_active = 1 
            ORDER BY created_at DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[limit])
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        return df
    
    def dismiss_alert(self, alert_id):
        """
        Désactive une alerte
        
        Args:
            alert_id: ID de l'alerte
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE alerts 
            SET is_active = 0 
            WHERE id = ?
        ''', (alert_id,))
        
        self.conn.commit()
    
    def close(self):
        """Ferme connexion BDD"""
        self.conn.close()


if __name__ == "__main__":
    # Test
    print("🧪 Test base de données...")
    
    db = PriceDatabase('data/test_meteotrader.db')
    
    # Test stockage prix réels
    test_prices = pd.DataFrame({
        'timestamp': pd.date_range(start='2025-12-15', periods=24, freq='h'),
        'price_eur_mwh': [80 + i * 2 for i in range(24)]
    })
    
    n = db.store_actual_prices(test_prices)
    print(f"✅ {n} prix réels stockés")
    
    # Test stockage prédictions
    test_predictions = pd.DataFrame({
        'timestamp': pd.date_range(start='2025-12-16', periods=24, freq='h'),
        'predicted_price': [85 + i * 2 for i in range(24)],
        'confidence_lower': [75 + i * 2 for i in range(24)],
        'confidence_upper': [95 + i * 2 for i in range(24)]
    })
    
    n = db.store_predictions(test_predictions)
    print(f"✅ {n} prédictions stockées")
    
    # Test accuracy
    accuracy = db.calculate_accuracy(period_hours=24)
    print(f"\n📊 Accuracy 24h:")
    print(f"  MAE: {accuracy['mae']:.2f} €/MWh" if accuracy['mae'] else "  Pas assez de données")
    
    # Test timeline
    timeline = db.get_unified_timeline(lookback_hours=24, lookahead_hours=24)
    print(f"\n📈 Timeline: {len(timeline)} points")
    print(timeline.head())
    
    db.close()
    print("\n✅ Tests réussis!")

