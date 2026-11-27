# Erreurs rencontrées

Chaque erreur est documentée avec : objectif recherché, commande, erreur affichée, logs, résolution.

---

## Erreur 1 - `swapon: command not found`
- **Objectif** : vérifier que le swap de 4 Go est bien actif.
- **Commande** : `swapon --show`
- **Erreur** : `-bash: swapon: command not found`
- **Cause** : `swapon` est un binaire d'administration situé dans `/sbin`, qui n'est pas dans le PATH d'un utilisateur non-root sous Debian.
- **Résolution** : exécuter la commande avec les droits root : `sudo swapon --show`.

---

## Erreur 2 - `kubectl: command not found` dans un script

- **Objectif** : créer les Secrets avec le script `02-secrets.sh`.
- **Commande** : `./scripts/02-secrets.sh`
- **Erreur** : `kubectl: command not found`
- **Cause** : `kubectl` était un alias vers `minikube kubectl`, et les alias ne fonctionnent pas dans les scripts.
- **Résolution** : installation du binaire officiel kubectl v1.37.0 (vérifié avec sha256) et suppression de l'alias dans `~/.bashrc`.

---

## Erreur 3 - Conflit de port pendant le test de la boutique

- **Objectif** : tester la boutique depuis la VM avec un port-forward.
- **Commande** : `kubectl port-forward -n ecommerce-r-27-11-2026 svc/boutique-r-27-11-2026 5000:80`
- **Erreur** : pages vides puis erreur 404 sur `/payer`.
- **Cause** : le port 5000 était déjà utilisé par le relais vers le registry, donc les requêtes arrivaient au registry et pas à la boutique.
- **Résolution** : utilisation d'un autre port libre (5050).

---

## Erreur 4 - Clé Stripe affichée par erreur

- **Objectif** : enregistrer les clés Stripe dans un Secret sans les afficher.
- **Commande** : `read -rsp "Clé secrète Stripe (sk_test_...) : " SK`
- **Erreur** : la clé a été collée dans la commande au lieu d'être collée après, elle était donc visible à l'écran et dans l'historique.
- **Cause** : erreur de manipulation au copier-coller.
- **Résolution** : rotation de la clé dans le dashboard Stripe (l'ancienne ne fonctionne plus), suppression de la ligne dans l'historique (`history -d` puis `history -w`), puis nouvelle saisie.
