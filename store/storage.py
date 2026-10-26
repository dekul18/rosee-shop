"""Minimal Cloudinary file storage: uploads product photos to Cloudinary and serves them from its CDN."""
import io
import os
import uuid

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryStorage(Storage):
    def _save(self, name, content):
        import cloudinary.uploader  # reads CLOUDINARY_URL from the environment
        content.seek(0)
        base, _ = os.path.splitext(name.replace("\\", "/"))
        result = cloudinary.uploader.upload(
            io.BytesIO(content.read()), public_id=f"{base}-{uuid.uuid4().hex[:8]}",
            resource_type="image", overwrite=False)
        return f"{result['public_id']}.{result['format']}"

    def url(self, name):
        import cloudinary.utils
        return cloudinary.utils.cloudinary_url(name, secure=True)[0]

    def exists(self, name):
        return False  # every upload gets a unique id

    def delete(self, name):
        import cloudinary.uploader
        cloudinary.uploader.destroy(os.path.splitext(name)[0], invalidate=True)

    def _open(self, name, mode="rb"):
        raise NotImplementedError("Files are stored on Cloudinary; use .url instead.")
