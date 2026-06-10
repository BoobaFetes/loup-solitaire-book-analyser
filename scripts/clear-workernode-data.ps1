write-host "files before:"
docker exec -it desktop-worker sh -c "ls ./mnt/volumes/lsba/**/**/*"

write-host "deleting files..."
docker exec -it desktop-worker sh -c "rm ./mnt/volumes/lsba/**/**/*"

write-host "files after:"
docker exec -it desktop-worker sh -c "ls ./mnt/volumes/lsba/**/**/*"