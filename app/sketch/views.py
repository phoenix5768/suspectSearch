import base64
import json
import ujson

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpRequest
from django.contrib.auth.decorators import user_passes_test

from . import models
from .forms import CriminalsDataForm
from .models import CriminalsData
from sketch.ml import feature_extraction as fe
from sketch.handlers import criminals_handler as ch
from loguru import logger
from django.db.models import QuerySet, Q
from sketch.ml import search_algorithm as sa

from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt


def admin_login_view(request):
    # Logic for admin login page
    return render(request, 'admin_login.html')


class CriminalsDataView(APIView):
    @csrf_exempt
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))

        # importing personal data of a criminal
        criminal = ch.criminal_detail_import(request_data)

        # finding facial metrics and importing them into DB
        face_detials = fe.Mesh(f'/home/phoenix/education/SeniorProject/suspectSearch/app{criminal.picture.url}')
        image_details = ch.image_detail_import(criminal.iin, face_detials)

        # creating normalized feature vector
        ch.normalized_feature_array(image_details)

        resp = {
            'iin': request_data.get('iin'),
            'firstName': request_data.get('firstName'),
            'lastName': request_data.get('lastName'),
            'dob': request_data.get('dob'),
            'maritalStatus': request_data.get('maritalStatus'),
            'offense': request_data.get('offense'),
            'zipCode': request_data.get('zipCode'),
            'picture': request_data.get('picture')
        }

        return JsonResponse(resp, safe=False)


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
            image_data = data.picture.read()
            encoded_image_data = base64.b64encode(image_data).decode('utf-8')

            suspects_data.append(
                {
                    'firstName': data.first_name,
                    'lastName': data.last_name,
                    'iin': data.iin,
                    'maritalStatus': data.martial_status,
                    'offense': data.offence,
                    'zipCode': data.zip_code,
                    'image': encoded_image_data
                }
            )

        return JsonResponse(ujson.dumps(suspects_data), safe=False)


class GetCriminalsView(APIView):
    @csrf_exempt
    def get(self, request):
        response = []
        data = models.CriminalsData.objects.all()
        for criminal in data:
            image_data = criminal.picture.read()
            encoded_image_data = base64.b64encode(image_data).decode('utf-8')

            response.append(
                {
                    'firstName': criminal.first_name,
                    'lastName': criminal.last_name,
                    'iin': criminal.iin,
                    'maritalStatus': criminal.martial_status,
                    'offense': criminal.offence,
                    'zipCode': criminal.zip_code
                }
            )

        resp = ujson.dumps(response)
        logger.info(resp)

        return JsonResponse(resp, safe=False)


def import_criminals(request):
    if request.method == "POST":
        form = CriminalsDataForm(request.POST, request.FILES)
        if form.is_valid():
            form_data = form.cleaned_data
            iin = form_data.get('iin')
            form.save()

            criminal = CriminalsData.objects.get(iin=iin)
            face_detials = fe.Mesh(f'/home/phoenix/senior-project/app{criminal.picture.url}')
            ch.image_detail_import(iin, face_detials)
            messages.success(request, 'success')
            return redirect('cry')
    else:
        form = CriminalsDataForm()

    return render(request, 'import_criminals.html', {'form': form})



# def admin_inner(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(request, email=email, password=password)
#         if user is not None and user.is_superuser:
#             login(request, user)
#             return render(request, 'admin_inner.html')
#         else:
#             return HttpResponse('Unauthorized', status=401)
#     else:
#         return render(request, 'admin_inner.html')
#
#
# def police_home(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None and (not user.is_superuser):
#             login(request, user)
#             return render(request, 'police_home.html')
#         else:
#             return HttpResponse('Unauthorized', status=401)
#     else:
#         return render(request, 'police_home.html')
#
#
# def add_policeman(request):
#     if request.method == "POST":
#         form = PolicemanForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Policeman is added successfully')
#             return redirect('add_policeman')
#     else:
#         form = PolicemanForm()
#     return render(request, 'add_policeman.html', {'form': form})
#
