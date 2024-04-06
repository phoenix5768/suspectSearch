from django.db import models


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


class Policeman(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    iin = models.CharField(primary_key=True, max_length=64)
    dob = models.DateField()
    department = models.CharField(max_length=256)
    badge_number = models.CharField(max_length=256)
    email = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    password = models.CharField(verbose_name='Password', max_length=256)

    def __str__(self):
        return self.first_name+ ' '+self.last_name


class Admin(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    iin = models.CharField(primary_key=True, max_length=64)
    email = models.CharField(max_length=256)
    #username = models.CharField(max_length=256)
    password = models.CharField(verbose_name='Password', max_length=256)
    def __str__(self):
        return self.first_name+ ' '+self.last_name


class Logs(models.Model):
    admin_logs = models.ForeignKey(Admin, on_delete=models.CASCADE)
    policeman_logs = models.ForeignKey(Policeman, on_delete=models.CASCADE)
    action_time = models.DateTimeField(editable=False, null=True, blank=True)
    action = models.TextField(null=True, blank=True)
