from rest_framework import serializers
from .models import Category, FileData, Module, FileDataHistory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name']


class FileDataIDSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    uploaded_at = serializers.SerializerMethodField()
    modified_at = serializers.SerializerMethodField()

    class Meta:
        model = FileData
        fields = ['id', 'title', 'category_name', 'uploaded_by_username', 'uploaded_at', 'modified_at', 'module_name']

    def get_uploaded_at(self, instance):
        return instance.uploaded_at.strftime('%m/%d/%y %H:%M')

    def get_modified_at(self, instance):
        return instance.modified_at.strftime('%m/%d/%y %H:%M')


class FileDataSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = FileData

        fields = ['id', 'title', 'data', 'category_name', 'uploaded_by_username', 'uploaded_at', 'modified_at',
                  'module_name']



class FileDataHistorySerializer(serializers.ModelSerializer):
    # parent_file_id = serializers.CharField(source='FileDataHistory.original_file', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = FileDataHistory
        fields = ['id', 'title', 'data', 'original_file', 'category_name', 'uploaded_by_username', 'uploaded_at',
                  'modified_at']


class FileDataHistoryIDSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    modified_at = serializers.SerializerMethodField()
    class Meta:
        model = FileDataHistory
        fields = ['id', 'title', 'uploaded_by_username', 'modified_at']

    def get_modified_at(self, instance):
        return instance.modified_at.strftime('%m/%d/%y %H:%M')
