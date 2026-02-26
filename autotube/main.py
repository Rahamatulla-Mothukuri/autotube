from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid, os, asyncio
from pathlib import Path

from agents.researcher import research_topic
from agents.scriptwriter import generate_script
from agents.voicegen import generate_voice
from agents.videocreator import create_video
from agents.uploader import upload_to_youtube

app = FastAPI(title="AutoTube AI Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

jobs = {}
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

class TopicRequest(BaseModel):
    topic: str
    style: str = "informative"
    duration: int = 60

class ApprovalRequest(BaseModel):
    job_id: str
    approved: bool
    feedback: str = ""

class UploadCredentials(BaseModel):
    job_id: str
    access_token: str
    youtube_title: str = ""
    youtube_description: str = ""
    youtube_tags: list[str] = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/generate")
async def generate_video(req: TopicRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"id": job_id, "topic": req.topic, "status": "queued", "step": "Starting...", "progress": 0, "error": None, "script": None, "video_url": None, "research_summary": None}
    background_tasks.add_task(run_pipeline, job_id, req)
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]

@app.post("/api/approve")
async def approve_video(req: ApprovalRequest):
    if req.job_id not in jobs:
        raise HTTPException(404, "Job not found")
    job = jobs[req.job_id]
    if not req.approved:
        job["status"] = "rejected"
        job["feedback"] = req.feedback
        return {"message": "Feedback received"}
    job["status"] = "approved"
    return {"message": "Approved!"}

@app.post("/api/upload")
async def upload_video(req: UploadCredentials, background_tasks: BackgroundTasks):
    if req.job_id not in jobs:
        raise HTTPException(404, "Job not found")
    background_tasks.add_task(run_upload, req.job_id, req)
    return {"message": "Upload started"}

@app.get("/api/video/{job_id}")
def get_video(job_id: str):
    path = OUTPUTS_DIR / job_id / "final.mp4"
    if not path.exists():
        raise HTTPException(404, "Video not found")
    return FileResponse(str(path), media_type="video/mp4")

async def run_pipeline(job_id: str, req: TopicRequest):
    job = jobs[job_id]
    job_dir = OUTPUTS_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    try:
        update_job(job, "researching", "Researching topic across the web...", 10)
        research = await asyncio.to_thread(research_topic, req.topic)
        job["research_summary"] = research

        update_job(job, "scripting", "Writing video script with AI...", 30)
        script = await asyncio.to_thread(generate_script, req.topic, research, req.style, req.duration)
        job["script"] = script

        update_job(job, "voicing", "Generating voiceover audio...", 50)
        audio_path = await asyncio.to_thread(generate_voice, script, str(job_dir / "audio.mp3"))

        update_job(job, "creating_video", "Fetching stock footage & creating video...", 70)
        video_path = await asyncio.to_thread(create_video, req.topic, script, audio_path, str(job_dir / "final.mp4"))

        job["video_url"] = f"/api/video/{job_id}"
        update_job(job, "ready", "Your video is ready for review!", 100)
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        job["step"] = f"Error: {str(e)}"

async def run_upload(job_id: str, req: UploadCredentials):
    job = jobs[job_id]
    video_path = str(OUTPUTS_DIR / job_id / "final.mp4")
    try:
        update_job(job, "uploading", "Uploading to YouTube...", 90)
        result = await asyncio.to_thread(upload_to_youtube, video_path, req.access_token, req.youtube_title or job.get("topic","AutoTube Video"), req.youtube_description or job.get("script","")[:500], req.youtube_tags or [])
        job["youtube_url"] = result
        update_job(job, "uploaded", "Successfully uploaded to YouTube!", 100)
    except Exception as e:
        job["status"] = "upload_error"
        job["error"] = str(e)

def update_job(job, status, step, progress):
    job["status"] = status
    job["step"] = step
    job["progress"] = progress
