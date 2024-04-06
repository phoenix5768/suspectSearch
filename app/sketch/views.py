from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpRequest
from django.contrib.auth.decorators import user_passes_test
from .forms import PolicemanForm, CriminalsDataForm
from .models import CriminalsData
from sketch.ml import feature_extraction as fe
from sketch.handlers import criminals_handler as ch
from loguru import logger

from . serializer import *
from rest_framework.response import Response
from rest_framework.views import APIView
import ujson

def admin_login_view(request):
    # Logic for admin login page
    return render(request, 'admin_login.html')


class CriminalsDataView(APIView):
    def post(self, request):
        request_data = ujson.loads(request.body.decode('utf-8'))

        # importing personal data of a criminal
        criminal = ch.criminal_detail_import(request_data)

        # finding facial metrics and importing them into DB
        face_detials = fe.Mesh(f'/home/phoenix/SP_new/app{criminal.picture.url}')
        ch.image_detail_import(criminal.iin, face_detials)

        # creating normalized feature vector
        ch.normalized_feature_array(request_data.get('iin'))

        resp = {
            'iin': request_data.get('iin'),
            'first_name': request_data.get('firstName'),
            'last_name': request_data.get('lastName'),
            'dob': request_data.get('dob'),
            'martial_status': request_data.get('maritalStatus'),
            'offence': request_data.get('offense'),
            'zip_code': request_data.get('zipCode'),
            'picture': request_data.get('picture')
        }

        return JsonResponse(resp)


class SearchCriminalsView(APIView):
    def post(self, request):
        return JsonResponse("message: Success")




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
#
# def home(request):
#     return render(request, 'home.html', {})
