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

* **Git** & **GitHub CLI**: To clone the repository.
* **Python 3.8+** and **pip**: For running the application in standalone mode.
* **Docker** & **Docker Compose**: For running the application in a container.

---

## Setup & Configuration

Follow these steps to set up the project locally.

### 1. Clone the Repository

```bash
gh repo clone josephxsxn/asp_ui
cd asp_ui
```

### 2. Prepare Your API Key File

This application loads your Atlas API credentials from a local file via the web UI. You need to create this file **somewhere on your computer** (it does not need to be inside the project folder).

Create a plain text file (e.g., `my_atlas_keys.txt`) with the following format, replacing the placeholder values with your actual credentials.

```
# my_atlas_keys.txt

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

You will use the "Load Config from File or Text" button in the web UI to load this file.

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
This is the simplest method for local use.

```bash
python3 web_api_client.py
```

The application will be available at `http://localhost:5000`.

**To run with TLS (HTTPS):**
This is optional and only needed if you require a secure connection.

1. Create a directory named `certs` in the project root.
2. Place your TLS certificate (`.pem`) and private key (`.key`) files inside the `certs` directory.
3. Create a file named `.env` in the project root. This file is **only** for the server's TLS certificate paths.
   ```
   # .env file
   TLS_CERT_PATH=certs/your_cert_file.pem
   TLS_KEY_PATH=certs/your_key_file.key
   ```
4. Start the application:
   ```bash
   python3 web_api_client.py
   ```

The application will be available at `https://localhost:5000`.

---

### Option 2: Docker Mode

This is the recommended method for consistent deployment.

#### A. Configure for Docker

**To run without TLS (HTTP):**
No extra files are needed. The application will start and serve over HTTP.

**To run with TLS (HTTPS):**

1. Create the `certs` directory and place your certificate and key files inside it.
2. Create the `.env` file with the `TLS_CERT_PATH` and `TLS_KEY_PATH` variables. These paths must point to where the files will be *inside the container*, as defined in `docker-compose.yml`.
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

