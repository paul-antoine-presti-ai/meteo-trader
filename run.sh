#!/bin/bash
# MétéoTrader Pro - Plateforme Unifiée

echo "⚡ MétéoTrader Pro - Plateforme Complète"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Activer venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé"
    exit 1
fi

# Créer dossiers
mkdir -p data models

# Lancer app
echo "🚀 Lancement interface..."
streamlit run app.py --server.port 8501 --server.address localhost

