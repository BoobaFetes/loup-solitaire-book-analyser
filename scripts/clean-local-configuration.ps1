# Ce script permet l'initialisation des volumes dans un cluster local (ex: k3s) en créant les dossiers nécessaires à l'intérieur du volume monté.
# il n'a pas pour but d'être utilisé tel quel dans un environnement de production, mais plutôt de faciliter le développement local.
# POUR RAPPEL : dans un environnement de production, les volumes sont généralement gérés par des solutions de stockage dédiées (ex: NFS, Ceph, etc.) et ne nécessitent pas ce genre d'initialisation manuelle.

# TODO : mettre en place des volumes dans le cloud (AWS ou Azure)

$NODE = "desktop-worker" # à changer en fonction du nom des nœuds de votre cluster local

Write-Host "Connexion au noeud $NODE..." -ForegroundColor Cyan

# Commandes à exécuter dans le nœud
$commands = @(
    'rm -rf /mnt/volumes/lsba'
)
$groups = @(
    @{ gid = 4000; name = "lsba-dev-app" },
    @{ gid = 4001; name = "lsba-dev-data" },
    @{ gid = 4100; name = "lsba-stg-app" },
    @{ gid = 4101; name = "lsba-stg-data" },
    @{ gid = 4200; name = "lsba-prod-app" },
    @{ gid = 4201; name = "lsba-prod-data" }
)
$groupscmd = ""
foreach ($group in $groups) {
    $groupscmd += "groupdel $($group.name);"
}
$commands += $groupscmd
$commands += "getent group | grep lsba"

foreach ($cmd in $commands) {
    Write-Host "`n> Exécution : $cmd" -ForegroundColor Yellow
    docker exec -it $NODE bash -c $cmd
}

Write-Host "`nTerminé !" -ForegroundColor Green