import base64

from fastapi import (
    APIRouter,
    UploadFile,
    Header,
    HTTPException,
    BackgroundTasks,
    Form,
)
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import tempfile
import shutil
import os
import requests
from typing import Optional
from app.core.config import settings
from app.services.preview import preview_service
from app.services.meta import meta_service

router = APIRouter()


class FileProcessingResult(BaseModel):
    file_type: str
    content: str
    preview: Optional[str] = None


class CallbackResponse(BaseModel):
    message: str


@router.post(
    "/process_file/",
    responses={
        200: {
            "content": {
                "application/json": {},
                "image/jpeg": {},
            },
            "description": "Returns JSON with file info or image preview based on Accept header",
        }
    },
)
async def process_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    callback_url: Optional[str] = Form(None),
    x_api_key: str = Header(...),
    accept: str = Header(None),
):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    try:
        file_type = meta_service.get_file_mimetype(temp_file_path)
        content = meta_service.extract_content(temp_file_path)
        preview_data = preview_service.create_preview(temp_file_path)

        result = FileProcessingResult(
            file_type=file_type,
            content=content,
            preview=(
                base64.b64encode(preview_data).decode("utf-8") if preview_data else None
            ),
        )

        if callback_url:
            background_tasks.add_task(send_callback, callback_url, result)
            return CallbackResponse(
                message="File processing started. Results will be sent to the callback URL."
            )

        if accept == "image/jpeg" and preview_data:
            return Response(content=preview_data, media_type="image/jpeg")

        return JSONResponse(content=result.dict())
    finally:
        os.unlink(temp_file_path)


async def send_callback(callback_url: str, result: FileProcessingResult):
    response = requests.post(callback_url, json=result.dict())
    if response.status_code != 200:
        print(f"Failed to send results to callback URL: {response.text}")
