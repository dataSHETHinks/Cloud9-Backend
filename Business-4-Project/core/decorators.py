from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

UserModel = get_user_model()


def authenticate_user(view_function):
    def wrapper(request, *args, **kwargs):
        try:
            # Authenticate the request using your JWT authentication logic
            user = JWTAuthentication().authenticate(request)
            if user:
                user_obj = user[0]
                if user_obj.is_deleted:
                    return JsonResponse({"data": ""
                                            ,"error": "Your account has been removed. Please contact admin if this was a mistake."}, status=404)

                provided_verification_key = user[1].get('user_verification_key')
                if user_obj.user_verification_key != provided_verification_key:
                    return JsonResponse({"data": "","error": "Please login again."}, status=404)
                

                user_roles = user_obj.customuserroles_set.all()
                permissions = get_combined_permissions(user_roles)
                kwargs['user'] = user_obj
                kwargs['permissions'] = permissions
            else:
                return JsonResponse({"data": "", "error": "Please login."}, status=401)
        except InvalidToken as e:
            return JsonResponse({"data": "", "error": "Token Expired. Please login again."}, status=401)

        # Call the view function with the updated arguments
        return view_function(request, *args, **kwargs)

    return wrapper


def get_combined_permissions(user_roles):
    combined_permissions = {
        "can_modify_module": False,
        "can_modify_category": False,
        "can_modify_user": False,
        "can_modify_roles": False,
        "can_modify_files": False
        # Add more permissions as needed
    }

    for role in user_roles:
        combined_permissions["can_modify_module"] = combined_permissions["can_modify_module"] or role.can_modify_module
        combined_permissions["can_modify_category"] = combined_permissions[
                                                          "can_modify_category"] or role.can_modify_category
        combined_permissions["can_modify_user"] = combined_permissions["can_modify_user"] or role.can_modify_user
        combined_permissions["can_modify_roles"] = combined_permissions["can_modify_roles"] or role.can_modify_roles
        combined_permissions["can_modify_files"] = combined_permissions["can_modify_files"] or role.can_modify_files

    return combined_permissions
