# Ce script permet l'initialisation des volumes dans un cluster local (ex: k3s) en créant les dossiers nécessaires à l'intérieur du volume monté.
# il n'a pas pour but d'être utilisé tel quel dans un environnement de production, mais plutôt de faciliter le développement local.
# POUR RAPPEL : dans un environnement de production, les volumes sont généralement gérés par des solutions de stockage dédiées (ex: NFS, Ceph, etc.) et ne nécessitent pas ce genre d'initialisation manuelle.

# TODO : mettre en place des volumes dans le cloud (AWS ou Azure)

$NODE = "desktop-worker" # à changer en fonction du nom des nœuds de votre cluster local

Write-Host "Connexion au noeud $NODE..." -ForegroundColor Cyan

# Commandes à exécuter dans le nœud
$commands = @()

# creation des repertoires et sous-repertoires
$dir = "/mnt/volumes/lsba"
$subDirs = (    
    "$dir/dev/data", 
    "$dir/dev/logs", 
    "$dir/dev/postgresql", 
    "$dir/stg/data", 
    "$dir/stg/logs", 
    "$dir/stg/postgresql",
    "$dir/prod/data", 
    "$dir/prod/logs", 
    "$dir/prod/postgresql"
)

$commands += "mkdir -p $dir"
$commands += "cd $dir"
$commands += "mkdir -p $($subDirs -join ' ')"

# creation des groupes et des utilisateurs

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
    $groupscmd += "groupadd -g $($group.gid) $($group.name);"
}
$commands += $groupscmd
$commands += "getent group | grep lsba"

$persmissions = @(
    @{ index = 0; owner = "root"; gid = 4000; mode = "2770" },
    @{ index = 1; owner = "root"; gid = 4000; mode = "2770" },
    @{ index = 2; owner = "root"; gid = 4001; mode = "2770" },
    @{ index = 3; owner = "root"; gid = 4100; mode = "2770" },
    @{ index = 4; owner = "root"; gid = 4100; mode = "2770" },
    @{ index = 5; owner = "root"; gid = 4101; mode = "2770" },
    @{ index = 6; owner = "root"; gid = 4200; mode = "2770" },
    @{ index = 7; owner = "root"; gid = 4200; mode = "2770" },
    @{ index = 8; owner = "root"; gid = 4201; mode = "2770" }
)
$chowncmd = ""
$chmodcmd = ""
foreach ($permission in $persmissions) {
    $chowncmd += "chown $($permission.owner):$($permission.gid) $($subDirs[$permission.index]);"
    $chmodcmd += "chmod $($permission.mode) $($subDirs[$permission.index]);"
}
$commands += $chowncmd
$commands += $chmodcmd

$commands += 'cd /'
$commands += "ls -la $dir/**/**"
    


foreach ($cmd in $commands) {
    Write-Host "`n> Exécution : $cmd" -ForegroundColor Yellow
    docker exec -it $NODE bash -c $cmd
}

Write-Host "`nTerminé !" -ForegroundColor Green