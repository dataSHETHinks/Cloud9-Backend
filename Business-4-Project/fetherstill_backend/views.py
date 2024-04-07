from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from core.decorators import authenticate_user

UserModel = get_user_model()

@csrf_exempt
@require_POST
@authenticate_user
def logout(request, user, permissions):
    user.user_verification_key = get_random_string(length=12)
    user.save()
    return JsonResponse({"data": {"message": "Logout success."}, "error": ""}, status=200)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        password = request.data['password']
        user_instance = authenticate(username=username, password=password)

        if user_instance is not None and not user_instance.is_password_reset and user_instance.key_expiry < timezone.now():
            custom_response = {
                "data": "",
                'error': "Key expired"
            }
            return Response(custom_response, status=401)

        if user_instance is None:
            custom_response = {
                "data": "",
                "error": "Please check your credentials"
            }
            return Response(custom_response, status=401)

        if user_instance.is_deleted:
            custom_response = {
                "data": "",
                "error": "Your account has been deactivated. Please contact admin if this was a mistake."
            }
            return Response(custom_response, status=401)

        response = super().post(request, *args, **kwargs)
        access_token = response.data.get('access')
        custom_response = {
            'data': {
                'access_token': access_token
            },
            'error': ''
        }
        return Response(custom_response)
