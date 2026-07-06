# loup-solitaire-book-analyser Project

## 1. Overview

loup-solitaire-book-analyser is a Python application designed to download a list of books from a specified URL with these prices. The application is structured using a clean architecture approach, separating concerns into different components such as ports, adapters and use cases.

## 2. Project Structure

```text
loup-solitaire-book-analyser
├── .github\workflows         # GitHub Actions workflows for CI/CD pipelines
├── k8s                       # Directory for Kubernetes manifests and configurations
├── scripts                   # Directory for utility scripts for development, deployment, and maintenance (powershell only for now, but we can add cross OS scripts if needed)
├── src
│   ├── main.py               # Main entry point for testing and development
│   ├── find_books.py         # Main entry point to find books and their details with kubernetes
│   ├── find_prices.py        # Main entry point to find book prices with kubernetes
│   ├── adapters
│   │   └── __init__.py       # Adapter classes for file system, http fetching, and logging, etc.
│   ├── domain
│   │   └── __init__.py       # Domain models and entities
│   ├── ports
│   │   └── __init__.py       # Port interfaces for communication between layers
│   └── usecases
│       └── __init__.py       # Business logic for managing tomes
├── data                      # Directory for data storage (like html files representing books and their prices, used to update unit tests)
├── logs                      # Directory for log files
├── postgresql                # Directory for persisted data with PostgreSQL
├── Dockerfile                # Dockerfile for containerizing the application
├── .dockerignore             # Files and directories to ignore in Docker builds
├── requirements.txt          # Python dependencies for the application
├── README.md                 # Documentation for the project
├── README-security.md        # Kubernetes security model and volume permissions
└── todo.md                   # TODO list for the project, or tasks that remain to be completed
```

> Note:
>
> The application has code checking, unit tests and coverage for CI/CD pipelines that ensure code quality and reliability.
> We are using best practices that can break the automatic build if issues are detected.

## 3. Prerequisites

- Python 3.14 or higher
- Docker (for containerization)
- Docker-desktop or Minikube (for Kubernetes testing and deployment)

