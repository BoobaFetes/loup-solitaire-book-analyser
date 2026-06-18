#arguments
param(
    [string]$image = "loup-solitaire-book-analyser",
    [string]$tag = "v0.1.3"
)
$rootPath = "$psscriptroot/.."

# script permettant de construire une nouvelle image Docker à partir du Dockerfile situé à la racine du projet, en utilisant les arguments spécifiés pour le nom de l'image et le tag. 
# Après la construction, il affiche la liste des images Docker filtrée par le nom de l'image pour vérifier que l'image a été créée avec succès.

# CE SCRIPT EST UN AIDE MEMOIRE, OU UNE FACILITE POUR LES DEVELOPPEMENTS LOCAUX ET NE DOIT PAS ETRE UTILISE TEL QUEL DANS UN ENVIRONNEMENT DE PRODUCTION.
# En effet, dans un environnement de production, la construction et le déploiement des images Docker sont généralement gérés par des pipelines CI/CD (ex: GitHub Actions, Jenkins, GitLab CI, etc.) et ne nécessitent pas ce genre de script manuel.

$imageTag = "$($image):$tag"
docker build -t $imageTag -f "$rootPath/Dockerfile" $rootPath
write-host "Image $imageTag built successfully."


docker image ls --filter "reference=$image"