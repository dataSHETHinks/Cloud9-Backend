from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from rest_framework.parsers import JSONParser

from core.decorators import authenticate_user
from core.models import CustomUserRoles
from core.serializers import CustomUserRoleSerializer


UserModel = get_user_model()


@csrf_exempt
@require_GET
@authenticate_user
def get_user_roles(request, user, permissions):
    roles = CustomUserRoles.objects.all()
    data = CustomUserRoleSerializer(roles, many=True).data
    return JsonResponse({"data": data, "error": ""}, status=200)


@csrf_exempt
@require_POST
@authenticate_user
def add_new_user_role(request, user, permissions):
    message = ""
    error = ""
    status = 200
    if permissions.get("can_modify_roles"):
        try:
            data = JSONParser().parse(request)
            title = data.get("title")
            can_modify_module = data.get("can_modify_module")
            can_modify_category = data.get("can_modify_category")
            can_modify_user = data.get("can_modify_user")
            can_modify_roles = data.get("can_modify_roles")
            can_modify_files = data.get("can_modify_files")
            custom_user_role_obj = CustomUserRoles.objects.create(title=title, can_modify_user=can_modify_user,
                                                                  can_modify_category=can_modify_category,
                                                                  can_modify_module=can_modify_module,
                                                                  can_modify_files=can_modify_files,
                                                                  can_modify_roles=can_modify_roles)
            message = "Role added successfully."
        except Exception as e:
            error = str(e)
            status = 400

        return JsonResponse({"data": {"message": message}, "error": error}, status=status)
    else:
        error = "You do not have the permission to add new roles."
        status = 403
        return JsonResponse({"data": {}, "error": error}, status=status)


@csrf_exempt
@require_POST
@authenticate_user
def change_assigned_user_role(request, user, permissions):
    message = ""
    error = ""
    status = 200
    if permissions.get("can_modify_user"):
        try:
            data = JSONParser().parse(request)
            user = data.get('user_id')
            role = data.get('role_id')
            user_obj = UserModel.objects.get(pk=user)
            if role == "REMOVE_ROLE":
                user_obj.customuserroles_set.clear()
                message = "Role removed successfully."
                return JsonResponse({"data": {"message": message}, "error": error}, status=status)
            role_obj = CustomUserRoles.objects.get(pk=role)
            user_obj.customuserroles_set.clear()
            role_obj.user.add(user_obj)
            role_obj.save()
            message = "Role assigned successfully."
        except Exception as e:
            error = str(e)
            status = 400

        return JsonResponse({"data": {"message": message}, "error": error}, status=status)
    else:
        error = "You do not have the permission to change roles."
        status = 403
        return JsonResponse({"data": {}, "error": error}, status=status)