# Agent C Framework Dockerfiles 

**All commands assume you're int the root folder of the project.**

## GRADION Dev container:

Build: `docker build -t agent_c_framework -f dockerfiles\Dockerfile.dev .`

Run: `>docker run -it -p 7860:7860 --rm --env-file .env  agent_c_framework`

When you see the message about going to http://0.0.0 open http://127.0.0.1:7860/ in your browser.

- Note: you must have set up up your `.env` file
- **Important**: If you already have a `.env` file remove quotes around strings in it before running thing.

## REACT UI and API Containers:
### Prerequisites
* Docker and Docker Compose must be installed on your machine.
* A valid .env file must exist in the project root (agent_c_framework/.env).
  * Note: ADVANCED USERS ONLY - 
    * .dockerignore excludes copying this file over by default. By default we load via docker-compose.yml and load into memory.  If it is needed at run time, such as by an underlying tool, then you will have to manually copy it inside the container.
    * If need to change the location of the .env to pull from, then modify Docker Compose’s env_file directive to the correct path.
    * By default we're loading .env into memory from the .env file in the project root.
* For Windows users, ensure that batch scripts are executed from the correct directory.
* For macOS/Linux users, ensure that the shell scripts are executable.

### Running the Containers
#### Windows
* Open a `cmd` window
* Navigate to the `dockerfiles` directory:
```bash
cd C:\Users\justj\PycharmProjects\agent_c_framework\dockerfiles
```
* Run the batch script:
```bash
web_api_docker_start.bat
```

#### Linux/macOS
* Open a terminal
* Navigate to the `dockerfiles` directory:
```bash
cd /path/to/agent_c_framework/dockerfiles
```
* Ensure the `start.sh` file is executable:
```bash
chmod +x web_api_docker_start.sh
```
* Run the script:
```bash
./web_api_docker_start.sh
```

Open browser to http://localhost:5173/ to view the React UI.
Open browser to http://localhost:8000/ to view the API directly (really only for troubleshooting).


### Docker Compose Configuration Details
#### API Service

* **Build Context**: Set to the project root (..) so that all required files (including .env) are available.
* **Dockerfile**: Located at `dockerfiles/api.Dockerfile`.
* **Environment File**: Uses `env_file: - ../.env` to load environment variables.
* **Volumes**:
  * `../src` is mounted to `/app/src` for development hot-reloading.
  * `../images` is mounted to `/app/images` to store saved images.
* **Ports**: Exposes port 8000.

#### Frontend Service
* **Build Context**: Set to the project root (..).
* **Dockerfile**: Located at `dockerfiles/frontend.Dockerfile`.
* **Volumes**:
        `../src/agent_c_api_ui/agent_c_react_client` is mounted to `/app` for hot-reloading.
* **Ports**: Exposes port 5173.
* **Depends on**: The API service, so it waits for the API container to start.

Both services are connected via the agent-c-network (a bridge network).

### Stopping the Containers
#### Stop and keep existing Containers
* Navigate to the `dockerfiles` directory.
```bash
docker-compose.yml stop
```
#### Stop and REMOVE the Containers
* Navigate to the `dockerfiles` directory.
```bash
docker-compose.yml down
```
* to also remove the volumes, add the `-v` flag:
```bash
docker-compose.yml down -v
```
* Down and remove images
```bash
docker-compose.yml down --rmi <all|local>
```
