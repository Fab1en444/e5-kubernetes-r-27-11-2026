#!/bin/bash
# Projet E5 - r-27-11-2026
# Création du cluster Minikube du projet
set -e

PROFILE=cluster-r-27-11-2026

# Cluster mono-nœud, limité à 2,5 Go de RAM (la VM héberge aussi d'autres services)
# CNI Calico : nécessaire pour que les NetworkPolicy soient appliquées
minikube start -p "$PROFILE" \
  --driver=docker \
  --kubernetes-version=v1.37.0 \
  --cpus=4 \
  --memory=2560 \
  --cni=calico

# Ce profil devient le profil par défaut des commandes minikube
minikube profile "$PROFILE"

# Addons : métriques (HPA, kubectl top) et registry d'images interne
minikube addons enable metrics-server -p "$PROFILE"
minikube addons enable registry -p "$PROFILE"
