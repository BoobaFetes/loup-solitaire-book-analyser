# Utilisation De PostgreSQL

> ce quide peut etre obsolète ou contenir des erreurs, il est présent surtout pour les developpeurs junior pour les aider à comprendre comment utiliser PostgreSQL avec l'application. Il est recommandé de se référer à la documentation officielle de PostgreSQL et aux guides de l'équipe de développement pour des informations à jour.

Ce guide explique comment initialiser les utilisateurs de base de donnees,
executer les migrations Alembic, lancer l'exemple local SQLAlchemy, puis
verifier le resultat dans PostgreSQL.

Toutes les commandes sont a lancer depuis la racine du repository.

## 1. Exposer La Base Locale

Demarrer le port-forward PostgreSQL :

```powershell
& .\scripts\serve-local-database.ps1
```

Garder ce terminal ouvert. Il expose PostgreSQL sur `localhost:5432`.

## 2. Initialiser Les Utilisateurs Applicatifs

Dans un autre terminal PowerShell, lancer :

```powershell
.\.venv\Scripts\python.exe src\migrations\bootstrap_roles.py
```

Cette commande execute `for-devops-temp/init-db.sql` avec
`CONNECTION_STRING_ADMIN`.

Le script cree ou met a jour :

- `db_batch_usr`
- `db_webapp_usr`

Il donne aussi les droits de connexion a la base et d'utilisation du schema.

## 3. Executer Les Migrations Alembic

Lancer :

```powershell
.\.venv\Scripts\python.exe -m alembic -c src\migrations\alembic.ini upgrade head
```

Cette commande applique toutes les migrations de base de donnees, notamment :

- les permissions par defaut pour les futurs objets crees par `db_migration_usr`
- la creation de la table `db_probe` utilisee par `src/main.py`

## 4. Lancer L'Exemple SQLAlchemy

Lancer :

```powershell
.\.venv\Scripts\python.exe src\main.py
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

## 5. Verifier La Base De Donnees

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

## Resume Des Commandes

```powershell
.\.venv\Scripts\python.exe src\migrations\bootstrap_roles.py
.\.venv\Scripts\python.exe -m alembic -c src\migrations\alembic.ini upgrade head
.\.venv\Scripts\python.exe src\main.py
```

Responsabilites :

- `bootstrap_roles.py` : etape admin/devops pour les utilisateurs de base
- `alembic upgrade head` : etape de migration du schema
- `src/main.py` : exemple runtime applicatif avec SQLAlchemy
