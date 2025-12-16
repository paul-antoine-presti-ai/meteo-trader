"""
Composants utilitaires pour MétéoTrader Pro
"""

import streamlit as st
from datetime import datetime
import pytz

def display_clock_header():
    """
    Affiche une barre sticky minimaliste en haut avec horloge LIVE
    """
    import streamlit.components.v1 as components
    
    paris_tz = pytz.timezone('Europe/Paris')
    now = datetime.now(paris_tz)
    
    # Calculer temps jusqu'à prochaine mise à jour
    next_hour = (now.replace(minute=0, second=0, microsecond=0) + __import__('datetime').timedelta(hours=1))
    time_to_update = next_hour - now
    hours_to_update = int(time_to_update.total_seconds() / 3600)
    minutes_to_update = int((time_to_update.total_seconds() % 3600) / 60)
    
    # Barre sticky horizontale minimaliste
    components.html(f"""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #1a1a1a 0%, #0c0c0c 100%);
        border-bottom: 1px solid rgba(255, 107, 53, 0.2);
        padding: 8px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 9999;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    ">
        <!-- Horloge à gauche -->
        <div style="display: flex; align-items: center; gap: 16px;">
            <div id="live-clock" style="
                font-size: 18px;
                font-weight: 400;
                color: #ffffff;
                font-family: 'SF Mono', Monaco, monospace;
                letter-spacing: 1px;
            ">
                {now.strftime('%H:%M:%S')}
            </div>
            <div style="
                font-size: 11px;
                color: #a0a0a0;
                border-left: 1px solid #333;
                padding-left: 12px;
            ">
                <span style="color: #ff6b35; font-weight: 500;">Europe/Paris</span> · {now.strftime('%d %b %Y')}
            </div>
        </div>
        
        <!-- Timer MAJ à droite -->
        <div style="
            background: rgba(255, 107, 53, 0.1);
            border: 1px solid rgba(255, 107, 53, 0.3);
            border-radius: 6px;
            padding: 4px 12px;
            font-size: 11px;
            color: #ff6b35;
            font-weight: 500;
        ">
            🔄 MAJ dans {"{}h{:02d}".format(hours_to_update, minutes_to_update) if hours_to_update > 0 else "{}min".format(minutes_to_update)}
        </div>
    </div>
    
    <script>
    function updateClock() {{
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const clockElement = document.getElementById('live-clock');
        if (clockElement) {{
            clockElement.textContent = hours + ':' + minutes + ':' + seconds;
        }}
    }}
    
    // Mettre à jour toutes les secondes
    setInterval(updateClock, 1000);
    updateClock();
    </script>
    """, height=45)


def display_data_freshness(last_data_time):
    """
    Affiche l'âge des données et le prochain rafraîchissement
    """
    now = datetime.now()
    age = now - last_data_time
    age_minutes = int(age.total_seconds() / 60)
    
    # Calcul du prochain rafraîchissement (prochain top de l'heure)
    next_refresh = now.replace(minute=0, second=0, microsecond=0)
    if now.minute > 5:  # Si on est après :05, le prochain refresh est dans 1h
        next_refresh += __import__('datetime').timedelta(hours=1)
    
    time_to_refresh = next_refresh - now
    minutes_to_refresh = int(time_to_refresh.total_seconds() / 60)
    
    freshness_color = "#00ff00" if age_minutes < 120 else ("#ffa500" if age_minutes < 240 else "#ff0000")
    
    st.markdown(f"""
    <div style="
        background: rgba(26, 26, 26, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        display: flex;
        gap: 24px;
        align-items: center;
    ">
        <div>
            <span style="color: #888; font-size: 12px; text-transform: uppercase;">Âge des données</span>
            <div style="color: {freshness_color}; font-weight: 600; font-size: 16px; margin-top: 4px;">
                {'🟢' if age_minutes < 120 else '🟠' if age_minutes < 240 else '🔴'} 
                Il y a {age_minutes} minutes
            </div>
        </div>
        
        <div style="border-left: 1px solid #333; padding-left: 24px;">
            <span style="color: #888; font-size: 12px; text-transform: uppercase;">Prochain rafraîchissement</span>
            <div style="color: #ff6b35; font-weight: 600; font-size: 16px; margin-top: 4px;">
                ⏱️ Dans {minutes_to_refresh} minutes
            </div>
        </div>
        
        <div style="margin-left: auto;">
            <button style="
                background: rgba(255, 107, 53, 0.1);
                border: 1px solid rgba(255, 107, 53, 0.3);
                color: #ff6b35;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                transition: all 0.2s;
            " onclick="window.location.reload()">
                🔄 Rafraîchir maintenant
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)


def format_recommendation_card(recommendation, price_current, price_predicted_next_hours):
    """
    Crée une carte de recommandation professionnelle
    
    Args:
        recommendation: dict avec action, raison, confiance, impact_eur_mwh
        price_current: prix actuel
        price_predicted_next_hours: liste des prix prédits pour les prochaines heures
    """
    
    action_colors = {
        'BUY': ('#00ff00', '📈'),
        'SELL': ('#ff6b35', '📉'),
        'HOLD': ('#ffa500', '⏸️'),
        'WAIT': ('#6495ed', '⏳')
    }
    
    color, emoji = action_colors.get(recommendation['action'], ('#888', '❓'))
    
    avg_next_price = sum(price_predicted_next_hours[:6]) / len(price_predicted_next_hours[:6])
    price_trend = avg_next_price - price_current
    trend_pct = (price_trend / price_current) * 100
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e1e1e 0%, #141414 100%);
        border: 2px solid {color};
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <div style="font-size: 14px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                    Recommandation du Modèle ML
                </div>
                <div style="font-size: 36px; font-weight: 700; color: {color};">
                    {emoji} {recommendation['action']}
                </div>
            </div>
            
            <div style="text-align: right;">
                <div style="font-size: 12px; color: #888;">Confiance</div>
                <div style="
                    font-size: 28px;
                    font-weight: 700;
                    color: {'#00ff00' if recommendation['confiance'] > 0.8 else '#ffa500' if recommendation['confiance'] > 0.6 else '#ff6b35'};
                ">
                    {recommendation['confiance']*100:.0f}%
                </div>
            </div>
        </div>
        
        <div style="
            background: rgba(255, 107, 53, 0.05);
            border-left: 3px solid #ff6b35;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        ">
            <div style="font-size: 14px; color: #e3e3e3; line-height: 1.6;">
                {recommendation['raison']}
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px;">
            <div style="background: rgba(255, 255, 255, 0.03); padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #888; text-transform: uppercase;">Prix Actuel</div>
                <div style="font-size: 20px; font-weight: 600; color: #fff; margin-top: 4px;">
                    {price_current:.2f} €/MWh
                </div>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.03); padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #888; text-transform: uppercase;">Tendance 6h</div>
                <div style="font-size: 20px; font-weight: 600; color: {'#00ff00' if price_trend > 0 else '#ff6b35'}; margin-top: 4px;">
                    {'+' if price_trend > 0 else ''}{price_trend:.2f} €
                    <span style="font-size: 14px; margin-left: 4px;">({trend_pct:+.1f}%)</span>
                </div>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.03); padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #888; text-transform: uppercase;">Impact Estimé</div>
                <div style="font-size: 20px; font-weight: 600; color: #ff6b35; margin-top: 4px;">
                    {recommendation.get('impact_eur_mwh', 0):.2f} €/MWh
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

