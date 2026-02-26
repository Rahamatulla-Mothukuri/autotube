import os
import asyncio
import httpx
from moviepy.editor import (
    VideoFileClip, AudioFileClip, concatenate_videoclips,
    TextClip, CompositeVideoClip, ColorClip
)
from moviepy.video.fx import resize
import textwrap

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PEXELS_URL = "https://api.pexels.com/videos/search"

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080


async def create_video(script: dict, audio_path: str, output_dir: str, job_id: str) -> str:
    """Download stock footage and assemble final video."""
    
    scenes = script.get("scenes", [])
    narration = script.get("narration", "")
    title = script.get("title", "AutoTube Video")

    # Get audio duration to time scenes
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    audio_clip.close()

    # Redistribute scene durations proportionally
    total_script_duration = sum(s.get("duration", 5) for s in scenes)
    for scene in scenes:
        ratio = scene.get("duration", 5) / max(total_script_duration, 1)
        scene["actual_duration"] = ratio * total_duration

    # Download videos for each scene
    clips_dir = f"{output_dir}/clips"
    os.makedirs(clips_dir, exist_ok=True)

    video_clips = []
    
    for i, scene in enumerate(scenes):
        query = scene.get("search_query", scene.get("text", "nature landscape"))
        duration = scene.get("actual_duration", 5)
        
        clip_path = await download_pexels_video(query, f"{clips_dir}/scene_{i}.mp4", duration)
        
        if clip_path and os.path.exists(clip_path):
            try:
                clip = VideoFileClip(clip_path)
                # Resize to standard size
                clip = clip.resize((VIDEO_WIDTH, VIDEO_HEIGHT))
                # Trim to needed duration
                if clip.duration > duration:
                    clip = clip.subclip(0, duration)
                elif clip.duration < duration:
                    # Loop if too short
                    loops = int(duration / clip.duration) + 1
                    from moviepy.editor import concatenate_videoclips as concat
                    clip = concat([clip] * loops).subclip(0, duration)
                video_clips.append(clip)
            except Exception as e:
                print(f"Error processing clip {i}: {e}")
                # Fallback: colored placeholder
                video_clips.append(create_placeholder_clip(duration, scene.get("text", "")))
        else:
            video_clips.append(create_placeholder_clip(duration, scene.get("text", "")))

    if not video_clips:
        raise ValueError("No video clips could be created")

    # Concatenate all clips
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Add audio
    audio = AudioFileClip(audio_path)
    if audio.duration < final_video.duration:
        final_video = final_video.subclip(0, audio.duration)
    
    final_video = final_video.set_audio(audio)

    # Add title overlay for first 3 seconds
    title_clip = create_title_overlay(title, min(3, final_video.duration))
    final_with_title = CompositeVideoClip([
        final_video,
        title_clip
    ])

    # Export final video
    output_path = f"{output_dir}/final_video.mp4"
    final_with_title.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=f"{output_dir}/temp_audio.m4a",
        remove_temp=True,
        preset="ultrafast",
        threads=4,
        logger=None,
    )

    # Generate thumbnail from first frame
    thumbnail_path = f"{output_dir}/thumbnail.jpg"
    thumbnail_frame = final_video.get_frame(1)
    from PIL import Image
    import numpy as np
    img = Image.fromarray(thumbnail_frame.astype('uint8'))
    img = img.resize((1280, 720))
    img.save(thumbnail_path, "JPEG", quality=85)

    # Cleanup
    for clip in video_clips:
        clip.close()
    audio.close()
    final_video.close()
    final_with_title.close()

    return output_path


async def download_pexels_video(query: str, output_path: str, min_duration: float) -> str:
    """Download a stock video from Pexels API."""
    if not PEXELS_API_KEY:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                PEXELS_URL,
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": query,
                    "per_page": 5,
                    "orientation": "landscape",
                    "size": "medium",
                }
            )
            response.raise_for_status()
            data = response.json()

        videos = data.get("videos", [])
        if not videos:
            return None

        # Pick first video with adequate duration
        for video in videos:
            if video.get("duration", 0) >= min_duration:
                # Get HD video file
                video_files = sorted(
                    video.get("video_files", []),
                    key=lambda x: x.get("width", 0),
                    reverse=True
                )
                
                for vf in video_files:
                    if vf.get("width", 0) >= 720:
                        download_url = vf.get("link")
                        if download_url:
                            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as dl_client:
                                dl_response = await dl_client.get(download_url)
                                dl_response.raise_for_status()
                                with open(output_path, "wb") as f:
                                    f.write(dl_response.content)
                            return output_path

        return None

    except Exception as e:
        print(f"Pexels download error for '{query}': {e}")
        return None


def create_placeholder_clip(duration: float, text: str = "") -> VideoFileClip:
    """Create a dark placeholder clip when stock footage unavailable."""
    bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(20, 20, 40), duration=duration)
    if text:
        try:
            txt = TextClip(
                textwrap.fill(text, 40),
                fontsize=48,
                color="white",
                font="DejaVu-Sans",
                align="center",
            ).set_duration(duration).set_position("center")
            return CompositeVideoClip([bg, txt])
        except Exception:
            pass
    return bg


def create_title_overlay(title: str, duration: float):
    """Create a title text overlay for the beginning."""
    try:
        wrapped = textwrap.fill(title, 35)
        txt = TextClip(
            wrapped,
            fontsize=72,
            color="white",
            font="DejaVu-Sans-Bold",
            stroke_color="black",
            stroke_width=3,
            align="center",
        ).set_duration(duration).set_position(("center", 0.15), relative=True).fadein(0.5).fadeout(0.5)
        return txt
    except Exception as e:
        print(f"Title overlay error: {e}")
        return ColorClip(size=(1, 1), color=(0, 0, 0, 0), duration=duration, ismask=False)
