"""
URL mapping for the user API.
"""
from django .urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserAPIView.as_view(), name='create'),
    path('token/create/',
         views.CreateTokenAPIView.as_view(),
         name='token-create'),
    path('token/discard/',
         views.DiscardTokenAPIView.as_view(),
         name='token-discard'),
]
