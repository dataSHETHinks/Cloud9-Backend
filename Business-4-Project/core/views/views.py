from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from rest_framework.parsers import JSONParser

from core.decorators import authenticate_user
from core.models import CustomUserRoles
from core.serializers import UserSerializer, CustomUserRoleSerializer
from microservice_apis.send_emails.send_email import send_email

# Create your views here.

@csrf_exempt
@require_GET
@authenticate_user
def get_user_details(request, user, permissions):
    data = UserSerializer(user, many=False).data
    return JsonResponse({"data": data, "error": ""}, status=200)


@csrf_exempt
@authenticate_user
def user_list(request, user, **kwargs):
    try:
        if not user.is_staff:
            return JsonResponse({"data": "", "error": "You are not authorized to view this."}, status=403)

        try:
            users = UserModel.objects.all()
        except DatabaseError as db_error:
            return JsonResponse({"data": "", "error": f"Database error: {str(db_error)}"}, status=500)

        serializer = UserSerializer(users, many=True)
        user_list_data = serializer.data
        return JsonResponse({"data": {"user_list": user_list_data}, "error": ""}, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({"data": "", "error": "User does not exist."}, status=404)

    except Exception as e:
        return JsonResponse({"data": "", "error": str(e)}, status=500)


UserModel = get_user_model()


@csrf_exempt
@require_POST
@authenticate_user
def change_password(request, user, **kwargs):
    message = ""
    try:
        data = JSONParser().parse(request)
        new_password = data.get('password')

        if new_password:
            user.set_password(new_password)

            if data.get('fromForgetPassword'):
                user.is_password_reset = True
            user.is_password_reset = True
            user.save()

            message = "Password changed successfully."
            error = ""
        else:
            error = "New password not provided."
    except ObjectDoesNotExist:
        return JsonResponse({"data": "", "error": "User does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"data": "", "error": str(e)}, status=500)

    return JsonResponse({"data": {"message": message}, "error": error}, status=200)


@csrf_exempt
@require_POST
def forget_password(request):
    try:
        data = JSONParser().parse(request)
        username_or_email = data.get('usernameOrEmail')
        user_query_data = UserModel.objects.filter(Q(username=username_or_email) | Q(email=username_or_email))
        if user_query_data.exists():
            user_instance = user_query_data[0]
            code = user_instance.generate_forget_password_key()
            user_instance.is_password_reset = False
            user_instance.save()

            # Prepare email content
            subject = "Password Reset Code"
            # message = f"Your password reset code is: {code}"

            # Call send_email function
            if send_email(user_instance.email, subject, code, user_instance.username):
                message = "An email has been sent to you. Please enter the code to change your password."
                data = {"message": message, "username": user_instance.username}
                return JsonResponse({"data": data, "error": ""}, status=200)
            else:
                return JsonResponse({"data": "", "error": "Failed to send email. Please try again later."},
                                    status=500)
        else:
            return JsonResponse({"data": "", "error": "User not found. Please check your username or email."},
                                status=404)
    except Exception as e:
        return JsonResponse({"data": "", "error": str(e)}, status=500)


@csrf_exempt
@require_POST
@authenticate_user
def add_new_user(request, user, permissions):
    message = ""
    error = ""
    status = 200
    if permissions.get("can_modify_user"):
        try:
            data = JSONParser().parse(request)
            username = data.get("username")
            email = data.get("email")
            temp_password = data.get("temp_password")
            role = data.get("role")
            role_obj = CustomUserRoles.objects.get(pk=role)
            user_obj = UserModel.objects.create(username=username, email=email, customuserroles=role_obj)
            user_obj.set_password(temp_password)
            role_obj.user.add(user_obj)
            role_obj.save()
            user_obj.save()
            message = "User added successfully."
        except Exception as e:
            error = str(e)
            status = 400

        return JsonResponse({"data": {"message": message}, "error": error}, status=status)
    else:
        error = "You do not have the permission to add new users."
        status = 403
        return JsonResponse({"data": {}, "error": error}, status=status)


@csrf_exempt
@require_POST
@authenticate_user
def modify_user_status(request, user, permissions):
    message = ""
    error = ""
    status = 200
    if not permissions.get('can_modify_user'):
        error = "You do not have the permission to add/remove users."
        status = 403
        return JsonResponse({"data": {}, "error": error}, status=status)

    try:
        data = JSONParser().parse(request)
        user_id = data.get("user_id")
        delete_user = data.get("delete_user")
        user_obj = UserModel.objects.get(pk=user_id)
        user_obj.is_deleted = delete_user
        user_obj.customuserroles_set.clear()
        user_obj.save()
        message = "User status changed successfully."
    except Exception as e:
        error = str(e)
        status = 400

    return JsonResponse({"data": {"message": message}, "error": error}, status=status)
