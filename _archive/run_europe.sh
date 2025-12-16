#!/bin/bash
# Lancement MétéoTrader Pro Europe

echo "🚀 Démarrage MétéoTrader Pro Europe..."

# Activer environnement virtuel
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé"
    exit 1
fi

# Créer dossier data
mkdir -p data

# Lancer Streamlit
echo "✅ Lancement interface complète..."
streamlit run app_europe.py --server.port 8502 --server.address localhost

