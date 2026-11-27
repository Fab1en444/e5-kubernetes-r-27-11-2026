# Erreurs rencontrées

Chaque erreur est documentée avec : objectif recherché, commande, erreur affichée, logs, résolution.

---

## Erreur 1 - `swapon: command not found`
- **Objectif** : vérifier que le swap de 4 Go est bien actif.
- **Commande** : `swapon --show`
- **Erreur** : `-bash: swapon: command not found`
- **Cause** : `swapon` est un binaire d'administration situé dans `/sbin`, qui n'est pas dans le PATH d'un utilisateur non-root sous Debian.
- **Résolution** : exécuter la commande avec les droits root : `sudo swapon --show`.
