"""API Panier - Projet E5 (r-27-11-2026)
Microservice qui stocke les paniers des clients dans Redis (clé/valeur avec expiration).
"""
import os
import socket

import redis
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
PANIER_TTL = int(os.getenv("PANIER_TTL_SECONDES", "86400"))
POD = socket.gethostname()

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD,
                decode_responses=True, socket_timeout=2, socket_connect_timeout=2)

app = FastAPI(title="API Panier - E5 r-27-11-2026",
              description="Gestion des paniers de la boutique (stockage Redis).",
              version="1.0.0")


class Article(BaseModel):
    produit_id: int = Field(gt=0)
    quantite: int = Field(default=1, gt=0, le=99)


def cle(panier_id: str) -> str:
    if not panier_id.isalnum() or len(panier_id) > 64:
        raise HTTPException(status_code=400, detail="identifiant de panier invalide")
    return f"panier:{panier_id}"


@app.middleware("http")
async def entete_pod(request, call_next):
    reponse = await call_next(request)
    reponse.headers["X-Pod"] = POD
    return reponse


@app.get("/healthz", tags=["sante"])
def healthz():
    return {"statut": "ok", "pod": POD}


@app.get("/readyz", tags=["sante"])
def readyz(response: Response):
    try:
        r.ping()
        return {"statut": "pret", "redis": "ok", "pod": POD}
    except redis.RedisError:
        response.status_code = 503
        return {"statut": "indisponible", "redis": "injoignable", "pod": POD}


@app.get("/paniers/{panier_id}", tags=["paniers"])
def lire_panier(panier_id: str):
    articles = r.hgetall(cle(panier_id))
    return {"panier_id": panier_id,
            "articles": {int(k): int(v) for k, v in articles.items()},
            "pod": POD}


@app.post("/paniers/{panier_id}/articles", tags=["paniers"], status_code=201)
def ajouter_article(panier_id: str, article: Article):
    k = cle(panier_id)
    pipe = r.pipeline()
    pipe.hincrby(k, str(article.produit_id), article.quantite)
    pipe.expire(k, PANIER_TTL)
    pipe.execute()
    return lire_panier(panier_id)


@app.delete("/paniers/{panier_id}/articles/{produit_id}", tags=["paniers"])
def retirer_article(panier_id: str, produit_id: int):
    r.hdel(cle(panier_id), str(produit_id))
    return lire_panier(panier_id)


@app.delete("/paniers/{panier_id}", tags=["paniers"], status_code=204)
def vider_panier(panier_id: str):
    r.delete(cle(panier_id))
    return Response(status_code=204)
