from sketch import models
import base64
from loguru import logger
from django.core.files.base import ContentFile
from django.db.models import QuerySet, Q
import json
import random
from datetime import datetime, timedelta
import os
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from app import settings
from sketch.ml import feature_extraction as fe


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
        zip_code=request_data.get('zipCode'),
        gender=request_data.get('gender')
    )

    criminal_data.picture.save(file_name, data, save=True)
    criminal_data.save()

    return criminal_data


def updating_minmax(data: dict):
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

    return


def image_detail_import(iin: str, data: dict):
    """

    """
    updating_minmax(data=data)

    image_details, created = models.CriminalsImage.objects.update_or_create(
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


def normalized_feature_array(image_details: QuerySet) -> dict:
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

    return normalized_dict


def update_criminal(iin: str, data: dict):
    """

    """
    updating_minmax(data=data)

    image_details = models.CriminalsImage.objects.get(iin=iin)
    image_details.nose_len = data['nose_length']
    image_details.lips_size = data['lips_size']
    image_details.nose_size = data['nose_size']
    image_details.left_brow_size = data['left_brow_size']
    image_details.left_eye_size = data['left_eye_size']
    image_details.right_brow_size = data['right_brow_size']
    image_details.right_eye_size = data['right_eye_size']

    image_details.save()
    normalized_dict = normalized_feature_array(image_details)


# Function to generate random date of birth
def generate_dob():
    start_date = datetime(1960, 1, 1)
    end_date = datetime(2005, 12, 31)
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    return random_date.strftime('%Y-%m-%d')


def random_generator() -> dict:
    # List of Female Names
    # names = [
    #     "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn",
    #     "Abigail", "Emily", "Elizabeth", "Mila", "Ella", "Avery", "Sofia", "Camila", "Aria", "Scarlett",
    #     "Victoria", "Madison", "Luna", "Grace", "Chloe", "Penelope", "Layla", "Riley", "Zoey", "Nora",
    #     "Lily", "Eleanor", "Hannah", "Lillian", "Addison", "Aubrey", "Ellie", "Stella", "Natalie", "Zoe",
    #     "Leah", "Hazel", "Violet", "Aurora", "Savannah", "Audrey", "Brooklyn", "Bella", "Claire", "Skylar"
    # ]

    # List of Male Names
    names = [
        "James", "John", "Robert", "Michael", "William",
        "David", "Richard", "Joseph", "Charles", "Thomas",
        "Christopher", "Daniel", "Matthew", "Anthony", "Donald",
        "Mark", "Paul", "Steven", "Andrew", "Kenneth",
        "Joshua", "George", "Kevin", "Brian", "Edward",
        "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
        "Gary", "Jacob", "Nicholas", "Eric", "Stephen",
        "Jonathan", "Larry", "Justin", "Scott", "Brandon",
        "Frank", "Benjamin", "Gregory", "Samuel", "Raymond",
        "Patrick", "Alexander", "Jack", "Dennis", "Jerry"
    ]

    # List of Surnames
    surnames = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
        "Walker", "Young", "Hall", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Rivera", "Campbell", "Mitchell", "Carter"
    ]
    offenses = ['Theft', 'Assault', 'Fraud', 'Drug Possession', 'Shoplifting', 'DUI', 'Speeding']
    zip_codes = ['10001', '20002', '30003', '40004', '50005']

    name = random.choice(names)
    surname = random.choice(surnames)
    dob = generate_dob()
    martial_status = random.choice(['Single', 'Married', 'Divorced'])
    offense = random.choice(offenses)
    zip_code = random.choice(zip_codes)
    people = {'name': name, 'surname': surname, 'dob': dob, 'martial_status': martial_status, 'offense': offense, 'zip_code': zip_code}

    return people


def script():
    counter = 2000
    rd = {}
    directory = f'{settings.BASE_DIR}/media/men2'
    for filename in os.listdir(directory):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            face_detials = fe.Mesh(f'{directory}/{filename}')
            woman = random_generator()
            rd = {
                'iin': counter,
                'firstName': woman['name'],
                'lastName': woman['surname'],
                'dob': woman['dob'],
                'maritalStatus': woman['martial_status'],
                'offense': woman['offense'],
                'zipCode': woman['zip_code'],
                'gender': 'male'
            }

            criminal_data = models.CriminalsData.objects.create(
                iin=rd.get('iin'),
                first_name=rd.get('firstName'),
                last_name=rd.get('lastName'),
                dob=rd.get('dob'),
                martial_status=rd.get('maritalStatus'),
                offence=rd.get('offense'),
                zip_code=rd.get('zipCode'),
                gender=rd.get('gender')
            )

            with open(f"{directory}/{filename}", 'rb') as f:
                logger.info(f)
                image_data = f.read()

            file_name = f"{str(rd.get('iin'))}.jpeg"
            logger.info(file_name)

            image_file = io.BytesIO(image_data)
            uploaded_file = InMemoryUploadedFile(image_file, None, file_name, 'image/jpeg', len(image_data),
                                                 None)

            criminal_data.picture.save(file_name, uploaded_file, save=True)
            criminal_data.save()

            image_details = image_detail_import(rd.get('iin'), face_detials)

            # creating normalized feature vector
            normalized_dict = normalized_feature_array(image_details)
            logger.info('saved')
            counter += 1
            # time.sleep(1)
