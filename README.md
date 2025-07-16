# MongoDB Atlas Stream Processing UI

This web application provides a user-friendly interface to manage MongoDB Atlas Stream Processing instances, connections, and processors. You can list, create, manage, and delete resources directly from your browser.

---

## Features

* **Load Configuration**: Easily populate API credentials from a text file or pasted text.
* **List Resources**: View tables of your Stream Processing Instances (SPIs), Connections, and Processors.
* **Create Resources**: Use modal dialogs to create new SPIs, Connections, and Processors by providing their JSON definitions.
* **Manage Processors**: Start, stop, and delete individual processors.
* **View Details**: View the full JSON details for connections and processor stats in a formatted pop-up with a copy-to-clipboard feature.
* **Flexible Deployment**: Run as a standalone Python Flask application or as a containerized service using Docker Compose.
* **Optional Security**: Supports running with TLS/SSL for a secure HTTPS connection or insecurely over HTTP for local development.

---

## Prerequisites

Before you begin, ensure you have the following software installed on your system:

* **Git**: To clone the repository.
* **Python 3.8+** and **pip**: For running the application in standalone mode.
* **Docker** & **Docker Compose**: For running the application in a container.

---

## Setup & Configuration

Follow these steps to set up the project locally.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

### 2. Create the Configuration File

The application requires a configuration file to store your API credentials. Create a file named `env_file` in the root of the project directory.

Paste the following content into the `env_file`, replacing the placeholder values with your actual credentials.

```
# env_file

# Your MongoDB Atlas API Public Key
public_key=your-public-key

# Your MongoDB Atlas API Private Key
private_key=your-private-key-uuid

# The ID of the project where your streams reside
project_id=your-project-id

# The name of the Stream Processing Instance you want to manage
spi_name=your-instance-name

# The Atlas API hostname (e.g., cloud.mongodb.com)
api_host=cloud.mongodb.com
```

**Note:** This file is included in `.gitignore` and will not be committed to your repository.

---

## Running the Application

You can run the application in two ways: Standalone or with Docker.

### Option 1: Standalone Mode (Without Docker)

This method runs the Python script directly on your machine.

#### A. Create a Virtual Environment

It is highly recommended to use a Python virtual environment to isolate the project's dependencies.

```bash
# Create the virtual environment (we'll name it .venv)
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate
```

#### B. Install Dependencies

Install the required Python libraries using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

#### C. Run the Application

Now, you can start the Flask server.

**To run without TLS (HTTP):**

Make sure you do **not** have a `certs` directory or the `TLS_CERT_PATH` and `TLS_KEY_PATH` variables in your `.env` file.

```bash
python3 web_api_client.py
```

The application will be available at `http://localhost:5000`.

**To run with TLS (HTTPS):**

1.  Create a directory named `certs` in the project root.
2.  Place your TLS certificate (`.pem`) and private key (`.key`) files inside the `certs` directory.
3.  Create a file named `.env` (this is separate from `env_file`) and add the paths to your certificate and key:

    ```
    # .env file
    TLS_CERT_PATH=certs/your_cert_file.pem
    TLS_KEY_PATH=certs/your_key_file.key
    ```
4.  Start the application:

    ```bash
    python3 web_api_client.py
    ```

The application will be available at `https://localhost:5000`.

---

### Option 2: Docker Mode

This is the recommended method for consistent deployment.

#### A. Configure for Docker

The `docker-compose.yml` file is already set up to use the configuration files.

**To run without TLS (HTTP):**

Ensure the `env_file` is present with your API credentials. No `certs` directory is needed.

**To run with TLS (HTTPS):**

1.  Create the `certs` directory and place your certificate and key files inside it.
2.  Create the `.env` file with the `TLS_CERT_PATH` and `TLS_KEY_PATH` variables, pointing to the paths *inside the container*:

    ```
    # .env file
    TLS_CERT_PATH=/certs/your_cert_file.pem
    TLS_KEY_PATH=/certs/your_key_file.key
    ```

#### B. Build and Run the Container

Execute the following command from the project's root directory:

```bash
docker-compose up --build
```

Docker will build the image, install dependencies, and start the application. You can access it in your browser at `http://localhost:5000` or `https://localhost:5000` depending on your TLS setup.

