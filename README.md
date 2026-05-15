# LoupSolitaire Project

## Overview

LoupSolitaire is a Python application designed to manage and download a list of books from a specified URL. The application is structured using a modular approach, separating concerns into different components such as gateways and use cases.

## Project Structure

```
LoupSolitaire
├── src
│   ├── main.py               # Main entry point of the application
│   ├── gateways
│   │   └── __init__.py       # Gateway classes for file system, HTML reading, and logging
│   └── usecases
│       └── __init__.py       # Business logic for managing tomes
├── data                       # Directory for data storage
├── Dockerfile                 # Dockerfile for containerizing the application
├── .dockerignore              # Files and directories to ignore in Docker builds
├── requirements.txt           # Python dependencies for the application
└── README.md                  # Documentation for the project
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Docker (for containerization)

### Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd LoupSolitaire
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

To run the application locally, execute the following command:

```
python src/main.py
```

### Docker Setup

To build and run the application in a Docker container, follow these steps:

1. Build the Docker image:

   ```
   docker build -t loup-solitaire-book-analyser .
   ```

2. Run the Docker container:
   ```
   docker run loup-solitaire-book-analyser
   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
