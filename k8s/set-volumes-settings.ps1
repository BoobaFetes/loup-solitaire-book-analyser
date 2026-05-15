$NODE = "desktop-worker"

Write-Host "Connexion au noeud $NODE..." -ForegroundColor Cyan

# Commandes à exécuter dans le nœud
$commands = @(
    "mkdir -p /mnt/volumes/loup-solitaire-book-analyser/dev/data",
    "mkdir -p /mnt/volumes/loup-solitaire-book-analyser/dev/logs",

    "mkdir -p /mnt/volumes/loup-solitaire-book-analyser/prod/data",
    "mkdir -p /mnt/volumes/loup-solitaire-book-analyser/prod/logs",
    
    "ls -la /mnt/volumes/loup-solitaire-book-analyser"
    "ls -la /mnt/volumes/loup-solitaire-book-analyser/dev"
    "ls -la /mnt/volumes/loup-solitaire-book-analyser/prod"
)

foreach ($cmd in $commands) {
    Write-Host "`n> Exécution : $cmd" -ForegroundColor Yellow
    docker exec -it $NODE bash -c $cmd
}

Write-Host "`nTerminé !" -ForegroundColor Green