from django.urls import path

from .views import views, file_views, file_history_views

app_name = "data"

urlpatterns = [
    path('upload_file/', file_views.upload_file),
    path('export_file/', file_views.export_file),
    path('get_file_data/', file_views.get_file_data),
    path('get_file_history_names/', file_history_views.get_file_history_names),
    path('get_history_file_data/', file_history_views.get_history_file_data),
    path('get_file_names/', file_views.get_file_names),
    path('update_file_data/', file_views.update_file_data),

    path('get_file_categories/', views.get_file_categories),
    path('add_new_category/', views.add_new_category),

    path('get_file_modules/', views.get_file_modules),
    path('add_new_module/', views.add_file_module),

    path('filter_file_data/', file_views.filter_file_data, name='filter_file_data'),
    path('filter_by_column/', file_views.filter_file_data_by_column, name='filter_file_data_by_column'),

]
