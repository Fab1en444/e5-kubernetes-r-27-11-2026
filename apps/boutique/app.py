"""Boutique TechShop - Projet E5 (r-27-11-2026)
Catalogue (MariaDB) + panier (API Panier / Redis) + paiement Stripe (mode test).
"""
import os
import socket
import uuid

import requests
import stripe
from flask import Flask, flash, redirect, render_template, request, session, url_for
from sqlalchemy import bindparam, create_engine, text

POD = socket.gethostname()
PANIER_API = os.getenv("PANIER_API_URL", "http://localhost:8000")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

DATABASE_URL = os.getenv("DATABASE_URL") or "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(
    os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_HOST"),
    os.getenv("DB_PORT", "3306"), os.getenv("DB_NAME"))
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280)

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


@app.context_processor
def variables_globales():
    return {"pod": POD}


@app.template_filter("euros")
def euros(centimes):
    return f"{centimes / 100:.2f} €".replace(".", ",")


def panier_id():
    """Identifiant du panier du visiteur, conservé dans un cookie de session signé."""
    session.setdefault("panier_id", uuid.uuid4().hex)
    return session["panier_id"]


def api_panier(methode, chemin, **kwargs):
    """Appel à l'API Panier (microservice FastAPI)."""
    r = requests.request(methode, f"{PANIER_API}/paniers/{panier_id()}{chemin}", timeout=3, **kwargs)
    r.raise_for_status()
    return r.json() if r.content else None


def contenu_panier():
    articles = api_panier("GET", "")["articles"]
    if not articles:
        return [], 0
    requete = text("SELECT * FROM produits WHERE id IN :ids").bindparams(bindparam("ids", expanding=True))
    with engine.connect() as c:
        produits = {p.id: p for p in c.execute(requete, {"ids": [int(i) for i in articles]})}
    lignes = [{"produit": produits[int(i)], "quantite": q} for i, q in articles.items() if int(i) in produits]
    total = sum(l["produit"].prix_centimes * l["quantite"] for l in lignes)
    return lignes, total


@app.get("/")
def catalogue():
    with engine.connect() as c:
        produits = c.execute(text("SELECT * FROM produits ORDER BY id")).all()
    return render_template("catalogue.html", produits=produits)


@app.post("/ajouter/<int:produit_id>")
def ajouter(produit_id):
    try:
        api_panier("POST", "/articles", json={"produit_id": produit_id, "quantite": 1})
        flash("Article ajouté au panier.")
    except requests.RequestException:
        flash("Service panier indisponible, réessayez.")
    return redirect(url_for("catalogue"))


@app.get("/panier")
def panier():
    lignes, total = contenu_panier()
    return render_template("panier.html", lignes=lignes, total=total)


@app.post("/vider")
def vider():
    api_panier("DELETE", "")
    return redirect(url_for("panier"))


@app.post("/payer")
def payer():
    """Crée une session de paiement Stripe Checkout et redirige le client vers Stripe."""
    lignes, _ = contenu_panier()
    if not lignes:
        return redirect(url_for("panier"))
    paiement = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"quantity": l["quantite"],
                     "price_data": {"currency": "eur", "unit_amount": l["produit"].prix_centimes,
                                    "product_data": {"name": l["produit"].nom}}} for l in lignes],
        success_url=f"{BASE_URL}/succes?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{BASE_URL}/panier",
    )
    return redirect(paiement.url, code=303)


@app.get("/succes")
def succes():
    """Retour de Stripe : on vérifie le paiement auprès de Stripe avant d'enregistrer la commande."""
    paiement = stripe.checkout.Session.retrieve(request.args.get("session_id", ""))
    if paiement.payment_status != "paid":
        flash("Paiement non confirmé.")
        return redirect(url_for("panier"))
    email = paiement.customer_details.email if paiement.customer_details else None
    with engine.begin() as c:
        deja = c.execute(text("SELECT id FROM commandes WHERE stripe_session_id = :s"), {"s": paiement.id}).first()
        if not deja:  # évite les doublons si la page est rechargée
            c.execute(text("INSERT INTO commandes (stripe_session_id, email, montant_centimes) VALUES (:s, :e, :m)"),
                      {"s": paiement.id, "e": email, "m": paiement.amount_total})
    api_panier("DELETE", "")
    flash(f"✅ Paiement de {euros(paiement.amount_total)} confirmé, merci !")
    return redirect(url_for("commandes"))


@app.get("/commandes")
def commandes():
    with engine.connect() as c:
        liste = c.execute(text("SELECT * FROM commandes ORDER BY id DESC LIMIT 20")).all()
    return render_template("commandes.html", commandes=liste)


@app.get("/healthz")
def healthz():
    return {"statut": "ok", "pod": POD}


@app.get("/readyz")
def readyz():
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return {"statut": "pret", "pod": POD}
    except Exception:
        return {"statut": "base injoignable", "pod": POD}, 503
