from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import docker
import tempfile
import os
import shutil

app = FastAPI()
client = docker.from_env()


@app.post("/upload")
# async def upload( # for future use
#     repo_url: str = Form(...),
#     tech_stack: str = Form(...),
#     port_number: str = Form(...)
# ):
async def upload(repo_url: str = Form(...)):
    # Receive the user's repository

    # Clone or download the repository to a temporary directory
    temp_dir = tempfile.mkdtemp()
    clone_repo(repo_url, temp_dir)

    # TODO: enable user to pass in tech stack options and paths for running commands
    tech_stack = "react-express"  # want to pass this in too eventually

    # Build the Docker container with the user's code
    container_name = generate_unique_container_name()
    container = build_and_run_container(temp_dir, container_name, tech_stack)

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)

    # Return the URL to the user
    url = generate_url(container)
    return JSONResponse(content={"url": url})


# def add_paths_to_dockerfile(tech_stack, cmds, pths):
#     if tech_stack != "react-express":
#         return


def clone_repo(repo_url, temp_dir):
    # For simplicity, let's use git to clone the repo
    os.system(f"git clone {repo_url} {temp_dir}")


def generate_unique_container_name():
    # Here's a simple example using a UUID
    import uuid

    return f"container-{str(uuid.uuid4())}"


def build_and_run_container(temp_dir, container_name, tech_stack):
    # Copy the appropriate Dockerfile into the user's repo
    dockerfile_path = select_dockerfile(tech_stack)
    shutil.copy(dockerfile_path, os.path.join(temp_dir, "Dockerfile"))

    # Build and run the Docker container
    image, _ = client.images.build(path=temp_dir, tag=container_name)
    # container = client.containers.run(
    #     image, detach=True, ports={"8080/tcp": ("0.0.0.0", 0)}
    # )
    container = client.containers.run(image, detach=True, ports={"8080/tcp": 12345})
    return container


def generate_url(container):
    # Generate the URL for the user
    local_public_ip = "127.0.0.1"  # Replace the ec2_instance_public_ip
    print("Dict NetworkSettings[Ports]--------------------------------------")
    print(container.attrs["NetworkSettings"])

    port = (
        12345  # container.attrs["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"]
    )
    return f"http://{local_public_ip}:{port}"


def select_dockerfile(tech_stack):
    # Map technology stacks to Dockerfile paths
    dockerfile_mapping = {
        "react-express": "containers/Dockerfile.react-express",
        "vue-flask": "containers/Dockerfile.vue-flask",
        "react-flask": "containers/Dockerfile.react-flask",
        # Add more mappings as needed
    }

    # Return the Dockerfile path for the given tech_stack
    return dockerfile_mapping.get(tech_stack, "path/to/default/Dockerfile")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
