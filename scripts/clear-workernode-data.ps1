write-host "files before:"
docker exec -it desktop-worker sh -c "ls ./mnt/lsba/**/**/*"

write-host "deleting files..."
docker exec -it desktop-worker sh -c "rm ./mnt/lsba/**/**/*"

write-host "files after:"
docker exec -it desktop-worker sh -c "ls ./mnt/lsba/**/**/*"