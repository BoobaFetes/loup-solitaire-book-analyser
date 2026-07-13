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
├── assets                    # Directory for image or html storage
├── logs                      # Directory for log files
├── readme                    # Detailed project documentation
├── Dockerfile                # Dockerfile for containerizing the application
├── requirements.txt          # Python dependencies for the application
├── README.md                 # Documentation entrypoint
└── todo.md                   # TODO list for the project, or tasks that remain to be completed
```

> Note:
>
> The application has code checking, unit tests and coverage for CI/CD pipelines that ensure code quality and reliability.
> We are using best practices that can break the automatic build if issues are detected.

## 3. Prerequisites

- Python 3.14 or higher
- Docker
- Docker Desktop or Minikube for Kubernetes testing and deployment

## Summary

- [Project Documentation](readme/project.md): detailed installation, runtime, delivery, filesystem, contribution and license notes.
- [Architecture](readme/architecture.md): overview of the architecture, inputs and outputs for the web app, batchs and persisted data.
- [Command Reminder](readme/command-reminder.md): quick reference for the most common local development and Kubernetes commands.
- [PostgreSQL Local Usage](readme/postgres-usage.md): French guide for bootstrapping DB users, running Alembic, executing `main.py`, and checking the database.
- [Kubernetes Security](readme/security.md): Kubernetes security model, service accounts, Linux users/groups and volume permissions.
- [How To Bitnami PostgreSQL](readme/how-to-bitnami-postgresql.md): notes and examples for the Bitnami PostgreSQL Helm chart.
- [Todo](todo.md): short tracking list for current and upcoming work.
