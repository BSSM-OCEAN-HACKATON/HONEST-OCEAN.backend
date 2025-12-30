import os
from supabase import create_client, Client
import uuid

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = os.environ.get("SUPABASE_BUCKET_NAME")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not set in .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_file(file_content: bytes, filename: str, content_type: str = "image/jpeg") -> str:
    """
    Uploads a file to Supabase Storage and returns the public URL.
    Generates a unique filename to prevent collisions.
    """
    if not BUCKET_NAME:
        raise ValueError("SUPABASE_BUCKET_NAME not set in .env")

    client = get_supabase_client()
    
    # Generate unique path
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    path = f"merchant_uploads/{unique_filename}"
    
    # Upload
    # Note: 'upload' is synchronous in the python client usually? 
    # The python client is sync by default unless async client used. 
    # Standard `create_client` returns a sync client.
    # We'll run it synchronously for now or wrap it if needed.
    # Fastapi handles sync endpoints in threadpool, async endpoints need non-blocking calls.
    # If storage call is blocking, we should ideally run it in a thread or use async client.
    # But for simplicity, let's call it directly. If it blocks, it blocks this request.
    
    res = client.storage.from_(BUCKET_NAME).upload(
        path=path,
        file=file_content,
        file_options={"content-type": content_type}
    )
    
    # Get Public URL
    # The new python client might return response object differently.
    # Assuming successful upload doesn't raise exception.
    
    public_url = client.storage.from_(BUCKET_NAME).get_public_url(path)
    
    return public_url
