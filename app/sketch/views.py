import base64
import json
import os

import ujson

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpRequest
from django.contrib.auth.decorators import user_passes_test

from . import models
from sketch.ml import feature_extraction as fe
from sketch.handlers import criminals_handler as ch
from loguru import logger
from django.db.models import QuerySet, Q
from sketch.ml import search_algorithm as sa

from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

from app import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.files.base import ContentFile


UserModel = get_user_model()


class IdentificationNumberBackend(ModelBackend):
    def authenticate(self, request, iin=None, password=None, **kwargs):
        if iin is None or password is None:
            return
        try:
            # Adjusting the query to use the `iin` field for lookup
            user = UserModel.objects.get(iin=iin)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to mitigate timing attacks
            UserModel().set_password(password)


def admin_inner(request):
    if request.method == 'POST':
        iin = request.POST.get('iin')
        password = request.POST.get('password')

        # Ensure the IIN is exactly 12 digits
        if len(iin) != 12 or not iin.isdigit():
            return HttpResponse('Invalid IIN', status=400)

        try:
            user = authenticate(request, iin=iin, password=password)

            # Verify the password manually since `authenticate` is not used here
            if user and not user.is_policeman() and user.is_admin() and not user.is_superuser:
                login(request, user)
                return render(request, 'admin_inner.html')
            else:
                return JsonResponse('Unauthorized', status=401)
        except User.DoesNotExist:
            return JsonResponse('Unauthorized', status=401)
    else:
        return JsonResponse('Method not allower', status=405)


def police_inner(request):
    if request.method == 'POST':
        iin = request.POST.get('iin')
        password = request.POST.get('password')

        # Ensure the IIN is exactly 12 digits
        if len(iin) != 12 or not iin.isdigit():
            return HttpResponse('Invalid IIN', status=400)

        try:
            user = authenticate(request, iin=iin, password=password)

            if user and user.is_policeman() and not user.is_admin() and not user.is_superuser:
                login(request, user)
                return render(request, 'police_inner.html')
            else:
                return HttpResponse('Unauthorized', status=401)
        except User.DoesNotExist:
            return HttpResponse('Unauthorized', status=401)
    else:
        return render(request, 'police_inner.html')


def logout_user(request):
    logout(request)

    return JsonResponse('logged out')


class CriminalsDataView(APIView):
    @csrf_exempt
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))

        # importing personal data of a criminal
        criminal = ch.criminal_detail_import(request_data)

        # finding facial metrics and importing them into DB
        face_detials = fe.Mesh(os.path.join(settings.BASE_DIR, criminal.picture.url[1:]))
        image_details = ch.image_detail_import(criminal.iin, face_detials)

        # creating normalized feature vector
        normalized_dict = ch.normalized_feature_array(image_details)

        response = {
            'left_brow_size': normalized_dict['left_brow_size'],
            'left_eye_size': normalized_dict['left_eye_size'],
            'lips_size': normalized_dict['lips_size'],
            'nose_length': normalized_dict['nose_len'],
            'nose_size': normalized_dict['nose_size'],
            'right_brow_size': normalized_dict['right_brow_size'],
            'right_eye_size': normalized_dict['right_eye_size']
        }

        return JsonResponse(response, safe=False)


class SearchCriminalsView(APIView):
    @csrf_exempt
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))

        search_dict = {
            'nose_len': request_data.get('nose_height'),
            'right_brow_size': request_data.get('right_brow'),
            'left_brow_size': request_data.get('left_brow'),
            'left_eye_size': request_data.get('left_eye'),
            'right_eye_size': request_data.get('right_eye'),
            'nose_size': request_data.get('nose_size'),
            'lips_size': request_data.get('mouth')
        }

        potential_suspects = sa.search_criminal(search_dict)

        suspects_data = []
        for suspect in potential_suspects:
            data = models.CriminalsData.objects.get(iin=suspect.iin)

            if data.gender == request_data.get('gender') or request_data.get('gender') == 'both':
                suspects_data.append(
                    {
                        'firstName': data.first_name,
                        'lastName': data.last_name,
                        'iin': data.iin,
                        'gender': data.gender,
                        'maritalStatus': data.martial_status,
                        'offense': data.offence,
                        'zipCode': data.zip_code,
                        'image': f'https://suspectsearch.pythonanywhere.com{data.picture.url}'
                    }
                )

        return JsonResponse(suspects_data, safe=False)


