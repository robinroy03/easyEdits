from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import shutil
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Tuple
import subprocess


app = FastAPI()
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# CORS settings to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Change if frontend is hosted elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = r"C:\Users\Robin Roy\Desktop\idkhack\files\upload"  # ROBIN
# UPLOAD_DIR =          # shreesh
# UPLOAD_DIR =          # swagat

# os.makedirs(UPLOAD_DIR, exist_ok=True)

def ffmpeg_runner(ffmpeg_code: str):
    """
    Runs an FFmpeg command and prints output in real-time.
    """
    print(ffmpeg_code)
    try:
        process = subprocess.run(
            ffmpeg_code, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.STDOUT,  # Capture errors in the same stream
            text=True  # Ensure output is treated as text (not bytes)
        )
        
        print(process.stdout)  # Print FFmpeg output
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with error:\n{e.output}")
        return False


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    print(file)
    if not file.filename:
        raise ValueError("No filename provided")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        subprocess.run(f'ffmpeg -i "../files/upload/{file.filename}" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1" -r 30 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -ar 44100 -movflags +faststart "../files/upload/normalized_{file.filename}"')
    except subprocess.CalledProcessError as e:
        print(e)
        raise ValueError("Normalizing failed")

    os.remove(f"../files/upload/{file.filename}")
    os.rename(f"../files/upload/normalized_{file.filename}", f"../files/upload/{file.filename}")

    return {"filename": file.filename, "message": "File uploaded successfully"}


class Query(BaseModel):
    prompt: str
    video_version: str  # this is the file name in /edit

@app.post("/query")
async def user_query(query: Query) -> Tuple[bool, int]:
    """
    work on the mentioned video version using the given prompt.

    example: trim this video from 2nd second to the 7th second.

    It'll then use this prompt on the specified video with the name "video_version.mp4".

    Returns the new video version number as a string
    """

    edit_dir = r"C:\Users\Robin Roy\Desktop\idkhack\files\edit"
    # edit_dir = r"C:\Users\Robin Roy\Desktop\idkhack\files\edit"           # SHREESH
    # edit_dir = r"C:\Users\Robin Roy\Desktop\idkhack\files\edit"           # SWAGAT

    num_files = len([name for name in os.listdir(edit_dir) if os.path.isfile(os.path.join(edit_dir, name))])
    print(num_files)

    SYSTEM_INSTRUCTION = f"""
Write ffmpeg code for the queries given. The files are inside `../files/upload`. Save the file inside `../files/edit` as {num_files+1}.mp4.

example code: ffmpeg -i input1.mp4 -i input2.mp4 -filter_complex "[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[outv][outa]" -map "[outv]" -map "[outa]" output.mp4

For some queries, you'll need to work on the latest edit, so you've to work on the current file: ../files/edit/{query.video_version}.mp4. Save the new file as {num_files+1}.mp4

ALWAYS CALL THE FUNCTION FFMPEG_RUNNER.
"""

    chat = client.aio.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[ffmpeg_runner]
        ),
    )

    response = await chat.send_message(query.prompt)
    print(response)

    try:
        if response.automatic_function_calling_history[-1].parts[0].function_response.response['result']:
            return True, num_files+1
        else:
            return False, -1
    except Exception as e:
        print(e)
        return False, -1
