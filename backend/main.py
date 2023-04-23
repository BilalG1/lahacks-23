from fastapi import FastAPI, Request
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import datetime
import openai
import os

# export OPENAI_API_KEY="sk_..."
openai.api_key = os.environ["OPENAI_API_KEY"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
active_ids = { id: datetime.datetime(2023, 1, 1) for id in range(375, 380) }

@app.get('/gen-id')
def get_id(): 
    for id in range(375, 380):
        if (datetime.datetime.now() - active_ids[id]).total_seconds() > 60 * 10:
            active_ids[id] = datetime.datetime.now()
            return id
    return False

@app.post('/reset-ids')
def reset():
    global active_ids
    active_ids = { id: datetime.datetime(2023, 1, 1) for id in range(375, 380) }

@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}

@app.get("/")
async def main():
    content = """
        <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
        <input name="files" type="file" webkitdirectory multiple>
        <input type="submit">
        </form>
        </body>
    """
    return HTMLResponse(content=content)

@app.post("/gen-plan")
async def gen_plan(request: Request):
    payload = await request.json()
    objective = payload.get("objective")
    return "[\n  { file: 'src/components/HomePage.vue', purpose: 'The first page the user sees' },\n  { file: 'src/components/VideoList.vue', purpose: 'Displays a list of videos' },\n  { file: 'src/components/VideoCard.vue', purpose: 'Displays information about a single video' },\n  { file: 'src/components/VideoPlayer.vue', purpose: 'Plays a selected video' },\n  { file: 'src/components/SearchBar.vue', purpose: 'Allows the user to search for videos' },\n  { file: 'src/components/Navigation.vue', purpose: 'Provides navigation links to various parts of the site' },\n  { file: 'src/components/Footer.vue', purpose: 'Provides information about the site and its creators' }\n]"
    planPrompt = f"""
    You are a frontend developer. Your job is to help plan the development of a website using Vue. 
    Use the following objective to come up with a list of files you would need to create the frontend. 
    Output your list as an array of dicts. Each dict should be of the form {{ file: 'src/components/HomePage.vue': purpose: 'The first page the user sees' }}.
    All of your files should be in the src/components directory or a subdirectory and should be .vue files.
    Objective: {objective}
    """

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": planPrompt}]
    )
    return completion["choices"][0]["message"]["content"]

@app.post("/gen-file")
async def gen_file(request: Request):
    payload = await request.json()
    objective = payload.get("objective")
    plan = payload.get("plan")


    planPrompt = f"""
    You are a frontend developer. Your job is to help plan the development of a website using Vue. 
    Use the following objective to come up with a list of files you would need to create the frontend. 
    Output your list as an array of dicts. Each dict should be of the form {{ file: 'src/components/HomePage.vue': purpose: 'The first page the user sees' }}.
    All of your files should be in the src/components directory and should be .vue files
    Objective: {objective}"""

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": planPrompt}]
    )
    return completion["choices"][0]["message"]["content"]
