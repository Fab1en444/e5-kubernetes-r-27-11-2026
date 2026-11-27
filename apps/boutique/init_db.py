"""Initialisation de la base de la boutique (lancé par un Job Kubernetes).
Crée les tables et le catalogue de démonstration. Peut être relancé sans risque.
"""
from sqlalchemy import text

from app import engine

PRODUITS = [
    ("Clavier mécanique", "Switches tactiles, rétroéclairage RGB", 8990, "⌨️"),
    ("Souris sans fil", "Capteur haute précision, 70 h d'autonomie", 4990, "🖱️"),
    ("Écran 27 pouces", "QHD 165 Hz, dalle IPS", 27900, "🖥️"),
    ("Casque audio", "Réduction de bruit active", 12900, "🎧"),
]

with engine.begin() as c:
    c.execute(text("""CREATE TABLE IF NOT EXISTS produits (
        id INT AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(100) NOT NULL,
        description VARCHAR(255) NOT NULL, prix_centimes INT NOT NULL, emoji VARCHAR(16) NOT NULL)"""))
    c.execute(text("""CREATE TABLE IF NOT EXISTS commandes (
        id INT AUTO_INCREMENT PRIMARY KEY, stripe_session_id VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255), montant_centimes INT NOT NULL, cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""))
    if c.execute(text("SELECT COUNT(*) FROM produits")).scalar() == 0:
        for nom, description, prix, emoji in PRODUITS:
            c.execute(text("INSERT INTO produits (nom, description, prix_centimes, emoji) VALUES (:n, :d, :p, :e)"),
                      {"n": nom, "d": description, "p": prix, "e": emoji})
print("Base de la boutique initialisée.")
