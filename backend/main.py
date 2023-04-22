from fastapi import FastAPI
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse


app = FastAPI()


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