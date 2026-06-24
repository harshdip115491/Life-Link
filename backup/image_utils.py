import os
from PIL import Image

# Folder to store images
UPLOAD_FOLDER = "user_images"

# Create folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🔹 Save Image (Camera / Upload / Cropped)
def save_image(image_file, username, cropped_img=None):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, f"{username}.jpg")

        # ✅ If cropped image provided (PIL Image)
        if cropped_img is not None:
            cropped_img.save(file_path, format="JPEG")

        # ✅ Else save original upload/camera image
        else:
            img = Image.open(image_file)
            img.save(file_path, format="JPEG")

        return file_path

    except Exception as e:
        print("Error saving image:", e)
        return None


# 🔹 Load Image (for profile display)
def load_image(username):
    file_path = os.path.join(UPLOAD_FOLDER, f"{username}.jpg")

    if os.path.exists(file_path):
        return file_path
    else:
        return None


# 🔹 Replace Image (Profile Update)
def update_image(image_file, username, cropped_img=None):
    return save_image(image_file, username, cropped_img)


# 🔹 Delete Image (Optional)
def delete_image(username):
    file_path = os.path.join(UPLOAD_FOLDER, f"{username}.jpg")

    if os.path.exists(file_path):
        os.remove(file_path)
        return True

    return False
