#!/bin/bash
# Projet E5 - r-27-11-2026
# Génère les valeurs sensibles (si absentes) dans secrets/ (exclu de git),
# puis crée ou met à jour un Secret Kubernetes pour chaque fichier secrets/*.env
set -e

NS=ecommerce-r-27-11-2026
cd "$(dirname "$0")/.."
mkdir -p secrets

gen() { openssl rand -hex 16; }

[ -f secrets/mariadb-root.env ] || echo "MARIADB_ROOT_PASSWORD=$(gen)" > secrets/mariadb-root.env
[ -f secrets/shop-db.env ] || printf "DB_NAME=shop_db\nDB_USER=shop_user\nDB_PASSWORD=%s\n" "$(gen)" > secrets/shop-db.env
[ -f secrets/backoffice-db.env ] || printf "DB_NAME=backoffice_db\nDB_USER=backoffice_user\nDB_PASSWORD=%s\n" "$(gen)" > secrets/backoffice-db.env
[ -f secrets/redis.env ] || echo "REDIS_PASSWORD=$(gen)" > secrets/redis.env
chmod 600 secrets/*.env

for f in secrets/*.env; do
  s=$(basename "$f" .env)
  kubectl create secret generic "${s}-secret-r-27-11-2026" -n "$NS" \
    --from-env-file="$f" --dry-run=client -o yaml | kubectl apply -f -
done
