from django.urls import path, include
# from django.conf.urls import url
from sketch.views import *

urlpatterns = [
    path('import-criminals/', CriminalsDataView.as_view(), name='home'),
    path('search-criminals/', SearchCriminalsView.as_view(), name='search-criminals'),
    path('get-criminals/', GetCriminalsView.as_view(), name='get-criminals'),
    path('search-by-text/', SearchByText.as_view(), name='search-by-text'),
    path('add_policeman/', AddPoliceman.as_view(), name='add-policeman'),
    path('admin_inner/', admin_inner, name='admin_inner'),
    path('police_inner/', police_inner, name='police_inner'),
    path('logout/', logout_user, name='logout'),
    path('signin/', Login.as_view(), name='signin')

]
