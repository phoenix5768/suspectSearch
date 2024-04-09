from django.urls import path, include
# from django.conf.urls import url
from sketch.views import *

urlpatterns = [
    path('import-criminals/', CriminalsDataView.as_view(), name='home'),
    path('search-criminals/', SearchCriminalsView.as_view(), name='search-criminals'),
    path('get-criminals/', GetCriminalsView.as_view(), name='get-criminals'),
    path('search-by-text/', SearchByText.as_view(), name='search-by-text'),
    # path('admin_inner/', views.admin_inner, name='admin_inner'),
    # path('add_policeman/', views.add_policeman, name='add_policeman'),
    # path('police_home', views.police_home, name="police_home"),
]
