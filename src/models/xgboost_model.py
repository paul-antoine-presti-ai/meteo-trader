"""
XGBoost Model pour MétéoTrader
Alternative à Random Forest avec meilleure précision attendue
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle
from datetime import datetime


class XGBoostPricePredictor:
    """Prédicteur de prix avec XGBoost"""
    
    def __init__(self,
                 n_estimators: int = 200,
                 max_depth: int = 7,
                 learning_rate: float = 0.1,
                 subsample: float = 0.8,
                 colsample_bytree: float = 0.8,
                 random_state: int = 42):
        """
        Initialize XGBoost model
        
        Args:
            n_estimators: Nombre d'arbres
            max_depth: Profondeur max arbres
            learning_rate: Taux d'apprentissage
            subsample: Fraction échantillons par arbre
            colsample_bytree: Fraction features par arbre
            random_state: Seed reproductibilité
        """
        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=random_state,
            objective='reg:squarederror',
            tree_method='hist',  # Plus rapide
            verbosity=0  # Pas de logs
        )
        
        self.feature_names = None
        self.training_score = None
        self.test_score = None
        self.feature_importance = None
    
    def train(self, X_train, y_train, X_test, y_test):
        """
        Entraîne le modèle
        
        Args:
            X_train: Features train
            y_train: Target train
            X_test: Features test
            y_test: Target test
        
        Returns:
            Dict avec métriques
        """
        print("🚀 Training XGBoost...")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test: {len(X_test)} samples")
        print(f"   Features: {X_train.shape[1]}")
        
        # Train
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Prédictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Métriques train
        train_metrics = {
            'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'mae': mean_absolute_error(y_train, y_train_pred),
            'r2': r2_score(y_train, y_train_pred)
        }
        
        # Métriques test
        test_metrics = {
            'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'mae': mean_absolute_error(y_test, y_test_pred),
            'r2': r2_score(y_test, y_test_pred)
        }
        
        # Stocker
        self.feature_names = X_train.columns.tolist()
        self.training_score = train_metrics
        self.test_score = test_metrics
        
        # Feature importance
        importance = self.model.feature_importances_
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print(f"\n✅ Training terminé!")
        print(f"   R² Train: {train_metrics['r2']:.4f}")
        print(f"   R² Test: {test_metrics['r2']:.4f}")
        print(f"   MAE Test: {test_metrics['mae']:.2f} €/MWh")
        
        return {
            'train': train_metrics,
            'test': test_metrics,
            'feature_importance': self.feature_importance
        }
    
    def predict(self, X):
        """Prédiction"""
        return self.model.predict(X)
    
    def save(self, filepath: str):
        """Sauvegarde modèle"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f"✅ Modèle sauvegardé: {filepath}")
    
    @staticmethod
    def load(filepath: str):
        """Charge modèle"""
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        print(f"✅ Modèle chargé: {filepath}")
        return model
    
    def compare_with_rf(self, rf_metrics: dict) -> pd.DataFrame:
        """
        Compare XGBoost vs Random Forest
        
        Args:
            rf_metrics: Dict avec métriques RF
        
        Returns:
            DataFrame comparatif
        """
        comparison = pd.DataFrame({
            'Métrique': ['R² Score', 'RMSE (€/MWh)', 'MAE (€/MWh)', 'Erreur (%)'],
            'Random Forest': [
                rf_metrics['test']['r2'],
                rf_metrics['test']['rmse'],
                rf_metrics['test']['mae'],
                (rf_metrics['test']['mae'] / 75) * 100  # Assuming avg ~75€
            ],
            'XGBoost': [
                self.test_score['r2'],
                self.test_score['rmse'],
                self.test_score['mae'],
                (self.test_score['mae'] / 75) * 100
            ]
        })
        
        # Calcul amélioration
        comparison['Amélioration'] = [
            f"{((comparison['XGBoost'][0] - comparison['Random Forest'][0]) / comparison['Random Forest'][0] * 100):.1f}%",
            f"{((comparison['Random Forest'][1] - comparison['XGBoost'][1]) / comparison['Random Forest'][1] * 100):.1f}%",
            f"{((comparison['Random Forest'][2] - comparison['XGBoost'][2]) / comparison['Random Forest'][2] * 100):.1f}%",
            f"{((comparison['Random Forest'][3] - comparison['XGBoost'][3]) / comparison['Random Forest'][3] * 100):.1f}%"
        ]
        
        return comparison


def train_xgboost_model(df: pd.DataFrame, 
                       target_col: str = 'price_eur_mwh',
                       test_size: float = 0.2) -> tuple:
    """
    Pipeline complet training XGBoost
    
    Args:
        df: DataFrame avec features et target
        target_col: Colonne target
        test_size: Fraction test set
    
    Returns:
        (model, X_test, y_test, y_pred, feature_names, metrics)
    """
    print("=" * 70)
    print("🚀 TRAINING XGBOOST MODEL")
    print("=" * 70)
    
    # Séparer features et target
    feature_cols = [col for col in df.columns if col not in [target_col, 'timestamp']]
    X = df[feature_cols]
    y = df[target_col]
    
    print(f"\n📊 Données:")
    print(f"   Total: {len(df)} samples")
    print(f"   Features: {len(feature_cols)}")
    print(f"   Target: {target_col}")
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, shuffle=False
    )
    
    # Créer et entraîner modèle
    model = XGBoostPricePredictor()
    metrics = model.train(X_train, y_train, X_test, y_test)
    
    # Prédictions test
    y_pred = model.predict(X_test)
    
    print("\n" + "=" * 70)
    print("✅ XGBOOST TRAINING TERMINÉ!")
    print("=" * 70)
    
    return model, X_test, y_test, y_pred, feature_cols, metrics


if __name__ == "__main__":
    # Test
    print("🧪 Test XGBoost Module")
    print("=" * 60)
    
    # Données test
    np.random.seed(42)
    n_samples = 1000
    
    df_test = pd.DataFrame({
        'temperature_c': np.random.normal(15, 5, n_samples),
        'wind_speed_kmh': np.random.normal(20, 10, n_samples),
        'solar_radiation_wm2': np.random.normal(300, 100, n_samples),
        'demand_gw': np.random.normal(50, 10, n_samples),
        'nuclear_production_gw': np.random.normal(40, 5, n_samples),
        'hour': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples)
    })
    
    # Target synthétique avec corrélations
    df_test['price_eur_mwh'] = (
        50 + 
        df_test['demand_gw'] * 0.5 +
        -df_test['nuclear_production_gw'] * 0.3 +
        df_test['temperature_c'] * 0.2 +
        np.random.normal(0, 5, n_samples)
    )
    
    # Train
    model, X_test, y_test, y_pred, features, metrics = train_xgboost_model(df_test)
    
    print(f"\n📊 Feature Importance:")
    print(model.feature_importance.head())
    
    print("\n✅ Test réussi!")

