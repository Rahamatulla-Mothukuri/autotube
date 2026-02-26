from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os, uuid

from agents.research_agent import research_topic
from agents.script_agent import generate_script
from agents.voice_agent import generate_voice
from agents.video_agent import create_video
from agents.youtube_agent import upload_to_youtube

app = FastAPI(title="AutoTube AI Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

jobs = {}

class TopicRequest(BaseModel):
    topic: str

class ApprovalRequest(BaseModel):
    job_id: str
    approved: bool
    feedback: str = ""

class YouTubeRequest(BaseModel):
    job_id: str
    title: str
    description: str
    tags: list[str] = []

@app.get("/")
def root():
    return {"status": "AutoTube AI Agent running"}

@app.post("/api/generate")
async def generate_video(request: TopicRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"id": job_id, "topic": request.topic, "status": "starting", "step": "Initializing...", "progress": 0, "script": None, "video_url": None, "audio_url": None, "thumbnail_url": None, "error": None}
    background_tasks.add_task(run_pipeline, job_id, request.topic)
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.post("/api/upload")
async def upload_video(request: YouTubeRequest):
    if request.job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    video_path = f"outputs/{request.job_id}/final_video.mp4"
    if not os.path.exists(video_path):
        raise HTTPException(status_code=400, detail="Video not found")
    jobs[request.job_id]["status"] = "uploading"
    jobs[request.job_id]["step"] = "Uploading to YouTube..."
    try:
        result = await upload_to_youtube(video_path=video_path, title=request.title, description=request.description, tags=request.tags)
        jobs[request.job_id]["status"] = "uploaded"
        jobs[request.job_id]["youtube_url"] = result["url"]
        return {"success": True, "youtube_url": result["url"]}
    except Exception as e:
        jobs[request.job_id]["status"] = "upload_failed"
        jobs[request.job_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/regenerate")
async def regenerate(request: ApprovalRequest, background_tasks: BackgroundTasks):
    if request.job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    topic = jobs[request.job_id]["topic"]
    enhanced_topic = f"{topic}. Feedback: {request.feedback}" if request.feedback else topic
    jobs[request.job_id].update({"status": "starting", "step": "Regenerating...", "progress": 0, "video_url": None, "error": None})
    background_tasks.add_task(run_pipeline, request.job_id, enhanced_topic)
    return {"job_id": request.job_id}

async def run_pipeline(job_id: str, topic: str):
    try:
        output_dir = f"outputs/{job_id}"
        os.makedirs(output_dir, exist_ok=True)
        update_job(job_id, "researching", "🔍 Researching topic on the web...", 10)
        research_data = await research_topic(topic)
        update_job(job_id, "scripting", "✍️ Writing video script with AI...", 30)
        script = await generate_script(topic, research_data)
        jobs[job_id]["script"] = script
        update_job(job_id, "voicing", "🎙️ Generating voiceover...", 50)
        audio_path = await generate_voice(script["narration"], f"{output_dir}/narration.mp3")
        jobs[job_id]["audio_url"] = f"/outputs/{job_id}/narration.mp3"
        update_job(job_id, "creating_video", "🎬 Assembling video with stock footage...", 70)
        await create_video(script=script, audio_path=audio_path, output_dir=output_dir, job_id=job_id)
        jobs[job_id]["video_url"] = f"/outputs/{job_id}/final_video.mp4"
        jobs[job_id]["thumbnail_url"] = f"/outputs/{job_id}/thumbnail.jpg"
        update_job(job_id, "ready", "✅ Video ready for review!", 100)
    except Exception as e:
        import traceback; traceback.print_exc()
        jobs[job_id].update({"status": "error", "step": f"❌ Error: {str(e)}", "error": str(e)})

def update_job(job_id, status, step, progress):
    jobs[job_id].update({"status": status, "step": step, "progress": progress})
