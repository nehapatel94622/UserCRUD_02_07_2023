
from django.urls import path
from .views import *


urlpatterns = [
    # --------- Auth urls ------------
    path('signup/', SignupAPI.as_view(), name='signup'),
    path('signin/', SigninAPI.as_view(), name='signin'),
    path('logout/', LogoutAPI.as_view(), name='logout'),

 
    path('profile/', ProfileViewAPI.as_view(), name='profile'),
    path('profile/<int:pk>/', ProfileViewAPI.as_view(), name='profile'),

    path('userlist/', UserListAPI.as_view(), name='userlist'),

]