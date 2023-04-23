from fastapi import FastAPI, Form, File, UploadFile, Depends, Request
from fastapi.responses import JSONResponse
import docker
import tempfile
import os
import shutil
from typing import Any, List, Union, Optional, Annotated
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
from pydantic import BaseModel
import datetime

app = FastAPI()
client = docker.from_env()

# For processing passed in json representing file structure
class FileNode(BaseModel):
    label: str
    content: Union[str, None] = None
    children: Union[List['FileNode'], None] = None
    type: Optional[str] = None  # Add this line to accept the "type" field and set its default value to None

FileNode.update_forward_refs()

def process_file_node(node: FileNode, current_path: str):
    new_path = os.path.join(current_path, node.label)
    if node.children is None:
        with open(new_path, "w") as f:
            f.write(node.content)
    else:
        os.makedirs(new_path, exist_ok=True)
        for child in node.children:
            process_file_node(child, new_path)

active_ids = { usrid: datetime.datetime(2023, 1, 1) for usrid in range(375, 379) }
usrid_container_map = {usrid: None for usrid in range(375, 379) }
usrid_techstack_map = {usrid: None for usrid in range(375, 379) }

@app.get('/gen-id')
def get_id(): 
    for usrid in range(375, 379):
        if (datetime.datetime.now() - active_ids[usrid]).total_seconds() > 60 * 10:
            active_ids[usrid] = datetime.datetime.now()
            return usrid
    return False

