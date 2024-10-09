from fastapi import APIRouter, UploadFile, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel
import tempfile
import shutil
import os
import requests
from app.core.config import settings
from app.services.preview import preview_service
from app.services.meta import meta_service

router = APIRouter()


class CallbackData(BaseModel):
    file_id: int
    preview_path: str
    meta_data: dict


@router.post("/generate_preview/")
async def generate_preview(
        file: UploadFile,
        file_id: int,
        callback_url: str,
        background_tasks: BackgroundTasks,
        x_api_key: str = Header(...),
):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    background_tasks.add_task(process_file, temp_file_path, file_id, callback_url, file.filename)
    return {"message": "Preview generation started"}


def process_file(file_path: str, file_id: int, callback_url: str, original_filename: str):
    preview_path = preview_service.create_preview(file_path)

    file_type = meta_service.get_file_mimetype(file_path)
    description = meta_service.get_description(file_path)

    meta_data = {
        "file_type": file_type,
        "description": description,
    }

    callback_data = CallbackData(
        file_id=file_id,
        preview_path=preview_path,
        meta_data=meta_data
    )

    requests.post(callback_url, json=callback_data.dict())

    os.unlink(file_path)