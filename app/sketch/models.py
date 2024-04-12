from django.db import models
from django.contrib.auth.models import AbstractUser


class CriminalsData(models.Model):
    iin = models.CharField(primary_key=True, verbose_name='Personal Identification Number', max_length=64)
    first_name = models.CharField(verbose_name='First Name', max_length=128)
    last_name = models.CharField(verbose_name='Last Name', max_length=128)
    gender = models.CharField(verbose_name='Gender', max_length=32, blank=True, null=True)
    dob = models.DateField(verbose_name='Date of birth')
    martial_status = models.CharField(verbose_name='Martial Status', max_length=128)
    offence = models.CharField(verbose_name='Charged offence', max_length=256)
    zip_code = models.CharField(verbose_name='Zip code', max_length=64)
    picture = models.ImageField(null=True, blank=True, upload_to='images/')

    class Meta:
        verbose_name = "Criminal's Personal Data"
        verbose_name_plural = "Criminals' Personal Data"

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' ' + self.iin


class CriminalsImage(models.Model):
    iin = models.ForeignKey(CriminalsData, on_delete=models.CASCADE)
    nose_len = models.FloatField(default=0)
    right_brow_size = models.FloatField(default=0)
    left_brow_size = models.FloatField(default=0)
    left_eye_size = models.FloatField(default=0)
    right_eye_size = models.FloatField(default=0)
    nose_size = models.FloatField(default=0)
    lips_size = models.FloatField(default=0)
    normalized_feature = models.JSONField(verbose_name='Normalized Feature Array', null=True, blank=True)

    class Meta:
        verbose_name = "Criminal's Image Detail"
        verbose_name_plural = "Criminals' Image Details"

    def __str__(self):
        return self.iin.first_name + ' ' + self.iin.last_name


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    iin = models.CharField(primary_key=True, max_length=64)
    dob = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=256, null=True, blank=True)
    badge_number = models.CharField(max_length=256, null=True, blank=True)
    role = models.CharField(max_length=256)

    def is_policeman(self):
        return self.role == "policeman"

    def is_admin(self):
        return self.role == "admin"

    def __str__(self):
        return self.first_name + ' ' + self.last_name


# class Logs(models.Model):
#     user_logs = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     action_time = models.DateTimeField(editable=False, null=True, blank=True)
#     action = models.TextField(null=True, blank=True)


class MaxMin(models.Model):
    func_name = models.CharField(verbose_name='Max or Min', max_length=32, default='max')
    nose_len = models.FloatField(default=0)
    right_brow_size = models.FloatField(default=0)
    left_brow_size = models.FloatField(default=0)
    left_eye_size = models.FloatField(default=0)
    right_eye_size = models.FloatField(default=0)
    nose_size = models.FloatField(default=0)
    lips_size = models.FloatField(default=0)

    def __str__(self):
        return self.func_name
