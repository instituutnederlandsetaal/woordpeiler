git pull | while IFS= read -r line; do printf '[%s git pull] %s\n' "$(date '+%H:%M:%S')" "$line"; done
echo ""
docker compose pull | while IFS= read -r line; do printf '[%s docker compose pull] %s\n' "$(date '+%H:%M:%S')" "$line"; done
echo ""
docker compose up -d | while IFS= read -r line; do printf '[%s docker compose up] %s\n' "$(date '+%H:%M:%S')" "$line"; done
echo ""
yes | docker image prune | while IFS= read -r line; do printf '[%s docker image prune] %s\n' "$(date '+%H:%M:%S')" "$line"; done
echo ""