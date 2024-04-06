from rest_framework import serializers
from . models import *


class CriminalsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CriminalsData
        fields = ['iin', 'first_name', 'last_name', 'dob', 'martial_status', 'offence', 'zip_code']
