# This script cleans up the local configuration in a local cluster (e.g., k3s) by removing the directories and groups created for development purposes.
# It is not intended to be used as-is in a production environment, but rather to facilitate local development.
# REMINDER: In a production environment, volumes and groups are typically managed by dedicated storage solutions (e.g., NFS, Ceph, etc.) and do not require this kind of manual cleanup.

# TODO: clean up volumes in the cloud (AWS or Azure)

$NODE = "desktop-worker" # change according to the name of the nodes in your local cluster

Write-Host "Connecting to node $NODE..." -ForegroundColor Cyan

# arrange
$commands = @()

# delete directories and subdirectories

$commands += 'rm -rf /mnt/volumes/lsba'

# delete groups

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

# executes commands in the worker node

foreach ($cmd in $commands) {
    Write-Host "`n> Executing: $cmd" -ForegroundColor Yellow
    docker exec -it $NODE bash -c $cmd
}

Write-Host "Finished !" -ForegroundColor Green