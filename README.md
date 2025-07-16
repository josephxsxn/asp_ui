MongoDB Atlas Stream Processing UIThis web application provides a user-friendly interface to manage MongoDB Atlas Stream Processing instances, connections, and processors. You can list, create, manage, and delete resources directly from your browser.FeaturesLoad Configuration: Easily populate API credentials from a text file or pasted text.List Resources: View tables of your Stream Processing Instances (SPIs), Connections, and Processors.Create Resources: Use modal dialogs to create new SPIs, Connections, and Processors by providing their JSON definitions.Manage Processors: Start, stop, and delete individual processors.View Details: View the full JSON details for connections and processor stats in a formatted pop-up with a copy-to-clipboard feature.Flexible Deployment: Run as a standalone Python Flask application or as a containerized service using Docker Compose.Optional Security: Supports running with TLS/SSL for a secure HTTPS connection or insecurely over HTTP for local development.PrerequisitesBefore you begin, ensure you have the following software installed on your system:Git: To clone the repository.Python 3.8+ and pip: For running the application in standalone mode.Docker & Docker Compose: For running the application in a container.Setup & ConfigurationFollow these steps to set up the project locally.1. Clone the Repositorygit clone <your-repository-url>
cd <your-repository-folder>
2. Create the Configuration FileThe application requires a configuration file to store your API credentials. Create a file named env_file in the root of the project directory.Paste the following content into the env_file, replacing the placeholder values with your actual credentials.# env_file

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
Note: This file is included in .gitignore and will not be committed to your repository.Running the ApplicationYou can run the application in two ways: Standalone or with Docker.Option 1: Standalone Mode (Without Docker)This method runs the Python script directly on your machine.A. Create a Virtual EnvironmentIt is highly recommended to use a Python virtual environment to isolate the project's dependencies.# Create the virtual environment (we'll name it .venv)
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate
B. Install DependenciesInstall the required Python libraries using the requirements.txt file.pip install -r requirements.txt
C. Run the ApplicationNow, you can start the Flask server.To run without TLS (HTTP):Make sure you do not have a certs directory or the TLS_CERT_PATH and TLS_KEY_PATH variables in your .env file.python3 web_api_client.py
The application will be available at http://localhost:5000.To run with TLS (HTTPS):Create a directory named certs in the project root.Place your TLS certificate (.pem) and private key (.key) files inside the certs directory.Create a file named .env (this is separate from env_file) and add the paths to your certificate and key:# .env file
TLS_CERT_PATH=certs/your_cert_file.pem
TLS_KEY_PATH=certs/your_key_file.key
Start the application:python3 web_api_client.py
The application will be available at https://localhost:5000.Option 2: Docker ModeThis is the recommended method for consistent deployment.A. Configure for DockerThe docker-compose.yml file is already set up to use the configuration files.To run without TLS (HTTP):Ensure the env_file is present with your API credentials. No certs directory is needed.To run with TLS (HTTPS):Create the certs directory and place your certificate and key files inside it.Create the
