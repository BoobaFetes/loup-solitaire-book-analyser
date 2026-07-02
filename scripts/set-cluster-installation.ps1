###################################################################################################################
## NOTES: 
## This script has to be run once, after the cluster is created, to install all cluster dependencies
## 
###################################################################################################################

# Requires: powershell-yaml, a tool to convert yaml to json and vice versa.
Install-Module -Name powershell-yaml -Force

Write-Host "`n📥 Installing metrics-server..." -ForegroundColor Cyan
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

Write-Host "`n🔍 Fetching metrics-server deployment..." -ForegroundColor Cyan
$metricServer = kubectl -n kube-system get deployment metrics-server -o yaml | ConvertFrom-Yaml

Write-Host "`n🛠️ Patching metrics-server arguments..." -ForegroundColor Cyan

# Add missing args only if not already present
for ($i = 0; $i -lt $metricServer.spec.template.spec.containers[0].args.Count; $i++) {
    if ($metricServer.spec.template.spec.containers[0].args[$i].StartsWith("--kubelet-preferred-address-types=")) {
        $argsHasChanges = $false
        $values = $metricServer.spec.template.spec.containers[0].args[$i].Split("=")[1].Split(",")
        if ($values -notcontains "InternalIP") {
            $argsHasChanges = $true
            $values += "InternalIP"
        }
        if ($values -notcontains "Hostname") {
            $argsHasChanges = $true
            $values += "Hostname"
        }
        if ($argsHasChanges) {
            $metricServer.spec.template.spec.containers[0].args[$i] = "--kubelet-preferred-address-types=" + ($values -join ",")
        }
        break
    }
}
if ($metricServer.spec.template.spec.containers[0].args -notcontains "--kubelet-insecure-tls") {
    $metricServer.spec.template.spec.containers[0].args += "--kubelet-insecure-tls"
}
if ($metricServer.spec.template.spec.containers[0].args -notcontains "--kubelet-use-node-status-port") {
    $metricServer.spec.template.spec.containers[0].args += "--kubelet-use-node-status-port"
}

Write-Host "`n📤 Applying patched deployment..." -ForegroundColor Cyan
$metricServer | ConvertTo-Yaml | kubectl -n kube-system apply -f -

$maxSeconds = 300   # temps max d'attente (5 minutes)
$interval = 1       # pause entre les essais
$elapsed = 0
$attempt = 0
Write-Host "`n⏳ Waiting for metrics-server to restart (timeout: $maxSeconds s)..." -ForegroundColor Yellow
while ($elapsed -lt $maxSeconds) {
    $output = kubectl top node 2>&1
    if ($output -notmatch "Metrics API not available") {
        Write-Host "`n✅ Metrics Server is ready !"
        break
    }
    $attempt++
    Write-Host -NoNewline "`r❌ Metrics API not available, waiting for $attempt seconds..."
    
    Start-Sleep -Seconds $interval
    $elapsed += $interval
}

if ($elapsed -ge $maxSeconds) {
    Write-Host "`n⛔ Timeout : Metrics Server is still not responding after $maxSeconds seconds."
}

Write-Host "`n📡 Checking APIService availability..." -ForegroundColor Cyan
kubectl get apiservice v1beta1.metrics.k8s.io -o wide

Write-Host "`n📊 Testing metrics..." -ForegroundColor Cyan
Write-Host "`nPS> kubectl top node :`n"
kubectl top node
Write-Host "`n`nPS> kubectl top pod -A :`n"
kubectl top pod -A