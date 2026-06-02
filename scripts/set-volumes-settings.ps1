# Ce script permet l'initialisation des volumes dans un cluster local (ex: k3s) en créant les dossiers nécessaires à l'intérieur du volume monté.
# il n'a pas pour but d'être utilisé tel quel dans un environnement de production, mais plutôt de faciliter le développement local.
# POUR RAPPEL : dans un environnement de production, les volumes sont généralement gérés par des solutions de stockage dédiées (ex: NFS, Ceph, etc.) et ne nécessitent pas ce genre d'initialisation manuelle.

# TODO : mettre en place des volumes dans le cloud (AWS ou Azure)

$NODE = "desktop-worker" # à changer en fonction du nom des nœuds de votre cluster local

Write-Host "Connexion au noeud $NODE..." -ForegroundColor Cyan

# Commandes à exécuter dans le nœud
$commands = @(
    "mkdir -p /mnt/volumes/lsba/dev/data",
    "mkdir -p /mnt/volumes/lsba/dev/logs",

    "mkdir -p /mnt/volumes/lsba/prod/data",
    "mkdir -p /mnt/volumes/lsba/prod/logs",
    
    "ls -la /mnt/volumes/lsba",
    "ls -la /mnt/volumes/lsba/dev",
    "ls -la /mnt/volumes/lsba/prod"
)

foreach ($cmd in $commands) {
    Write-Host "`n> Exécution : $cmd" -ForegroundColor Yellow
    docker exec -it $NODE bash -c $cmd
}

Write-Host "`nTerminé !" -ForegroundColor Green