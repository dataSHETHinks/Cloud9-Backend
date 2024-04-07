import csv
import json
from datetime import datetime


import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from openpyxl.workbook import Workbook
from rest_framework.parsers import JSONParser

from core.decorators import authenticate_user
from data.models import Category, Module, FileData, FileDataHistory
from data.serializers import FileDataSerializer, FileDataIDSerializer


@csrf_exempt
@require_POST
@authenticate_user
def update_file_data(request, user, permissions):
    message = ''
    error = ''
    status = 200
    if not permissions.get('can_modify_files'):
        status = 401
        error = "You are not authorized to perform this action."
        return JsonResponse({"data": "", "error": error}, status=status)

    try:
        data = JSONParser().parse(request)
        file_id = data.get('file_id')
        row_num = data.get('row_num')
        row_data = data.get('row_data')

        file_obj = FileData.objects.get(pk=file_id)
        file_history_obj = FileDataHistory.objects.create(title=file_obj.title, data=file_obj.data, original_file=file_obj,
                                                          uploaded_by=user)
        data = file_obj.data
        data[row_num] = json.loads(row_data)
        file_obj.save()

        message = 'Data updated successfully.'
    except Exception as e:
        message = ''
        error = str(e)
        status = 400
    return JsonResponse({"data": {"message": message}, "error": error}, status=status)


@csrf_exempt
@require_GET
@authenticate_user
def get_file_names(request, user, **kwargs):
    try:
        file_data = FileData.objects.filter().order_by('-modified_at')
        serializer = FileDataIDSerializer(file_data, many=True)
        data = serializer.data
        return JsonResponse({"data": {"data": data}, "error": ""}, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({"data": "", "error": "No file names found."}, status=404)
    except Exception as e:
        return JsonResponse({"data": "", "error": f"Internal server error: {str(e)}"}, status=500)


@csrf_exempt
@require_POST
@authenticate_user
def export_file(request, user, permissions):
    data = JSONParser().parse(request)
    export_type = data.get('export_type')
    file_id = data.get('file_id')
    file_obj = FileData.objects.get(pk=file_id)
    file_data = file_obj.data
    if export_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'

        writer = csv.DictWriter(response, fieldnames=file_data['1'].keys())
        writer.writeheader()

        for row in file_data.values():
            writer.writerow(row)

        return response
    elif export_type == 'xlsx':
        wb = Workbook()
        ws = wb.active

        columns = list(file_data.values())[0].keys()
        ws.append(list(columns))

        for row in file_data.values():
            ws.append(list(row.values()))

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="exported_data.xlsx"'

        wb.save(response)
        return response
    else:
        return JsonResponse({"data": "", "error": "File type is not supported."}, status=415)


@csrf_exempt
@require_POST
@authenticate_user
def upload_file(request, user, permissions):
    if 'update_value' in request.POST:
        file_data_id = request.POST.get('file_data_id')
        row_number = int(request.POST.get('row_number'))
        column_name = request.POST.get('column_name')
        new_value = request.POST.get('new_value')

        try:
            file_data = FileData.objects.get(pk=file_data_id)
        except FileData.DoesNotExist:
            return JsonResponse({"data": "", "error": "File data not found."}, status=404)

        # Update the specific value in the data
        file_data.data[str(row_number)][column_name] = new_value
        file_data.save()

        return JsonResponse({"data": {"message": "File data updated successfully."}, "error": ""}, status=200)
    else:
        try:
            file_title = request.POST.get('file_name')
            file_type = request.POST.get('file_type')
            uploaded_file = request.FILES.get('uploaded_file')

            if file_type == "csv":
                print("inside csv")
                processed_data = process_file(uploaded_file)
            elif file_type == "xlsx":
                processed_data = process_xlsx_file_new(uploaded_file)
            else:
                return JsonResponse({"data": "", "error": "File type is not supported."}, status=415)
            category_id = request.POST.get('file_category')
            module_id = request.POST.get('file_module')
            try:
                category_obj = Category.objects.get(pk=category_id)
                module_obj = Module.objects.get(pk=module_id)
            except ObjectDoesNotExist:
                return JsonResponse({"data": "", "error": "Module or Category ID not found."}, status=404)

            file_data_object = FileData.objects.create(title=file_title, category=category_obj, data=processed_data, uploaded_by=user,
                                        module=module_obj)

            message = "File processed successfully."
            return JsonResponse({"data": {"message": message}, "error": ""}, status=200)
        except Exception as e:
            return JsonResponse({"data": "", "error": {str(e)}}, status=500)


def process_xlsx_file_new(uploaded_file):
    error = ""
    try:
        df = pd.read_excel(uploaded_file)
        data = df.to_dict(orient='records')
        count = 1
        json_data = {}
        for row in data:
            json_data[count] = row
            count += 1
        return json_data
    except Exception as e:
        error = f"Error processing the XLSX file: {str(e)}"
    return JsonResponse({"data": "", "error": error}, status=500)


def process_file(uploaded_file):
    try:
        content = uploaded_file.read().decode('utf-8')
        csv_reader = csv.DictReader(content.splitlines())

        count = 1
        json_data = {}
        for row in csv_reader:
            json_data[count] = row
            count += 1
        return json_data
    except UnicodeDecodeError:
        error = "Invalid file encoding. The file should be in UTF-8 encoding."
    except csv.Error as e:
        error = f"CSV parsing error: {str(e)}"
    except Exception as e:
        error = f"Error processing the CSV file: {str(e)}"
    return JsonResponse({"data": "", "error": error}, status=500)


@csrf_exempt
@require_GET
@authenticate_user
def get_file_data(request, user, **kwargs):
    try:
        file_id = request.GET.get('id', None)

        if file_id is None:
            return JsonResponse({"data": "", "error": "Missing 'id' parameter in the request."}, status=400)

        try:
            file_data = FileData.objects.get(pk=file_id)
            serializer = FileDataSerializer(file_data, many=False)
            data = serializer.data
            return JsonResponse({"data": {"data": data}, "error": ""}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"data": "", "error": f"File with ID {file_id} not found."}, status=404)
    except Exception as e:
        return JsonResponse({"data": "", "error": str(e)}, status=500)