# endpoint for edits+additions, initial uploads should use /upload-files/{usrid}
@app.post("/update-files/{usrid}")
async def upload_files(usrid: int, file_structure: FileNode):
    container_id = usrid_container_map[usrid]
    try:
        # Connect to the Docker daemon
        client = docker.from_env()
        # Find the container by ID or name
        container = client.containers.get(container_id)

        # Process the JSON object and create files and directories in the shared directory
        dir_path = os.path.dirname(os.path.realpath(__file__))
        local_shared_path = f"{dir_path}/{usrid}"

        process_file_node(file_structure, local_shared_path)

        # Python script to move the files and directories and re-run npm start
        move_file_and_restart_script = f'''
import os
import shutil

def move_files_up_one_level():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    for item in os.listdir(current_dir):
        if item == os.path.basename(__file__):
            continue

        item_path = os.path.join(current_dir, item)
        dest_path = os.path.join(parent_dir, item)

        if os.path.exists(dest_path):
            if os.path.isfile(dest_path):
                os.remove(dest_path)
            elif os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
        
        if os.path.isfile(item_path):
            shutil.move(item_path, dest_path)
        elif os.path.isdir(item_path):
            shutil.copytree(item_path, dest_path)
            shutil.rmtree(item_path)

if __name__ == '__main__':
    move_files_up_one_level()

'''

        # Create/update a file with the move_file_and_restart_script content in the shared directory
        script_name = "move_and_restart.py"
        script_path = os.path.join(local_shared_path, script_name)

        with open(script_path, "w") as script_file:
            script_file.write(move_file_and_restart_script)

        # Construct the file path inside the container
        container_script_path = os.path.join(f"/usr/src/app/{usrid}/", script_name)

        # Execute the script inside the container
        exec_result = container.exec_run(f"python {container_script_path}")

        # Check if the script execution was successful
        if exec_result.exit_code != 0:
            raise Exception("Error executing the move_file_and_restart script: {}".format(exec_result.output.decode()))

        return {"message": f"Files from the JSON object uploaded and moved to /usr/src/app/{usrid}/ in container {container_id}"}
    except docker.errors.NotFound:
        return {"error": f"Container {container_id} not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500


@app.post("/upload-files/{usrid}")
async def upload(usrid: int, file_structure: FileNode, tech_stack: str):
    
    external_frontend_port = usrid%375 + 8081
    external_backend_port = usrid%375 + 3001

    # Copy the uploaded folder to a temp_dir
    temp_dir = tempfile.mkdtemp()
    process_file_node(file_structure, temp_dir)

    # Define the absolute path where you want to mount the shared volume
    dir_path = os.path.dirname(os.path.realpath(__file__))
    local_mount_path = f"{dir_path}/{usrid}" #HERE

    # Build the Docker container with the user's code
    container_name = str(usrid)
    container = build_and_run_container(
        temp_dir, container_name, tech_stack, local_mount_path, external_frontend_port, external_backend_port, usrid
    )

    # Clean up the temporary directory
    # shutil.rmtree(temp_dir)

    # Return the URL to the user
    # TODO: integrate this with the Nginx - not sure if nginx only needs portnumbers or something more
    url = generate_url(container)
    return JSONResponse(content={"url": url})


# /uploadrepo is not supported rn but it works 
# Receive the user's repository
@app.post("/uploadrepo/{usrid}")
async def upload(usrid: int, repo_url: str = Form(...)):
    
    # Clone or download the repository to a temporary directory
    temp_dir = tempfile.mkdtemp()
    clone_repo(repo_url, temp_dir)

    # TODO: enable user to pass in tech stack options and (maybe) paths for running commands
    tech_stack = "react-express"

    # Define the absolute path where you want to mount the shared volume
    dir_path = os.path.dirname(os.path.realpath(__file__))
    local_mount_path = f"{dir_path}/shared" #HERE

    # Build the Docker container with the user's code
    container_name = str(usrid)
    container = build_and_run_container(
        temp_dir, container_name, tech_stack, local_mount_path
    )

    # Clean up the temporary directory
    # shutil.rmtree(temp_dir)

    # Return the URL to the user
    # TODO: integrate this with the Nginx - not sure if nginx only needs portnumbers or something more
    url = generate_url(container)
    return JSONResponse(content={"url": url})

@app.delete("/containers/{usrid}")
async def delete_container(usrid: int):
    container_id = usrid_container_map[usrid]
    usrid_container_map[usrid] = None

    try:
        # Connect to the Docker daemon
        client = docker.from_env()

        # Find the container by ID or name
        container = client.containers.get(container_id)
        # Stop and remove the container
        container.stop()
        container.remove()

        return {"message": f"Container {container_id} deleted successfully"}
    except docker.errors.NotFound:
        return {"error": f"Container {container_id} not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500



def clone_repo(repo_url, temp_dir):
    # For simplicity, let's use git to clone the repo
    os.system(f"git clone {repo_url} {temp_dir}")


def build_and_run_container(temp_dir, container_name, tech_stack, local_mount_path, external_frontend_port, external_backend_port, usrid):
    # Hard coded these, need to make sure every project has the same configuration
    internal_frontend_port = 5173
    internal_backend_port = 8000

    # Copy the appropriate Dockerfile into the user's repo
    dockerfile_path = select_dockerfile(tech_stack)
    shutil.copy(dockerfile_path, os.path.join(temp_dir, "Dockerfile"))

    # Make sure the local mount path exists
    os.makedirs(local_mount_path, exist_ok=True)

    # Create the bind mount
    bind_mount = docker.types.Mount(
        source=local_mount_path,
        target=f"/usr/src/app/{usrid}", #HERE
        type="bind",
    )

    # build and run docker container
    import subprocess

    subprocess.run(["docker", "build", "-t", container_name, temp_dir])
    container = client.containers.run(
        image=container_name,
        ports={f"{internal_frontend_port}/tcp": external_frontend_port, f"{internal_backend_port}/tcp": external_backend_port},
        mounts=[bind_mount],
        detach=True,
    )

    usrid_container_map[usrid] = container.id

    return container


def generate_url(container):
    # Generate the URL for the user
    local_public_ip = "127.0.0.1"  # Replace the ec2_instance_public_ip
    # print("Dict NetworkSettings[Ports]--------------------------------------")
    # print(container.attrs["NetworkSettings"])

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
        "vue-express": "containers/Dockerfile.vue-express",
        # Add more mappings as needed
    }

    # Return the Dockerfile path for the given tech_stack
    return dockerfile_mapping.get(tech_stack, "containers/Dockerfile.default")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
