from fastapi import FastAPI, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse
import docker
import tempfile
import os
import shutil
from typing import Any, List
from pydantic import BaseModel

# TODO: need to have some way to know which user is using which backend as the process for killing and 
# re-running the backed will be different for each backend
userBackend={"user1": "node", "user2": "flask"}    

app = FastAPI()
client = docker.from_env()

# For processing passed in json representing file structure
class FileNode(BaseModel):
    filename: str
    content: str = None
    children: List[Any] = []

def json_to_file_node(json_obj): # maybe not needed, not sure if json is converted to FileNode be default with fastAPI
    filename = json_obj['filename']
    content = json_obj.get('content')
    children = [json_to_file_node(child) for child in json_obj['children']]
    return FileNode(filename=filename, content=content, children=children)

def process_file_node(node, current_path):
    new_path = os.path.join(current_path, node.filename)
    if node.content is None:
        os.makedirs(new_path)
    else:
        with open(new_path, "w") as f:
            f.write(node.content)
    for child in node.children:
        process_file_node(child, new_path)

@app.post("/upload-file/{container_id}")
async def upload_file(container_id: str, file_structure: FileNode):#, target_path: str = Form(...)):
    try:
        # Connect to the Docker daemon
        client = docker.from_env()
        # Find the container by ID or name
        container = client.containers.get(container_id)

        # Process the JSON object and create files and directories in the shared directory
        dir_path = os.path.dirname(os.path.realpath(__file__))
        local_shared_path = f"{dir_path}/shared" #HERE

        process_file_node(file_structure, local_shared_path)

        # Python script to move the files and directories and re-run npm start
        move_file_and_restart_script = f'''
import os
import shutil
import subprocess

def move_files(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, False, None)
        else:
            shutil.copy2(s, d)

shared_dir = "/app/shared"
source_path = "{file_structure.filename}"
target_path = "{target_path}"

# Move the files and directories to the target path
move_files(os.path.join(shared_dir, source_path), target_path)

# Re-run npm start
os.chdir("/app/project")  # Change this to the project directory if needed
subprocess.run(["npm", "stop"], check=True)
subprocess.run(["npm", "start"], check=True)
'''

        # Create a temporary file with the move_file_and_restart_script content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as script_file:
            script_file.write(move_file_and_restart_script)
            script_file.flush()

            # Copy the script to the container
            with open(script_file.name, 'rb') as f:
                container.put_archive('/app', f.read())

            # Remove the temporary file from the local machine
            os.unlink(script_file.name)

        # Execute the script inside the container
        exec_result = container.exec_run("python /app/{}".format(os.path.basename(script_file.name)))

        # Check if the script execution was successful
        if exec_result.exit_code != 0:
            raise Exception("Error executing the move_file_and_restart script: {}".format(exec_result.output.decode()))

        return {"message": f"Files from the JSON object uploaded and moved to {target_path} in container {container_id}"}
    except docker.errors.NotFound:
        return {"error": f"Container {container_id} not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500


# async def upload( # for future use
#     repo_url: str = Form(...),
#     tech_stack: str = Form(...),
#     port_number: str = Form(...),
#     username: str = Form(...)
# ):
# Receive the user's repository
@app.post("/uploadrepo")
async def upload(repo_url: str = Form(...)):
    # Clone or download the repository to a temporary directory
    temp_dir = tempfile.mkdtemp()
    clone_repo(repo_url, temp_dir)

    # TODO: enable user to pass in tech stack options and (maybe) paths for running commands
    tech_stack = "react-express"

    # Define the absolute path where you want to mount the shared volume
    dir_path = os.path.dirname(os.path.realpath(__file__))
    local_mount_path = f"{dir_path}/shared" #HERE

    # Build the Docker container with the user's code
    container_name = generate_unique_container_name()
    container = build_and_run_container(
        temp_dir, container_name, tech_stack, local_mount_path
    )

    # Clean up the temporary directory
    # shutil.rmtree(temp_dir)

    # Return the URL to the user
    # TODO: integrate this with the Nginx - not sure if nginx only needs portnumbers or something more
    url = generate_url(container)
    return JSONResponse(content={"url": url})

# send files from editor on front-end to server. Then server copies file into shared volume with docker container, then 
# a python script is executed in the docker container which moves the uploaded files to where their path specifies
# finall the p
@app.post("/upload-file/{container_id}")
async def upload_file(container_id: str, file: UploadFile = File(...), target_path: str = Form(...)):
    try:
        # Connect to the Docker daemon
        client = docker.from_env()
        # Find the container by ID or name
        container = client.containers.get(container_id)

        # Save the uploaded file to the shared directory
        local_shared_path = "/path/to/your/local/shared/directory"
        local_file_path = os.path.join(local_shared_path, file.filename)
        with open(local_file_path, "wb") as f:
            f.write(await file.read())

        # Python script to move the file and re-run npm start
        move_file_and_restart_script = f'''
import os
import shutil
import subprocess

shared_dir = "/app/shared"
source_path = os.path.join(shared_dir, "{file.filename}")
target_path = "{target_path}"

# Move the file to the target path
shutil.move(source_path, target_path)

# Re-run npm start
os.chdir("/app/project")  # Change this to the project directory if needed
subprocess.run(["npm", "stop"], check=True)
subprocess.run(["npm", "start"], check=True)
'''

        # Create a temporary file with the move_file_and_restart_script content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as script_file:
            script_file.write(move_file_and_restart_script)
            script_file.flush()

            # Copy the script to the container
            with open(script_file.name, 'rb') as f:
                container.put_archive('/app', f.read())

            # Remove the temporary file from the local machine
            os.unlink(script_file.name)

        # Execute the script inside the container
        exec_result = container.exec_run("python /app/{}".format(os.path.basename(script_file.name)))

        # Check if the script execution was successful
        if exec_result.exit_code != 0:
            raise Exception("Error executing the move_file_and_restart script: {}".format(exec_result.output.decode()))

        return {"message": f"File {file.filename} uploaded and moved to {target_path} in container {container_id}"}
    except docker.errors.NotFound:
        return {"error": f"Container {container_id} not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500


@app.delete("/containers/{container_id}")
async def delete_container(container_id: str):
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


# def add_paths_to_dockerfile(tech_stack, cmds, pths):
#     if tech_stack != "react-express":
#         return


def clone_repo(repo_url, temp_dir):
    # For simplicity, let's use git to clone the repo
    os.system(f"git clone {repo_url} {temp_dir}")


def generate_unique_container_name():
    # TODO: name container with username+uuid
    import uuid

    return f"container-{str(uuid.uuid4())}"


def build_and_run_container(temp_dir, container_name, tech_stack, local_mount_path):
    internal_port = 8080
    external_port = 12345
    # Copy the appropriate Dockerfile into the user's repo
    dockerfile_path = select_dockerfile(tech_stack)
    shutil.copy(dockerfile_path, os.path.join(temp_dir, "Dockerfile"))

    # Make sure the local mount path exists
    os.makedirs(local_mount_path, exist_ok=True)

    # Create the bind mount
    bind_mount = docker.types.Mount(
        source=local_mount_path,
        target="/usr/src/app/shared", #HERE
        type="bind",
    )

    # NOTE: not using subprocess kinda breaks this as it creates three containers instead of one when using docker python sdk - if subprocesses doesn't work on vm, can switch back
    # Build and run the Docker container
    # image, _ = client.images.build(path=temp_dir, tag=container_name)
    # container = client.containers.run(
    #     image=image,
    #     ports={f"{internal_port}/tcp": external_port},
    #     mounts=[bind_mount],
    #     detach=True,
    # )
    import subprocess

    subprocess.run(["docker", "build", "-t", container_name, temp_dir])
    container = client.containers.run(
        image=container_name,
        ports={f"{internal_port}/tcp": external_port},
        mounts=[bind_mount],
        detach=True,
    )

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
        # Add more mappings as needed
    }

    # Return the Dockerfile path for the given tech_stack
    return dockerfile_mapping.get(tech_stack, "containers/Dockerfile.default")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