@csrf_exempt
@require_GET
@authenticate_user
def filter_file_data(request, user, **kwargs):
    module_id = request.GET.get('module_id')
    category_id = request.GET.get('category_id')

    if not module_id and not category_id:
        return JsonResponse({"data": "", "error": "No filtering parameters provided."}, status=400)

    file_qs = FileData.objects.all()

    if module_id:
        module_obj = get_object_or_404(Module, pk=module_id)
        file_qs = file_qs.filter(module=module_obj)

    if category_id:
        category_obj = get_object_or_404(Category, pk=category_id)
        file_qs = file_qs.filter(category=category_obj)

    data = FileDataSerializer(file_qs, many=True).data
    return JsonResponse({"data": data, "error": ""}, status=200)


@csrf_exempt
@require_GET
@authenticate_user
def filter_file_data_by_column(request, user, **kwargs):
    try:
        file_id = request.GET.get('id', None)
        column_name = request.GET.get('column_name', None)
        filter_type = request.GET.get('filter_type', None)
        filter_value = request.GET.get('filter_value', None)

        if file_id is None or column_name is None or filter_type is None or filter_value is None:
            return JsonResponse({"data": "", "error": "Missing required parameters in the request."}, status=400)

        try:
            file_data = FileData.objects.get(pk=file_id)
            filtered_data = file_data.data

            if filter_type == 'range':
                filter_values = [float(val) for val in filter_value.split('-')]
                filtered_data = {
                    row_num: row_data for row_num, row_data in filtered_data.items()
                    if filter_values[0] <= float(row_data.get(column_name, 0)) <= filter_values[1]
                }
            elif filter_type == 'date_range':
                filter_values = [datetime.strptime(val, '%Y-%m-%d').date() for val in filter_value.split('-')]
                filtered_data = {
                    row_num: row_data for row_num, row_data in filtered_data.items()
                    if filter_values[0] <= datetime.strptime(row_data.get(column_name, ''), '%Y-%m-%d').date() <= filter_values[1]
                }
            elif filter_type == 'value':
                filtered_data = {
                    row_num: row_data for row_num, row_data in filtered_data.items()
                    if str(row_data.get(column_name, '')) == filter_value
                }
            else:
                pass

            return JsonResponse({"data": {"filtered_data": filtered_data}, "error": ""}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"data": "", "error": f"File with ID {file_id} not found."}, status=404)
    except Exception as e:
        return JsonResponse({"data": "", "error": str(e)}, status=500)
