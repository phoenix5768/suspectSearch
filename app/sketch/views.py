import base64
import json
import os

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

from app import settings


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
