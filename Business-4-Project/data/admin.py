from django.contrib import admin
from .models import Category, FileData, Module, FileDataHistory


# Register your models here.


class FileDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


class FileDataHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Category, CategoryAdmin)
admin.site.register(FileData, FileDataAdmin)
admin.site.register(FileDataHistory, FileDataHistoryAdmin)
admin.site.register(Module, ModuleAdmin)
