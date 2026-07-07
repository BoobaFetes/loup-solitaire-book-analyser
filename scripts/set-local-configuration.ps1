# This script initializes volumes in a local cluster (e.g., k3s) by creating the necessary directories inside the mounted volume.
# It is not intended to be used as-is in a production environment, but rather to facilitate local development.
# REMINDER: In a production environment, volumes are typically managed by dedicated storage solutions (e.g., NFS, Ceph, etc.) and do not require this kind of manual initialization.

$NODES = @("desktop-worker", "desktop-worker2") # change according to the name of the nodes in your local cluster


# arrange
$commands = @()

# create directories and subdirectories
$dir = "/mnt/lsba"
$subDirs = (    
    "$dir/dev/data", 
    "$dir/dev/logs", 
    "$dir/dev/postgresql" 
    # not used in dev environment "$dir/stg/data", 
    # not used in dev environment "$dir/stg/logs", 
    # not used in dev environment "$dir/stg/postgresql",
    # not used in dev environment "$dir/prod/data", 
    # not used in dev environment "$dir/prod/logs", 
    # not used in dev environment "$dir/prod/postgresql"
)

$commands += "mkdir -p $dir"
$commands += "cd $dir"
$commands += "mkdir -p $($subDirs -join ' ')"

# create groups

$groups = @(
    @{ gid = 4001; name = "lsba-dev-app" },
    @{ gid = 4002; name = "lsba-dev-data" }
)
$groupscmd = ""
foreach ($group in $groups) {
    $groupscmd += "groupadd -g $($group.gid) $($group.name);"
}
$commands += $groupscmd
$commands += "getent group | grep lsba"

# create permissions for k8s hostpath volumes

$persmissions = @(
    @{ index = 0; owner = "root"; gid = 4001; mode = "2770" },
    @{ index = 1; owner = "root"; gid = 4001; mode = "2770" },
    @{ index = 2; owner = "root"; gid = 4002; mode = "2770" }
    # not used in dev environment @{ index = 3; owner = "root"; gid = 4100; mode = "2770" },
    # not used in dev environment @{ index = 4; owner = "root"; gid = 4100; mode = "2770" },
    # not used in dev environment @{ index = 5; owner = "root"; gid = 4101; mode = "2770" },
    # not used in dev environment @{ index = 6; owner = "root"; gid = 4200; mode = "2770" },
    # not used in dev environment @{ index = 7; owner = "root"; gid = 4200; mode = "2770" },
    # not used in dev environment @{ index = 8; owner = "root"; gid = 4201; mode = "2770" }
)
$chowncmd = ""
$chmodcmd = ""
foreach ($permission in $persmissions) {
    $chowncmd += "chown $($permission.owner):$($permission.gid) $($subDirs[$permission.index]);"
    $chmodcmd += "chmod $($permission.mode) $($subDirs[$permission.index]);"
}
$commands += $chowncmd
$commands += $chmodcmd

# show permissions and groups of each directory

$commands += 'cd /'
$commands += "ls -la $dir/**/**"
    
# executes commands in the worker node

foreach ($node in $NODES) {
    Write-Host "`nConnecting to node $node..." -ForegroundColor Cyan
    foreach ($cmd in $commands) {
        Write-Host "> Executing: $cmd" -ForegroundColor Yellow
        docker exec -it $node bash -c $cmd
    }
}

Write-Host "Finished !" -ForegroundColor Green