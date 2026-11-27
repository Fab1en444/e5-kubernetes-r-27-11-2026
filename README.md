# Projet E5 - Virtual Datacenter Automation (Kubernetes)

**Auteur :** Fabien RIVAS (projet réalisé seul) - ESTIAM Tarbes
**Empreinte :** `r-27-11-2026`

## Objectif
MVP e-commerce hautement disponible et résilient sur Kubernetes (Minikube),
composé de 3 applications prod-ready, dont une boutique avec paiement Stripe (mode test).

## Arborescence
- `apps/` : code source et Dockerfiles des applications
- `k8s/` : manifests Kubernetes (un fichier par ressource)
- `docs/` : rapport, schéma d'architecture
- `logs/` : historique des commandes et logs des frameworks
- `ERREURS.md` : erreurs rencontrées et résolutions
- `secrets/` : valeurs sensibles **(exclu du dépôt)**