class GetCriminalsView(APIView):
    @csrf_exempt
    def get(self, request):
        response = []
        data = models.CriminalsData.objects.all()

        for criminal in data:
            response.append(
                {
                    'firstName': criminal.first_name,
                    'lastName': criminal.last_name,
                    'dob': criminal.dob,
                    'iin': criminal.iin,
                    'gender': criminal.gender,
                    'maritalStatus': criminal.martial_status,
                    'offense': criminal.offence,
                    'zipCode': criminal.zip_code,
                    'image': f'https://suspectsearch.pythonanywhere.com{criminal.picture.url}'
                }
            )

        return JsonResponse(response, safe=False)


class SearchByText(APIView):
    @csrf_exempt
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))
        suspects_data = []
        data = models.CriminalsData.objects.get(iin='000000000001')

        suspects_data.append(
            {
                'firstName': data.first_name,
                'lastName': data.last_name,
                'iin': data.iin,
                'maritalStatus': data.martial_status,
                'offense': data.offence,
                'zipCode': data.zip_code,
                'image': f'https://suspectsearch.pythonanywhere.com{data.picture.url}'
            }
        )
        logger.info(suspects_data)

        return JsonResponse(suspects_data, safe=False)


class AddPoliceman(APIView):
    @csrf_exempt
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))

        temp = models.CustomUser.objects.create(
            iin=request_data.get('iin'),
            first_name=request_data.get('first_name'),
            last_name=request_data.get('last_name'),
            dob=request_data.get('dob'),
            department=request_data.get('department'),
            badge_number=request_data.get('badge_number', '1'),
            role=request_data.get('role'),
            password=request_data.get('password'),
            username=request_data.get('iin')
        )

        return JsonResponse('saved', safe=False)


class Login(APIView):
    @csrf_exempt
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))

        user = models.CustomUser.objects.get(
            iin=request_data.get('iin'),
            password=request_data.get('password')
        )

        if user:
            return JsonResponse({
                'role': user.role,
                'name': f'{user.first_name} {user.last_name}'
            }, status=200, safe=False)
        else:
            return JsonResponse('Unauthorized', status=401, safe=False)


class EditCriminal(APIView):
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))
        try:
            criminal = models.CriminalsData.objects.get(iin=request_data.get('iin'))
            criminal.first_name = request_data.get('firstName')
            criminal.last_name = request_data.get('lastName')
            criminal.gender = request_data.get('gender')
            criminal.dob = request_data.get('dob')
            criminal.martial_status = request_data.get('maritalStatus')
            criminal.offence = request_data.get('offense')
            criminal.zip_code = request_data.get('zipCode')

            if request_data.get('image') is not None:
                image_data = request_data.get('image')
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]

                data = ContentFile(base64.b64decode(imgstr))
                file_name = f"{str(request_data.get('iin'))}." + ext
                criminal.picture.save(file_name, data, save=True)

                face_detials = fe.Mesh(os.path.join(settings.BASE_DIR, criminal.picture.url[1:]))
                ch.update_criminal(criminal.iin, face_detials)

            criminal.save()
            return JsonResponse('Updated', status=200, safe=False)
        except:
            return JsonResponse('Not found', status=404, safe=False)


class DeleteCriminal(APIView):
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))
        try:
            models.CriminalsData.objects.get(iin=request_data.get('iin')).delete()
            return JsonResponse('deleted', status=200, safe=False)
        except:
            return JsonResponse('Not found', status=404, safe=False)


class GetUsers(APIView):
    @csrf_exempt
    def get(self, request):
        response = []
        data = models.CustomUser.objects.all()

        for user in data:
            response.append(
                {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'iin': user.iin,
                    'dob': user.dob,
                    'department': user.department,
                    'badge_number': user.badge_number,
                    'role': user.role,
                    'password': user.password
                }
            )

        return JsonResponse(response, safe=False)


class EditUsers(APIView):
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))
        try:
            user = models.CustomUser.objects.get(iin=request_data.get('iin'))
            user.first_name = request_data.get('first_name')
            user.last_name = request_data.get('last_name')
            user.dob = request_data.get('dob')
            user.department = request_data.get('department')
            user.badge_number = request_data.get('badge_number')
            user.role = request_data.get('role')
            user.password = request_data.get('password')

            user.save()
            return JsonResponse('Updated', status=200, safe=False)
        except:
            return JsonResponse('Not found', status=404, safe=False)


class DeleteUsers(APIView):
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))
        try:
            models.CustomUser.objects.get(iin=request_data.get('iin')).delete()
            return JsonResponse('deleted', status=200, safe=False)
        except:
            return JsonResponse('Not found', status=404, safe=False)
