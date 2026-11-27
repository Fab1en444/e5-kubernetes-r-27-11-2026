#!/bin/bash
# Projet E5 - r-27-11-2026
# Relais local (127.0.0.1:5000, non exposé sur Internet) vers le registry interne de minikube
if pgrep -f "TCP-LISTEN:5000" > /dev/null; then
  echo "Relais registry déjà actif"
else
  nohup socat TCP-LISTEN:5000,bind=127.0.0.1,reuseaddr,fork TCP:"$(minikube ip)":5000 \
    > /tmp/relais-registry-r-27-11-2026.log 2>&1 &
  sleep 2
fi
curl -s http://localhost:5000/v2/_catalog; echo
