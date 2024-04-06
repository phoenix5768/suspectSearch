from sketch import models
import base64
from loguru import logger
from django.core.files.base import ContentFile


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
    models.CriminalsImage.objects.create(
        iin=models.CriminalsData.objects.get(iin=iin),
        nose_len=data['nose_length'],
        right_brow_size=data['right_brow_size'],
        left_brow_size=data['left_brow_size'],
        left_eye_size=data['left_eye_size'],
        right_eye_size=data['right_eye_size'],
        nose_size=data['nose_size'],
        lips_size=data['lips_size']
    )

    return


def normalized_feature_array(iin: str):
    """

    """


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
