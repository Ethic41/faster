#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-23 23:47:33
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


import io
import ulid

from app.utils.misc import requester
from fastapi.datastructures import UploadFile
import qrcode # type: ignore
from io import BytesIO
from qrcode import constants
from os import getenv
from google.cloud import storage
from PIL import Image, ImageDraw, ImageFont


def create_frontend_qr_data(unique_data: str, frontend_var_name: str = ""):
    frontend_qr_url = getenv(frontend_var_name, "")
    return f"{frontend_qr_url}{unique_data}"


def create_qr_file(
    data: str, 
    fill_color: str = "black", 
    back_color: str = "white"
) -> Image.Image:

    qr = qrcode.QRCode(
        version=None,
        error_correction=constants.ERROR_CORRECT_M,
        box_size=10,
        border=1
    )
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color=fill_color, back_color=back_color)
    return image


def generate_in_memory_file(qr_image):
    in_memory = BytesIO()
    qr_image.save(in_memory, 'PNG')
    in_memory.seek(0)
    in_memory_png = in_memory.getvalue()
    return in_memory_png


def resize_image(uploaded_file: UploadFile, new_size=(350, 466)):
    image = Image.open(uploaded_file.file)
    image_out = image.resize(new_size)
    return image_out


def get_image(image_bytes):
    return Image.open(image_bytes)


def upload_file_to_cloud(in_memory_file, file_name, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    img_name = f"{file_name}"
    blob = bucket.blob(img_name)

    blob.upload_from_string(in_memory_file, content_type="image/png")
    return True


def create_and_upload_qr_cloud(
    qr_unique_data: str,
    cloud_bucket_var_name: str,
    qr_filename: str,
    qr_display_text: str = ""
    
):
    qr_data = create_frontend_qr_data(qr_unique_data)
    qr_image = create_qr_file(qr_data)
    
    if qr_display_text:
        qr_image = add_qr_display_text(qr_image, qr_display_text)
    
    in_memory_image = generate_in_memory_file(qr_image)
    bucket_name = getenv(cloud_bucket_var_name)
    return upload_file_to_cloud(in_memory_image, qr_filename, bucket_name)


def add_qr_display_text(qr_image: Image.Image, qr_display_text: str)-> Image.Image:
    width, height = qr_image.size
    new_image = Image.new('RGB', (width, height + 100), (255, 255, 255))
    text_image = Image.new('RGB', (width, 100), (255, 255, 255))
    font = ImageFont.truetype("app/assets/fonts/Roboto.ttf", size=42)
    draw = ImageDraw.Draw(text_image)
    draw.text((width/2, 100/2), qr_display_text, font=font, anchor="mm", fill=(0, 0, 0))
    new_image.paste(qr_image, (0, 0))
    new_image.paste(text_image, (0, height))
    return new_image


def upload_image_to_cloud(
    image,
    cloud_bucket_var_name: str,
    file_name: str
):
    in_memory_image = generate_in_memory_file(image)
    bucket_name = getenv(cloud_bucket_var_name)

    if upload_file_to_cloud(in_memory_image, file_name, bucket_name):
        return f"{getenv('CLOUD_STORAGE_PATH')}{bucket_name}/{file_name}"
    
    raise Exception("Unable to upload image to cloud")

def upload_remote_image_to_cloud(url: str, filename: str, bucket_var_name: str):
    response = requester(url)
    image = get_image(io.BytesIO(response.content))
    return upload_image_to_cloud(image, bucket_var_name, filename)


def upload_image_file_to_cloud(
    image_file: UploadFile,
    cloud_bucket_var_name: str,
):
    resized_image = resize_image(image_file)
    file_name = f"{str(ulid.new())}.png"
    return upload_image_to_cloud(resized_image, cloud_bucket_var_name, file_name)

