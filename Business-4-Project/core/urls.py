from django.urls import path

from core.views import views, user_role_views

urlpatterns = [
    path('get_user_details/', views.get_user_details),
    path('get_users/', views.user_list),

    path('forget_password/', views.forget_password),
    path('change_password/', views.change_password),


    path('add_new_user_role/', user_role_views.add_new_user_role),
    path('get_user_roles/', user_role_views.get_user_roles),
    path('change_assigned_user_role/', user_role_views.change_assigned_user_role),

    path('add_new_user/', views.add_new_user),
    path('modify_user_status/', views.modify_user_status),
]
