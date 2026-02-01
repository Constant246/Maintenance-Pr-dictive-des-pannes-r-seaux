from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import random
import time

app = FastAPI()
API_KEY_SECRET = "mon_code_secret_123" # Ma clé secrète

#--- VARIABLES D'ETAT POUR NOTRE DEMO ---
# On initialise des valeurs pour pouvoir les "reparer" dynamiquement
current_cpu_load = 85.0

# Modèle pour recevoir l'ordre de l'agent de Remédiation
class RemedyOrder(BaseModel):
    action_type: str  # ex: "RESTART_SERVICE", "FLUSH_CACHE"
    agent_id: str     # Pour savoir quel agent a décidé cela

# 1. L'Agent de Prédiction
@app.get("/network-status")
def get_status(x_api_key: str = Header(None)): # On attend un header nommé X-API-Key
    global current_cpu_load
    # Pour protéger mon API
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Simulation dynamique de métriques (On va les remplacer par des vraies données plus tard)
    latency = random.uniform(10, 150)    # en ms
    packet_loss = random.uniform(0, 3)   # en %
    # le CPU fluctue autour de notre variable globale
    cpu_load = current_cpu_load + random.uniform(-5, 5)
    cpu_load = max(10, min(100, cpu_load))    # en %

    # Calcul du score de risque (Normalisé sur 100)
    # Plus le score est haut, plus la panne est proche
    risk_score = (latency * 0.2) + (packet_loss * 10) + (cpu_load * 0.4)

    status = "OK"
    if risk_score > 70:
        status = "CRITICAL"
    elif risk_score > 40:
        status = "WARNING"

    return {
        "metrics": {
            "latency_ms": round(latency, 2),
            "packet_loss_pct": round(packet_loss, 2),
            "cpu_load_pct": round(cpu_load, 2),
        },
        "analysis": {
            "risk_score": round(risk_score, 2),
            "status": status,
            "message": "Anomalie détectée" if status != "OK" else "Réseau stable"
        }
    }

# 2. --- NOUVEAU : L'AGENT DE REMEDIATION (Action) ---
@app.post("/remedy")
def apply_remedy(order: RemedyOrder, x_api_key: str = Header(None)):
    global current_cpu_load
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Accès non autorisé !")

    start_time = time.time()

    # LOGIQUE DE REPARATION
    # Si l'IA demande une réparation, on fait chuter la charge CPU dans l'immédiat
    if order.action_type in ["RESTART_SERVICE", "FLUSH_CACHE"]:
        current_cpu_load = 25.0  # Le réseau redevient stable
        succes = True
    else:
        succes = False

    execution_time = time.time() - start_time

    # Retour des KPIs demandés par le Hackathon
    return {
        "remediation_status": "SUCCES" if succes else "FAILED",
        "action_executed": order.action_type,
        "kpis": {
            "mttr_seconds": round(execution_time, 4), # Time to Repair
            "cost_saved_usd": 150.0 if succes else 0, # Estimation d'économie
            "availability_impact": "+0.10%"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
