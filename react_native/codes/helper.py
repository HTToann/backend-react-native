import cloudinary
from codes.models import Location, Image, LandLordProfile, Post
import cloudinary.uploader
import threading
from django.http import JsonResponse
import httpx


def create_or_get_location(location_data):
    if location_data:
        location, created = Location.objects.get_or_create(
            **location_data, defaults={"latitude": None, "longitude": None}
        )
        return location
    return None


def create_images_type_banner(images_data):
    images = []
    for image_file in images_data:
        image = Image.objects.create(image=image_file, image_type="banner")
        images.append(image)
    return images


async def create_images_type(images_data, upload_preset):
    url = "https://api.cloudinary.com/v1_1/dypt73wn0/image/upload"
    image_urls = []
    async with httpx.AsyncClient() as client:
        for image_file in images_data:
            data = {"upload_preset": upload_preset}
            files = {"file": image_file}

            # Gửi yêu cầu POST bất đồng bộ đến Cloudinary
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            upload_result = response.json()
            image_urls.append(upload_result["secure_url"])  # Lưu URL an toàn của ảnh

    return image_urls


def create_post(user, content, location, images, type):
    post = Post.objects.create(user=user, location=location, type=type, content=content)
    if type == "find":
        return post
    elif not isinstance(images, list):  # Kiểm tra xem `images` có phải danh sách không
        raise TypeError("`images` must be a list of Image objects.")
    post.images.set(images)  # Gắn các hình ảnh vào bài viết
    post.save()
    return post


async def upload_images_to_cloudinary(images_data, upload_preset):
    url = "https://api.cloudinary.com/v1_1/dypt73wn0/image/upload"
    image_urls = []
    async with httpx.AsyncClient() as client:
        for image_file in images_data:
            data = {"upload_preset": upload_preset}
            files = {"file": image_file}

            # Gửi yêu cầu POST bất đồng bộ đến Cloudinary
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            upload_result = response.json()
            image_urls.append(upload_result["secure_url"])  # Lưu URL an toàn của ảnh

    return image_urls


def create_landlord_profile(user, location, image_urls):
    landlord_profile = LandLordProfile.objects.create(
        user=user, location=location, approved=False
    )

    # Tạo và liên kết ảnh từ danh sách URL
    images = []
    for url in image_urls:
        image = Image.objects.create(image=url, image_type="banner")
        images.append(image)

    landlord_profile.images.set(images)
    landlord_profile.save()
    return landlord_profile
