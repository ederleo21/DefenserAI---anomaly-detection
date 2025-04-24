from django.urls import path
from .views import main, register_camera, list_cameras, update_camera, delete_camera, manage_user_groups, user_list, get_group_permissions, manage_group_permissions

app_name = 'management'

urlpatterns = [
    path('main/', main, name='main'),
    path('register_camera/', register_camera, name='register_camera'),
    path('list_cameras/', list_cameras, name='list_cameras'),
    path('update_camera/<int:camera_id>/', update_camera, name='update_camera'),
    path('delete_camera/<int:camera_id>/', delete_camera, name='delete_camera'),
    path('users/', user_list, name='user_list'),
    path('users/<int:user_id>/groups/', manage_user_groups, name='manage_user_groups'),
    path('groups/<int:group_id>/permissions/', manage_group_permissions, name='manage_group_permissions'),
    path('groups/get-permissions/', get_group_permissions, name='get_group_permissions'),
]
