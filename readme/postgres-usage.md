# Utilisation De PostgreSQL

> ce quide peut etre obsolète ou contenir des erreurs, il est présent surtout pour les developpeurs junior pour les aider à comprendre comment utiliser PostgreSQL avec l'application. Il est recommandé de se référer à la documentation officielle de PostgreSQL et aux guides de l'équipe de développement pour des informations à jour.

Ce guide explique comment initialiser les utilisateurs de base de donnees,
executer les migrations Alembic, lancer l'exemple local SQLAlchemy, puis
verifier le resultat dans PostgreSQL.

Toutes les commandes sont a lancer depuis la racine du repository en **ayant activé le virtualenv** (cad : `./venv/Scripts/activate.ps1`).

## Resume Des Commandes

```powershell
python src/migrations/bootstrap_roles.py
alembic revision -m "describe database change"
alembic upgrade head
alembic downgrade -1
python src/main.py
```

## 1. Exposer La Base Locale

Demarrer le port-forward PostgreSQL :

```powershell
& ./scripts/serve-local-database.ps1
```

Garder ce terminal ouvert. Il expose PostgreSQL sur `localhost:5432`.

## 2. Initialiser Les Utilisateurs Applicatifs

Dans un autre terminal PowerShell, lancer :

```powershell
python src/migrations/bootstrap_roles.py
```

Cette commande execute `./init-db.sql` avec `CONNECTION_STRING_ADMIN`.

Le script cree ou met a jour :

- `db_batch_usr`
- `db_webapp_usr`

Il donne aussi les droits de connexion a la base et d'utilisation du schema.

## 3. Ajouter Une Migration Alembic

Creer une nouvelle migration :

```powershell
alembic revision -m "describe database change"
```

Alembic cree un nouveau fichier dans `src/migrations/versions/`.
Le fichier doit toujours contenir :

- un `upgrade()` qui applique la modification
- un `downgrade()` qui annule la modification
- une revision lisible et chainee avec la revision precedente

Exemple de migration avec ajout d'une colonne, creation d'une table et
suppression d'une colonne :

```python
"""example book model update

Revision ID: 003
Revises: 002
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "db_probe",
        sa.Column("source", sa.String(length=80), nullable=True),
    )

    op.create_table(
        "book_import",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.drop_column("db_probe", "message")


def downgrade() -> None:
    op.add_column(
        "db_probe",
        sa.Column("message", sa.String(length=200), nullable=True),
    )
    op.drop_table("book_import")
    op.drop_column("db_probe", "source")
```

Process de validation local :

1. Verifier que le port-forward PostgreSQL est actif.

   ```powershell
   & ./scripts/serve-local-database.ps1
   ```

2. Appliquer la migration.

   ```powershell
   alembic upgrade head
   ```

3. Verifier le schema dans PostgreSQL.

   ```powershell
   kubectl exec -it -n lsba-ns-dev lsba-db-postgresql-dev-0 -- psql -U db_migration_usr -d lsba_db
   ```

   ```sql
   \dt
   \d db_probe
   \d book_import
   SELECT * FROM alembic_version;
   ```

4. Tester le rollback.

   ```powershell
   alembic downgrade -1
   ```

5. Revenir a la derniere revision.

   ```powershell
   alembic upgrade head
   ```

Si les entites SQLAlchemy sont deja a jour, il est possible de generer une
base de migration avec `--autogenerate`, mais le resultat doit toujours etre
relu et corrige avant execution :

```powershell
alembic revision --autogenerate -m "describe database change"
```

## 4. Executer Les Migrations Alembic

Lancer :

```powershell
alembic upgrade head
```

Cette commande applique toutes les migrations de base de donnees, notamment :

- les permissions par defaut pour les futurs objets crees par `db_migration_usr`
- la creation de la table `db_probe` utilisee par `src/main.py`

## 5. Lancer L'Exemple SQLAlchemy

Lancer :

```powershell
python src/main.py
```

Le script doit :

- tester l'acces en ecriture au dossier monte `logs`
- se connecter avec `CONNECTION_STRING_BATCH`
- inserer une ligne dans `db_probe`
- lire le nombre total de lignes dans `db_probe`

La sortie attendue contient quelque chose comme :

```text
connexion base de données OK : db_probe id=1, total=1
```

## 6. Verifier La Base De Donnees

Se connecter a PostgreSQL avec l'utilisateur de migration :

```powershell
kubectl exec -it -n lsba-ns-dev lsba-db-postgresql-dev-0 -- psql -U db_migration_usr -d lsba_db
```

Lister les tables :

```sql
\dt
```

Les tables attendues incluent :

- `alembic_version`
- `db_probe`

Verifier la revision Alembic courante :

```sql
SELECT * FROM alembic_version;
```

Revision attendue :

```text
002
```

Verifier les lignes inserees par `src/main.py` :

```sql
SELECT id, message, created_at
FROM db_probe
ORDER BY id DESC
LIMIT 10;
```

Message attendu :

```text
test de connexion depuis main.py
```

Lister les roles de base de donnees :

```sql
\du
```

Les roles attendus incluent :

- `db_migration_usr`
- `db_batch_usr`
- `db_webapp_usr`

Responsabilites :

- `bootstrap_roles.py` : etape admin/devops pour les utilisateurs de base
- `alembic revision` : creation d'un fichier de migration
- `alembic upgrade head` : etape de migration du schema
- `alembic downgrade -1` : validation du rollback de la derniere migration
- `src/main.py` : exemple runtime applicatif avec SQLAlchemy
