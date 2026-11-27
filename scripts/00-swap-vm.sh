#!/bin/bash
# Projet E5 - r-27-11-2026
# Ajout d'un swap de 4 Go pour sécuriser la mémoire de la VM (3,8 Go de RAM)
set -e

SWAPFILE=/swapfile-r-27-11-2026

fallocate -l 4G "$SWAPFILE"
chmod 600 "$SWAPFILE"
mkswap "$SWAPFILE"
swapon "$SWAPFILE"

# Activation permanente au redémarrage
grep -q "$SWAPFILE" /etc/fstab || echo "$SWAPFILE none swap sw 0 0" >> /etc/fstab

# Le swap n'est utilisé qu'en dernier recours (la RAM reste prioritaire)
echo "vm.swappiness=10" > /etc/sysctl.d/99-swap-r-27-11-2026.conf
sysctl -p /etc/sysctl.d/99-swap-r-27-11-2026.conf
