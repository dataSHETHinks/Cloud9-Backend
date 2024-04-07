from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from core.decorators import authenticate_user
from data.models import FileDataHistory, FileData
from data.serializers import FileDataHistoryIDSerializer, FileDataHistorySerializer


@csrf_exempt
@require_GET
@authenticate_user
def get_file_history_names(request, user, permissions):
    file_data = FileDataHistory.objects.all()
    data = FileDataHistoryIDSerializer(file_data, many=True).data
    return JsonResponse({"data": {"data": data}, "error": ""}, status=200)


@csrf_exempt
@require_GET
@authenticate_user
def get_history_file_data(request, user, permissions):
    file_id = request.GET.get('file_id')

    file_history = FileDataHistory.objects.get(pk=file_id)

    data = FileDataHistorySerializer(file_history, many=False).data
    return JsonResponse({"data": {"data": data}, "error": ""}, status=200)

