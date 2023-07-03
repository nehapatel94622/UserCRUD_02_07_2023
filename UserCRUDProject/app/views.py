from django.shortcuts import render
from .models import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.hashers import make_password



#Create User View API
class SignupAPI(APIView):
    #Add User or Sign Up View
    def post(self, request, format=None):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                print(serializer.validated_data, "****")
                if request.data['password'] == request.data['confirm_password']:
                    user = serializer.save(
                        password=make_password(request.data['password']))
                    
                    user_token = Token.objects.create(user=user)
                    return Response({'status': True, 'message': 'User successfully registered'}, status=status.HTTP_201_CREATED)

                else:
                    return Response({'status': False, 'message': 'Password does not match'}, status=status.HTTP_400_BAD_REQUEST)
                    
            else:
                print(serializer.errors)
                return Response({'status': False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            if str(e.args[0]) == 'password':
                return Response({'password': "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
            elif str(e.args[0]) == 'confirm_password':
                return Response({'confirm_password': "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

#Create Sign In View API
class SigninAPI(APIView):
    def post(self, request, format=None):
        try:

            email = request.data['email']
            password = request.data['password']
            print(email)
            print(password)

            if UserModel.objects.get(email=email).is_active == True:
                print(True)
                auth_user = authenticate(email=email, password=password)
                print(auth_user)
                if auth_user is not None:
                    data = dict()
                    obj, _ = Token.objects.get_or_create(user=auth_user)
                    login(request, auth_user)
                   
                    data['id'] = auth_user.id
                    data['first_name'] = auth_user.first_name
                    data['last_name'] = auth_user.last_name
                    data['is_staff'] = auth_user.is_staff
                    data['is_superuser'] = auth_user.is_superuser
                    data['email'] = auth_user.email
                    data['token'] = obj.key
                    return Response({'status': True, 'data': data, 'message': 'User successfully logged in'}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': False, 'message': 'Invalid credentials!'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': False, 'message': 'Your account has been deactivated!'}, status=status.HTTP_400_BAD_REQUEST)
        except UserModel.DoesNotExist:
            return Response({'status': False, 'message': 'Invalid credentials!'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if str(e.args[0]) == 'email':
                return Response({'email': "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
            elif str(e.args[0]) == 'password':
                return Response({'password': "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                from traceback import format_exc
                print(format_exc(e))
                return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Create Logout View API
class LogoutAPI(APIView):
    def post(self, request, format=None):
        if request.user.is_authenticated:
            logout(request)
            return Response({'status': True, 'message': 'User successfully logged out'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'message': 'Login is required'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListAPI(APIView):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            users = UserModel.objects.all()
            serializer = UserListSerializer(users, many=True)
            return Response({'status': True, 'users': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
class ProfileViewAPI(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                get_profile = ProfileModel.objects.get(user=request.user)
                serializer = ProfileSerializer(
                    get_profile, context={'request': request})
                return Response({'status': True, 'data': serializer.data, 'message': 'Profile successfully displayed'}, status=status.HTTP_200_OK)
            except:
                return Response({'status': False, 'message': "Profile does not exist for this user"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'status': False, 'message': "Login is required"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        user =request.user
        print(user)
        if user.is_authenticated and user.is_active:
            serializer = ProfileSerializer(data = {**request.data, "user":request.user.id})
            if serializer.is_valid():
                email = user.email
                if ProfileModel.objects.filter(user__email=email).exists():
                    return Response({"status": False, "message": "user profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()  # Pass the user object instead of the user ID
                return Response({"status": True, "message": "User profile added"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": False, "message": serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"status": False, "message": "Authentication token is not set properly"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, pk=None, format=None):
        if request.user.is_authenticated:
            try:
                get_address = ProfileModel.objects.get(
                    user__id=request.user.id)
                serializer = ProfileSerializer(get_address, data=request.data, context={
                                               'request': request}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    request.user.first_name = request.data['first_name'] if 'first_name' in request.data.keys(
                    ) else None
                    request.user.last_name = request.data['last_name'] if 'last_name' in request.data.keys(
                    ) else None
                    request.user.save()
                    return Response({'status': True, 'data': serializer.data, 'message': 'Profile successfully updated'}, status=status.HTTP_200_OK)
                else:
                    first_error = list(serializer.errors.values())[0]
                    error_msg = first_error[0] if type(
                        first_error) == list else first_error
                    return Response({'status': False, 'message': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            except ProfileModel.DoesNotExist:
                return Response({'status': False, 'message': "Profile does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({'status': False, 'message': "Login is required"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        if request.user.is_authenticated:
            try:
                get_profile = ProfileModel.objects.get(user=request.user)
                get_profile.delete()
                return Response({'status': True, 'message': 'Profile Deleted'}, status=status.HTTP_200_OK)
            except:
                return Response({'status': False, 'message': "Profile does not exist for this user"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'status': False, 'message': "Login is required"}, status=status.HTTP_401_UNAUTHORIZED)
