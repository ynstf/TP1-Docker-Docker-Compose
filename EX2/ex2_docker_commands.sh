# Exercice 2 – Fonctionnalités avancées de Docker
# Durée estimée : 35 minutes
# Author: Atif Youness

# 1. Run an Ubuntu container in interactive mode
docker run -it --name ubuntu-test ubuntu

# 2. Inside the container: install curl and vim
apt update
apt install -y curl vim

# 3. Create a file test.txt with content
echo "Ceci est un test Docker." > test.txt
cat test.txt

# 4. Detach from container without stopping it (Ctrl+P, Ctrl+Q)
# (no command here, manual key combination)

# 5. Copy test.txt from container to host
docker cp ubuntu-test:/test.txt .

# 6. Modify file on host and copy it back to container
echo "Ajout depuis la machine hôte." >> test.txt
docker cp test.txt ubuntu-test:/test.txt

# 7. Reconnect to container and check modifications
docker exec -it ubuntu-test bash
cat /test.txt
curl --version
vim --version
exit

# 8. Create a new image from the modified container
docker commit ubuntu-test ubuntu-custom:v1

# 9. Launch a new container based on the custom image
docker run -it --name ubuntu-custom-test ubuntu-custom:v1

# 10. Verify the modifications inside the new container
cat /test.txt
curl --version
vim --version
exit

# BONUS: View real-time resource usage
docker stats

# Optional cleanup (if needed)
docker stop ubuntu-test ubuntu-custom-test
docker rm ubuntu-test ubuntu-custom-test
docker image prune -a -f
docker container prune -f
