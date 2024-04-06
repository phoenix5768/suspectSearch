from sketch import models
import base64
from loguru import logger
from django.core.files.base import ContentFile
from django.db.models import QuerySet, Q
import json


def criminal_detail_import(request_data: dict):
    """
    Inserts criminals data into database
    :param request_data: personal details of a criminal
    :return: created criminal object
    """

    image_data = request_data.get('picture')
    format, imgstr = image_data.split(';base64,')
    ext = format.split('/')[-1]

    data = ContentFile(base64.b64decode(imgstr))
    file_name = f"{str(request_data.get('iin'))}." + ext

    criminal_data = models.CriminalsData.objects.create(
        iin=request_data.get('iin'),
        first_name=request_data.get('firstName'),
        last_name=request_data.get('lastName'),
        dob=request_data.get('dob'),
        martial_status=request_data.get('maritalStatus'),
        offence=request_data.get('offense'),
        zip_code=request_data.get('zipCode')
    )

    criminal_data.picture.save(file_name, data, save=True)
    criminal_data.save()

    return criminal_data


def image_detail_import(iin: str, data: dict):
    """

    """
    max_values = models.MaxMin.objects.get(func_name='max')
    if max_values.nose_len < float(data['nose_length']):
        max_values.nose_len = float(data['nose_length'])
    if max_values.right_brow_size < float(data['right_brow_size']):
        max_values.right_brow_size = float(data['right_brow_size'])
    if max_values.left_brow_size < float(data['left_brow_size']):
        max_values.left_brow_size = float(data['left_brow_size'])
    if max_values.left_eye_size < float(data['left_eye_size']):
        max_values.left_eye_size = float(data['left_eye_size'])
    if max_values.right_eye_size < float(data['right_eye_size']):
        max_values.right_eye_size = float(data['right_eye_size'])
    if max_values.nose_size < float(data['nose_size']):
        max_values.nose_size = float(data['nose_size'])
    if max_values.lips_size < float(data['lips_size']):
        max_values.lips_size = float(data['lips_size'])
    max_values.save()

    min_values = models.MaxMin.objects.get(func_name='min')
    if min_values.nose_len > float(data['nose_length']) != 0:
        min_values.nose_len = float(data['nose_length'])
    if min_values.right_brow_size > float(data['right_brow_size']) != 0:
        min_values.right_brow_size = float(data['right_brow_size'])
    if min_values.left_brow_size > float(data['left_brow_size']) != 0:
        min_values.left_brow_size = float(data['left_brow_size'])
    if min_values.left_eye_size > float(data['left_eye_size']) != 0:
        min_values.left_eye_size = float(data['left_eye_size'])
    if min_values.right_eye_size > float(data['right_eye_size']) != 0:
        min_values.right_eye_size = float(data['right_eye_size'])
    if min_values.nose_size > float(data['nose_size']) != 0:
        min_values.nose_size = float(data['nose_size'])
    if min_values.lips_size > float(data['lips_size']) != 0:
        min_values.lips_size = float(data['lips_size'])
    min_values.save()

    image_details = models.CriminalsImage.objects.create(
        iin=models.CriminalsData.objects.get(iin=iin),
        nose_len=data['nose_length'],
        right_brow_size=data['right_brow_size'],
        left_brow_size=data['left_brow_size'],
        left_eye_size=data['left_eye_size'],
        right_eye_size=data['right_eye_size'],
        nose_size=data['nose_size'],
        lips_size=data['lips_size']
    )

    return image_details


def normalized_feature_array(image_details: QuerySet):
    """

    """
    max_values = models.MaxMin.objects.get(func_name='max')
    min_values = models.MaxMin.objects.get(func_name='min')

    normalized_dict = {}
    normalized_dict['nose_len'] = (image_details.nose_len - min_values.nose_len) / (
                max_values.nose_len - min_values.nose_len)
    normalized_dict['right_brow_size'] = (image_details.right_brow_size - min_values.right_brow_size) / (
                max_values.right_brow_size - min_values.right_brow_size)
    normalized_dict['left_brow_size'] = (image_details.left_brow_size - min_values.left_brow_size) / (
                max_values.left_brow_size - min_values.left_brow_size)
    normalized_dict['left_eye_size'] = (image_details.left_eye_size - min_values.left_eye_size) / (
                max_values.left_eye_size - min_values.left_eye_size)
    normalized_dict['right_eye_size'] = (image_details.right_eye_size - min_values.right_eye_size) / (
                max_values.right_eye_size - min_values.right_eye_size)
    normalized_dict['nose_size'] = (image_details.nose_size - min_values.nose_size) / (
                max_values.nose_size - min_values.nose_size)
    normalized_dict['lips_size'] = (image_details.lips_size - min_values.lips_size) / (
                max_values.lips_size - min_values.lips_size)

    image_details.normalized_feature = json.dumps(normalized_dict)
    image_details.save()

    return


def search_criminal(data: dict) -> list:
    result = []

    # Current idea of a search algorithm
    # 1. Normalise data (So each metric will have the same weight)
    # Example:
    #          normalized_nose_length = (nose_length - min_nose_length) / (max_nose_length - min_nose_length)
    # 2. Concatenate metrics into a single feature vector (np.array() or pd.Series())
    # 3. Compare feature vectors and choose the closest objects (like within 10%)
    # Comparing by calculating distances. Possible techniques: Euclidean distance or cosine similarity. Or maybe even KNN
    # linera or logistic regression

    return result
