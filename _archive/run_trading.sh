#!/bin/bash
# Lancement MétéoTrader Pro - Version Trading

echo "🚀 Démarrage MétéoTrader Pro..."

# Activer environnement virtuel
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé. Lancez: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Vérifier que les dépendances sont installées
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
fi

# Créer dossier data si nécessaire
mkdir -p data

# Lancer Streamlit
echo "✅ Lancement de l'interface..."
streamlit run app_trading.py --server.port 8501 --server.address localhost


