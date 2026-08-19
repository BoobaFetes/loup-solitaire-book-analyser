$projectRootDir = "$PSScriptRoot/.."
cd $projectRootDir

& .venv/Scripts/Activate.ps1

python $projectRootDir/src/migrations/bootstrap_roles.py

alembic upgrade head

deactivate