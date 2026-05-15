#arguments
param(
    [string]$image = "loup-solitaire-book-analyser",
    [string]$tag = "v1.0.3"
)
$rootPath = "$psscriptroot/.."
$tags = @($tag, "latest")
foreach ($t in $tags) {
    $imageTag = "$($image):$t"
    docker build -t $imageTag -f "$rootPath/Dockerfile" $rootPath
    write-host "Image $imageTag built successfully."
}

docker image ls --filter "reference=$image"