## 4. Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd loup-solitaire-book-analyser
   ```

2. Create a virtual environment (.venv):

   ```bash
   py -m venv .venv  
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     ./.venv/Scripts/activate
     ```

   - On Unix or MacOS:

     ```bash
     source .venv/bin/activate
     ```

   - Remember: to deactivate the virtual environment, simply run:

     ```bash
     (.venv) PS > deactivate
     ```

4. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Using Playwright, we have to install the browser that will be used:

   ```bash
   playwright install chromium
   ```
  
6. Install desktop-docker and launch it.

7. Execute the following command to finalize setup on your local machine:

   ```bash
   & ./scripts/set-local-configuration.ps1
   ```

8. Build the manifest files on your local cluster (desktop-docker or minikube):

   ```bash
    kustomize build ./k8s/overlays/dev/ --enable-helm | kubectl apply -f -
   ```

---

## 5. Running the Application

### for CI/CD

We assume that we always use the last version of python (last stable version) in the CI/CD pipelines without ignoring security concerns.

So, Team should check the Dockerfile to see which version of python is used, and be sure to use the last stable version with lesser security issue as possible.

### for development

To run the application locally, there is two ways.

First, using vscode, press F5 and the IDE will execute pyright to validate source code before runing the application.

Otherwise, you can execute the following command once the virtual environment is activated: (be advised that pyright will not be executed in this case, so you may want to run it manually before executing the application)

```bash
(.venv) PS > /.venv/Scripts/pyright.exe ./src/main.py
(.venv) PS > python src/main.py
```

---

## 6. Delivery

We use Kubernetes to run the application.

- `dev` runs on a local cluster such as Docker Desktop or Minikube.
- `stg` and `prod` are intended to run on a managed cloud Kubernetes cluster such as AWS or Azure.

For local hosting reasons, the `dev` overlay owns the local storage implementation:

- `k8s/overlays/dev/lsba-pv.yaml` defines a `PersistentVolume` backed by `hostPath`;
- `k8s/overlays/dev/patch-lsba-sc.yaml` patches the `StorageClass` provisioner to `kubernetes.io/no-provisioner`.

The cloud storage configuration for `stg` and `prod` is not finalized yet and must be completed when the cloud provider and CSI driver are selected.

### Team process

We choose to follow a specific process with git to track every move on the kubernetes clusters.

So we are using manifest files and versioning them.

It is the reason why the team have to follow theses step for delivery:

1. create new branch named `deliver/vX.Y.Z` (see bellow for how to version your delivery),
1. change the manifest (check if your needs are well reflected in manifest files),
1. delete cronjobs and local dev jobs
    - if you perform an update other than the image
    - or `k delete -k` works too -> jobs are namespaced so delete the NS delete jobs ;)

1. execute kubernetize project for your dev environment only (stg and prod are handled by CI/CD pipelines):
    - `kustomize build ./k8s/overlays/dev/ --enable-helm > ./k8s/overlays/dev-build.yaml`
    - `k apply -f ./k8s/overlays/dev-build.yaml`
1. Check the local dev jobs are working and processed as expected,
1. Check the cronjob is working after the next scheduled time
    - if local dev jobs are working, the cronjob will work too
    - but it is better to check it after the next scheduled time when an update has been made by one of the source of our data to check if their change is stable
1. Push to git origin the new branch `deliver/vX.Y.Z`
1. Ask for a Pull Request.
1. trigger the `cd-stg` github action to deliver on `stg`.
1. once all checks are done (note: there is no job only cronjobs), trigger the `cd-prod` github action to deliver on `prod`.

This **process is important** to be sure that the manifest files are in sync with the application, and to be sure that the application is **well delivered** on kubernetes cluster **at any time and from scratch**

> NEVER COMMITS the built manifest files, they are generated by the kubernetize project and should be ignored by git.

### Delivery process (deprecated)

**MUST BE REVIEWED, CI/CD pipelines will comes in a couple of days**

Please, follow these steps to deliver the application:

1. Build the Docker image:

   ```
   docker build -t loup-solitaire-book-analyser:vX.Y.Z .
   ```

   > Note:
   > version should be replaced with the actual version number of the application:
   > - X: Major version: Incremented for significant changes that may include breaking changes.
   > - Y: Minor version: Incremented for new features that are backward compatible.
   > - Z: Patch version: Incremented for bug fixes and minor improvements that are backward compatible.
   >
   > **Major version set to 0 means that the application is in development and may have breaking changes at any time, and should not be used in production**

2. deliver on kubernetes:

   ```bash
   kubectl apply -k k8s/overlays/dev
   ```

3. update cronjob and local dev jobs:

   > the kubernetize project set the namespace, so be advise to look after it before executing commands to delete cronjob and local dev jobs.

   - **3.1 local environment**

   ```bash
   
   # remove cronjob and local dev job because we can't restart them with "k rollout restart xxx/yyy" command
   k -n <namespace> delete cronjob loup-solitaire-book-analyser-cronjob
   k -n <namespace> delete job loup-solitaire-book-analyser-job
   ```

   Standalone Job resources are only present in the `dev` overlay. `stg` and `prod` deploy CronJobs only.

   SO, in `dev`, you must **delete the cronjob and local dev job** before execute the apply command when needed.

   Don't worry, the job is only executed once to be sure the application is well set up, even if it initialize data.
   <br/>

   - **3.2 local environment and CI/CD**

   To deliver more quickly, you can update the image (both cronjobs and jobs) but you have to keep in mind to sync manifest files with your changes.

   In CD pipelines, we will use this way to update the application, **so it is important to be sure that the manifest files are in sync with the application**.

   ```bash
   k -n <namespace> set image cronjob/dev-loup-solitaire-book-analyser-cronjob loup-solitaire-book-analyser=loup-solitaire-book-analyser:vX.Y.Z
   k -n <namespace> set image job/dev-loup-solitaire-book-analyser-job loup-solitaire-book-analyser=loup-solitaire-book-analyser:vX.Y.Z
   ```

## 7. File system

Kubernetes security settings and volume permissions are documented in [README-security.md](README-security.md).

> we use '4' as prefix for user and group to avoid conflict with other projects (if they exists).
> We have choose 4 because the alias of the project `lsba` has 4 characters.

### 7.1 Users and Groups

see the security model in [README-security.md](README-security.md#user-and-group-ids) for more details.

### 7.2 Repositories

On a local cluster, the `dev` overlay uses a `hostPath` volume at `/mnt/lsba/dev`. The local worker node must have matching directories and permissions so the application can read and write data and logs.

The local setup script prepares only the `dev` directories. `stg` and `prod` storage must be managed by the selected cloud storage provider.

| directory (env) | sub directory | group name | users |
| --- | --- | --- | --- |
| /mnt/lsba/dev/ | logs/ | **lsba-dev-app** | lsba-dev-batch-usr, lsba-dev-app-usr |
| /mnt/lsba/dev/ | data/ | **lsba-dev-app** | lsba-dev-batch-usr, lsba-dev-app-usr |
| /mnt/lsba/dev/ | postgresql/ | **lsba-dev-data** | lsba-dev-data-usr |

## 8. Project Inputs and Outputs (to be completed)

je me demande si je ne devrais pas faire un HLM puis un LLM par environnement (local avec desktop-docker et stg/prod avec azure ou aws) pour bien représenter les inputs et outputs par environnement.

par contre les LLM auront naturellement des inputs et outputs différents, mais je ne sais pas si c'est une bonne idée de faire un HLM par environnement. (GROS DOUTE surtout que le HLM est fait pour représenter les fonctionnalités normalement mais si on considère un HLM comme représentation technique alors dans ce cas cela represente aussi les inputs et output de chaque block donc ca complixifie inutilement les choses je pense)

### 8.1 Inputs

#### web app

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

#### batchs

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

#### persisted data

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

### 8.2 Outputs

#### web app

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

#### batchs

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

#### persisted data

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

## 9. Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## 10. License

This project is licensed under the MIT License. See the LICENSE file for details.
