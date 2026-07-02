###################################################################################################################
## NOTES: 
## This script has to be run once, after the cluster is created, to install all cluster dependencies
## 
###################################################################################################################

# Requires: powershell-yaml, a tool to convert yaml to json and vice versa.
Install-Module -Name powershell-yaml -Force

Write-Host "📥 Installing metrics-server..." -ForegroundColor Cyan
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

Write-Host "🔍 Fetching metrics-server deployment..." -ForegroundColor Cyan
$metricServer = kubectl -n kube-system get deployment metrics-server -o yaml | ConvertFrom-Yaml

Write-Host "🛠️ Patching metrics-server arguments..." -ForegroundColor Cyan
$metricServerArgs = $metricServer.spec.template.spec.containers[0].args

# Add missing args only if not already present
if ($metricServerArgs -notcontains "--kubelet-insecure-tls") {
    $metricServerArgs += "--kubelet-insecure-tls"
}
if ($metricServerArgs -notcontains "--kubelet-preferred-address-types=InternalIP,Hostname") {
    $metricServerArgs += "--kubelet-preferred-address-types=InternalIP,Hostname"
}
if ($metricServerArgs -notcontains "--kubelet-use-node-status-port") {
    $metricServerArgs += "--kubelet-use-node-status-port"
    
}

Write-Host "📤 Applying patched deployment..." -ForegroundColor Cyan
$metricServer | ConvertTo-Yaml | kubectl -n kube-system apply -f -

Write-Host "⏳ Waiting for metrics-server to restart..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "📡 Checking APIService availability..." -ForegroundColor Cyan
kubectl get apiservice v1beta1.metrics.k8s.io -o wide

Write-Host "📊 Testing metrics..." -ForegroundColor Cyan
kubectl top node
kubectl top pod -A