from codes.models import Location, Image, LandLordProfile, Post


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


def create_images_type(images_data, type):
    images = []
    for image_file in images_data:
        image = Image.objects.create(image=image_file, image_type=type)
        images.append(image)  # Lưu đối tượng Image vào danh sách
    return images


def create_post(user, content, location, images, type):
    post = Post.objects.create(user=user, location=location, type=type, content=content)
    if type == "find":
        return post
    elif not isinstance(images, list):  # Kiểm tra xem `images` có phải danh sách không
        raise TypeError("`images` must be a list of Image objects.")
    post.images.set(images)  # Gắn các hình ảnh vào bài viết
    post.save()
    return post


def create_landlord_profile(user, location, images):
    landlord_profile = LandLordProfile.objects.create(
        user=user, location=location, approved=False
    )
    landlord_profile.images.set(images)
    landlord_profile.save()
    return landlord_profile
