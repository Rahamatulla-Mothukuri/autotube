import os
import asyncio
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "youtube_token.json"
CREDENTIALS_FILE = "youtube_credentials.json"


async def upload_to_youtube(video_path: str, title: str, description: str, tags: list = []) -> dict:
    """Upload video to YouTube using OAuth2."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _upload, video_path, title, description, tags)
    return result


def _upload(video_path: str, title: str, description: str, tags: list) -> dict:
    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",  # Education
        },
        "status": {
            "privacyStatus": "private",  # Upload as private by default for safety
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 5,  # 5MB chunks
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    return {
        "id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def _get_credentials():
    creds = None

    # Load saved token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        return creds

    # New auth flow
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            "youtube_credentials.json not found. "
            "Please download OAuth2 credentials from Google Cloud Console "
            "and save as youtube_credentials.json"
        )

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=8080)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    return creds


def is_youtube_configured() -> bool:
    """Check if YouTube credentials are configured."""
    return os.path.exists(CREDENTIALS_FILE) or os.path.exists(TOKEN_FILE)
