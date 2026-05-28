# loup-solitaire-book-analyser Project

## Overview

loup-solitaire-book-analyser is a Python application designed to download a list of books from a specified URL with these prices. The application is structured using a clean architecture approach, separating concerns into different components such as ports, adapters and use cases.

## Project Structure

```text
loup-solitaire-book-analyser
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
├── data                      # Directory for data storage
├── logs                      # Directory for log files
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

## Prerequisites

- Python 3.14 or higher
- Docker (for containerization)
- Docker-desktop or Minikube (for Kubernetes testing and deployment)

## Installation

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

---

## Running the Application

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

## Delivery

We use kubernetes to expose our application, hosting will be done on Azure or AWS, but for now we will use minikube (or desktop docker)to test and deliver the application.

### Team process

We choose to follow a specific process with git to track every move on the kubernetes clusters.

So we are using manifest files and versioning them.

It is the reason why the team have to follow theses step for delivery:

1. create new branch named "deliver/vX.Y.Z" (see bellow for how to version your delivery),
1. change the manifest (check if your needs are well reflected in manifest files),
1. delete cronjob and job (if you perfom an update),
1. execute kubernetize project,
1. to check the job is working and processed as expected,
1. to check the cronjob is working,
1. to push to git origin in a new branch
1. to ask a Pull Request.

This **process is important** to be sure that the manifest files are in sync with the application, and to be sure that the application is **well delivered** on kubernetes cluster **at any time and from scratch**

### Delivery process

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

3. update cronjonb and job:

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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
