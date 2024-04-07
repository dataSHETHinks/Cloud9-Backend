import csv
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException

import json
import pandas as pd

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from rest_framework.parsers import JSONParser

from core.decorators import authenticate_user
from data.models import FileData, Category, Module, FileDataHistory
from data.serializers import CategorySerializer, FileDataSerializer, FileDataIDSerializer, ModuleSerializer


# Create your views here.
@csrf_exempt
@require_GET
@authenticate_user
def get_file_categories(request, user, **kwargs):
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        category_data = serializer.data
        return JsonResponse({"data": {"data": category_data}, "error": ""}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"data": "", "error": "No file categories found."}, status=404)
    except Exception as e:
        return JsonResponse({"data": "", "error": f"Internal server error: {str(e)}"}, status=500)


@csrf_exempt
@require_POST
@authenticate_user
def add_new_category(request, user, **kwargs):
    data = JSONParser().parse(request)
    status = 200
    error = ""
    try:
        cat_name = data.get('name')
        cat = Category.objects.create(name=cat_name)
        message = "Category successfully added."

    except Exception as e:
        error = str(e)
        message = ""
        status = 400
    return JsonResponse({"data": {"message": message}, "error": error}, status=status)


@csrf_exempt
@require_GET
@authenticate_user
def get_file_modules(request, user, **kwargs):
    module_list = Module.objects.all()
    status = 200
    data = ModuleSerializer(module_list, many=True).data
    return JsonResponse({"data": {"data": data}, "error": ""}, status=status)


@csrf_exempt
@require_POST
@authenticate_user
def add_file_module(request, user, **kwargs):
    message = "Module added successfully."
    request_data = JSONParser().parse(request)
    error = ""
    status = 200
    try:
        module_name = request_data.get('name')
        module_obj = Module.objects.create(name=module_name)
        data = ModuleSerializer(module_obj, many=False).data
    except (IntegrityError, ValueError) as e:
        if type(e) == IntegrityError:
            error = "Module name should be unique"
        else:
            error = str(e)
        data = ""
        status = 400
        message = ""
    return JsonResponse({"data": {"data": data, "message": message}, "error": error}, status=status)
