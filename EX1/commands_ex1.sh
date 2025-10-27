#!/bin/bash
# -----------------------------------------------------
# Exercice 1 - Découverte de Docker
# Auteur : Atif Youness
# Master SDIA - Docker Basics
# -----------------------------------------------------

# 1. Vérifier que Docker est installé et en cours d’exécution
docker --version
docker info

# 2. Exécuter le conteneur hello-world
docker run hello-world

# 3. Télécharger l’image nginx:alpine sans la lancer
docker pull nginx:alpine

# 4. Lister toutes les images présentes sur le système
docker images

# 5. Lancer un conteneur nginx en arrière-plan sur le port 8080
docker run -d -p 8080:80 --name mynginx nginx:alpine

# 6. Vérifier dans le navigateur : http://localhost:8080
# (aucune commande, juste une vérification manuelle)

# 7. Afficher les logs du conteneur nginx
docker logs mynginx

# 8. Lister tous les conteneurs (en cours et arrêtés)
docker ps -a

# 9. Arrêter et supprimer le conteneur nginx
docker stop mynginx
docker rm mynginx

# 10. Nettoyer les images inutilisées
docker image prune -a
