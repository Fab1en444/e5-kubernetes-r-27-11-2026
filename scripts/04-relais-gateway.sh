#!/bin/bash
# Projet E5 - r-27-11-2026
# Relais du port 8080 de la VM (ouvert uniquement à mon IP par UFW et le pare-feu IONOS)
# vers le Service NodePort du proxy Envoy de la Gateway
NP=$(kubectl get svc -n envoy-gateway-system \
  -l gateway.envoyproxy.io/owning-gateway-name=gateway-r-27-11-2026 \
  -o jsonpath='{.items[0].spec.ports[0].nodePort}')
pkill -f "TCP-LISTEN:8080" 2>/dev/null
nohup socat TCP-LISTEN:8080,fork,reuseaddr TCP:"$(minikube ip)":"$NP" \
  > /tmp/relais-gateway-r-27-11-2026.log 2>&1 &
sleep 1
echo "Relais actif : 8080 -> $(minikube ip):$NP"
ss -tln | grep 8080
