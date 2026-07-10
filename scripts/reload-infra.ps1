param(
    [switch]$Clean
)
$scriptRoot = $PSScriptRoot


write-host "Deleting the local build configuration..." -ForegroundColor Green
k delete -f "$scriptRoot/../k8s/overlays/dev-build.yaml"

write-host "Deleting the local configuration..." -ForegroundColor Green
& "$scriptRoot/clean-local-configuration.ps1"



if (!$Clean.IsPresent) {
    write-host "Recreating the local configuration in the local cluster..." -ForegroundColor Green
    & "$scriptRoot/set-local-configuration.ps1"

    write-host "Building the local build configuration..." -ForegroundColor Green
    kustomize build .\k8s\overlays\dev\ --enable-helm > "$scriptRoot/../k8s/overlays/dev-build.yaml"

    write-host "Recreating the local build configuration..." -ForegroundColor Green
    k apply -f "$scriptRoot/../k8s/overlays/dev-build.yaml"  

    write-host "Port forwarding the database on localhost..." -ForegroundColor Green
    start-sleep -Seconds 10
    & "$scriptRoot/serve-local-database.ps1"
}