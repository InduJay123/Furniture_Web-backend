import os
from supabase import create_client
from django.conf import settings

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def upload_image(image):
    file_path = f"products/{image.name}"

    supabase.storage.from_("furniture_products").upload(
        file_path,
        image.read(),
        {"content-type": image.content_type}
    )

    public_url = supabase.storage.from_("furniture_products").get_public_url(file_path)
    return public_url
