import os
import uuid

from server.utils.errors import APIError

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def upload_image(file, folder="listings"):
    _, ext = os.path.splitext(file.filename or "")
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise APIError(
            f"Unsupported image type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            status_code=400,
        )

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_UPLOAD_BYTES:
        raise APIError("Image is too large (max 5MB)", status_code=400)

    filename = f"{folder}/{uuid.uuid4()}{ext}"
    storage_path = os.getenv("STORAGE_PATH", "./uploads")
    os.makedirs(os.path.join(storage_path, folder), exist_ok=True)
    filepath = os.path.join(storage_path, filename)
    file.save(filepath)
    return f"/static/uploads/{filename}"


def delete_image(url):
    if url.startswith("/static/uploads/"):
        storage_path = os.getenv("STORAGE_PATH", "./uploads")
        filepath = url.replace("/static/uploads/", f"{storage_path}/")
        if os.path.exists(filepath):
            os.remove(filepath)
