from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILES_DIR = r"..\files"  # ROBIN
# UPLOAD_DIR =          # shreesh
# UPLOAD_DIR = r"D:\SWAGAT\idkhack\files\upload"         # swagat
# EDIT_DIR = r"D:\SWAGAT\idkhack\files\edit"             # swagat

# Mount the files directory to serve static files
app.mount("/files", StaticFiles(directory="../files"), name="files")

# os.makedirs(UPLOAD_DIR, exist_ok=True)
def ffmpeg_runner(ffmpeg_code: str):
    print(ffmpeg_code)
    try:
        process = subprocess.run(
            ffmpeg_code, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True
        )
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with error:\n{e.output}")
        return False

def scene_detect_runner(scene_detect_code: str):
    print(scene_detect_code)
    try:
        process = subprocess.run(
            scene_detect_code, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True
        )
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Scene detection failed with error:\n{e.output}")
        return False

def whisper_runner(whisper_code: str):
    print(whisper_code)
    try:
        process = subprocess.run(
            whisper_code, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True
        )
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Whisper failed with error:\n{e.output}")
        return False

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    print(file)
    if not file.filename:
        raise ValueError("No filename provided")
    file_path = os.path.join(FILES_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".mp4"):
        try:
            subprocess.run(f'ffmpeg -i "../files/{file.filename}" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1" -r 30 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -ar 44100 -movflags +faststart "../files/normalized_{file.filename}"')
        except subprocess.CalledProcessError as e:
            print(e)
            raise ValueError("MP4 Normalizing failed")
    elif file.filename.endswith(".mp3"):
        try:
            subprocess.run(
                f'ffmpeg -i "../files/{file.filename}" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -b:a 192k -ar 44100 "../files/normalized_{file.filename}"',
                shell=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(e)
            raise ValueError("MP3 normalizing failed")

    os.remove(f"../files/{file.filename}")
    os.rename(f"../files/normalized_{file.filename}", f"../files/{file.filename}")

    return {"filename": file.filename, "message": "File uploaded successfully"}

class Query(BaseModel):
    prompt: str
    video_version: str

@app.post("/query")
async def user_query(query: Query) -> Tuple[bool, int]:
    """
    work on the mentioned video version using the given prompt.

    example: trim this video from 2nd second to the 7th second.

    It'll then use this prompt on the specified video with the name "video_version.mp4".

    Returns the new video version number as a string
    """

    # edit_dir = r"C:\Users\Robin Roy\Desktop\idkhack\files\edit"
    # edit_dir = r"C:\Users\Robin Roy\Desktop\idkhack\files\edit"           # SHREESH
    # edit_dir = r"D:\SWAGAT\idkhack\files\edit"           # SWAGAT
    print(query)
    num_files = 0
    for name in os.listdir(FILES_DIR):
        if os.path.isfile(os.path.join(FILES_DIR, name)) and name[:-4].isdigit():
            num_files += 1
    print(num_files)

    SYSTEM_INSTRUCTION = f"""
Write command-line code based on user queries. The files are inside ../files. 
If the user asks for scene detection, use the command:
    scenedetect -i ../files/{query.video_version}.mp4 detect-content split-video -o ../files/{num_files+1}.mp4
If the user asks for subtitles, use Whisper with the command:
    whisper ../files/{query.video_version} --language English --output_format srt --output_dir ../files
Otherwise, use ffmpeg. Save output videos in ../files as {num_files+1}.mp4.

example code: ffmpeg -i ../files/input1.mp4 -i ../files/input2.mp4 -filter_complex "[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[outv][outa]" -map "[outv]" -map "[outa]" output.mp4
example code for adding subtitles srt file : ffmpeg -i ../files/WIN_20250306_11_55_38_Pro.mp4 -vf subtitles=../files/WIN_20250306_11_55_38_Pro.srt ../files/1.mp4 

and when the user aske to "add subtitles to video.mp4" -> ffmpeg -i ../files/video.mp4 -vf subtitles=../files/video.srt ../files/video_subtitle.mp4, PLEASE REMEMBER TO DO THIS WHEN THE USER ASKS TO ADD SUBTITLES

When user says version 1, version 2 etc, they are mentioning 1.mp4, 2.mp4 respectively.

ALWAYS CALL THE APPROPRIATE FUNCTION: ffmpeg_runner for FFmpeg, scene_detect_runner for scene detection, or whisper_runner for Whisper. MENTION THE PATH ALWAYS ../files
"""

# For some queries, you'll need to work on the latest edit, so you've to work on the current file: ../files/edit/{query.video_version}. Save the new file as {num_files+1}

    chat = client.aio.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[ffmpeg_runner, scene_detect_runner, whisper_runner]
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