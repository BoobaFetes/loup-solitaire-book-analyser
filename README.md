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

We use kubernetes to expose our application, hosting will be done on Azure or AWS, but for now we will use minikube (or desktop docker) to test and deliver the application.

### Team process

We choose to follow a specific process with git to track every move on the kubernetes clusters.

So we are using manifest files and versioning them.

It is the reason why the team have to follow theses step for delivery:

1. create new branch named `deliver/vX.Y.Z` (see bellow for how to version your delivery),
1. change the manifest (check if your needs are well reflected in manifest files),
1. delete cronjobs and jobs
    - if you perform an update other than the image
    - or k delete -k works too ;)

1. execute kubernetize project
    - `k apply -k ./k8s/overlays/dev or stg or prod` to deliver the application on the cluster,
1. Check the jobs are working and processed as expected,
1. Check the cronjob is working after the next scheduled time
    - if jobs are working, the cronjob will work too
    - but it is better to check it after the next scheduled time when an update has been made by one of the source of our data to check if their change is stable
1. Push to git origin in a new branch
1. Ask for a Pull Request.

This **process is important** to be sure that the manifest files are in sync with the application, and to be sure that the application is **well delivered** on kubernetes cluster **at any time and from scratch**

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
   kubectl apply -f k8s/overlay/dev
   ```

3. update cronjob and job:

   > the kubernetize project set the namespace, so be advise to look after it before executing commands to delete cronjob and job.

   - **3.1 local environment**

   ```bash
   
   # remove cronjob and job because we can't restart them with "k rollout restart xxx/yyy" command
   k -n <namespace> delete cronjob loup-solitaire-book-analyser-cronjob
   k -n <namespace> delete job loup-solitaire-book-analyser-job
   ```

   SO, you must **delete the cronjob and job** before execute the apply command.

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

> we use '4' as prefix for user and group to avoid conflict with other projects (if they exists).
> We have choose 4 because the alias of the project `lsba` has 4 characters.

### 7.1 Users and Groups

The groups are 4x0y: where x is the environment (dev, staging, prod) and y is the type of application (app or data).

so we have:

- `400x` for the dev groups
- `410x` for the staging groups
- `420x` for the prod groups

so :

| env | group id | group name | description |
| --- | -------- | ---------- | ----------- |
| dev | `4000` | **lsba-dev-app** | for app like jobs or webapp |
| dev | `4001` | **lsba-dev-data** | for data like postgresql |
| stg | `4100` | **lsba-stg-app** | for app like jobs or webapp |
| stg | `4101` | **lsba-stg-data** | for data like postgresql |
| prod | `4200` | **lsba-prod-app** | for app like jobs or |
| prod | `4201` | **lsba-prod-data** | for data like postgresql |

The users are:

| env | user id | user name | group id | description |
| --- | ------- | --------- | -------- | ---------- |
| dev | 4001 | **lsba-dev-batch-usr** | 4000 | for batchs (cronjobs and jobs) |
| dev | 4002 | **lsba-dev-app-usr** | 4000 | for webapp (webapp and api) |
| dev | 4003 | **lsba-dev-data-usr** | 4001 | for data (postgresql) |
| stg | 4101 | **lsba-stg-batch-usr** | 4100 | for batchs (cronjobs and jobs) |
| stg | 4102 | **lsba-stg-app-usr** | 4100 | for webapp (webapp and api) |
| stg | 4103 | **lsba-stg-data-usr** | 4101 | for data (postgresql) |
| prod | 4201 | **lsba-prod-batch-usr** | 4200 | for batchs (cronjobs and jobs) |
| prod | 4202 | **lsba-prod-app-usr** | 4200 | for webapp (webapp and api) |
| prod | 4203 | **lsba-prod-data-usr** | 4201 | for data (postgresql) |

> In K8s manifests, we use user id to do not use root (runAsNonRoot need a runAsUser), but only the group id is used for permission in the linux file system.
> WHY are user not set in linux ?
> Because, in local, we use en image of linux with docker-desktop, and the linux kernel checks the group id not the user id so we don't need to define them on the linux accounts /etc/passwd nor addUser

In local node (with desktop-docker or minikube):

- `root` (only for local and to check files in physical volumes)

    ```cmd
    k get node # to find the name of the worker node
    docker exec -it <worker_node_name> bash
    # then check the files in the physical volumes and their permissions
    root@<worker_node_name>:/# ls -l /mnt/volumes/lsba/**/**/
    ```

> we have to use root to check the files in the physical volumes, so we have to add a user for root

### 7.2 Repositories

on local cluter (desktop ), we have to set the file system permissions to be sure that the applications can read and write in the right directories.

so:

in /mnt/volumes/lsba/ permissions are :

| directory (env) | sub directory | group name | users |
| --- | --- | --- | --- |
| dev/ | logs/ | **lsba-dev-app** | lsba-dev-batch-usr, lsba-dev-app-usr |
| dev/ | data/ | **lsba-dev-app** | lsba-dev-batch-usr, lsba-dev-app-usr |
| dev/ | postgresql/ | **lsba-dev-data** | lsba-dev-data-usr |
| stg/ | logs/ | **lsba-stg-app** | lsba-stg-batch-usr, lsba-stg-app-usr |
| stg/ | data/ | **lsba-stg-app** | lsba-stg-batch-usr, lsba-stg-app-usr |
| stg/ | postgresql/ | **lsba-stg-data** | lsba-stg-data-usr |
| prod/ | logs/ | **lsba-prod-app** | lsba-prod-batch-usr, lsba-prod-app-usr |
| prod/ | data/ | **lsba-prod-app** | lsba-prod-batch-usr, lsba-prod-app-usr |
| prod/ | postgresql/ | **lsba-prod-data** | lsba-prod-data-usr |

for now, because we don't know where the application will be deployed

- /mnt/volumes/lsba/    → root seul

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
