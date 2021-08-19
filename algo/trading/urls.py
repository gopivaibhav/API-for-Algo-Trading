from django.urls import path
from .views import index,check

urlpatterns = [
    path('',index),
    path('<str:tit>',check)
]