from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CameraForm
from .models import Camera
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import Group, Permission, User

@login_required(login_url='accounts:login')
def main(request):
    view_camera = request.user.has_perm('management.view_camera')
    view_user = request.user.has_perm('auth.view_user')
    permissions = {
        'view_camera' : view_camera,
        'view_user' : view_user,
    }
    return render(request, "management/main.html", {'permissions': permissions})


@login_required(login_url='accounts:login')
@permission_required('management.add_camera', login_url='management:list_cameras')
def register_camera(request):
    if request.method == 'POST':
        form = CameraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('management:list_cameras')
    else:
        form = CameraForm()

    return render(request, 'management/register_camera.html', {'form': form})


@login_required(login_url='accounts:login')
@permission_required('management.view_camera', login_url='management:main')
def list_cameras(request):
    cameras = Camera.objects.all()
    add_camera = request.user.has_perm('management.add_camera')
    change_camera = request.user.has_perm('management.change_camera')
    delete_camera = request.user.has_perm('management.delete_camera')
    permissions = {
        'add_camera' : add_camera,
        'change_camera' : change_camera,
        'delete_camera' : delete_camera
    }
    return render(request, 'management/list_cameras.html', {'cameras': cameras, 'permissions': permissions})


@login_required(login_url='accounts:login')
@permission_required('management.change_camera', login_url='management:list_cameras')
def update_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)

    if request.method == 'POST':
        form = CameraForm(request.POST, instance=camera)
        if form.is_valid():
            form.save()
            return redirect('management:list_cameras')
    else:
        form = CameraForm(instance=camera)

    return render(request, 'management/update_camera.html', {'form': form, 'camera': camera})


@login_required(login_url='accounts:login')
def delete_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    if request.method == 'POST':
        camera.delete()
        return redirect('management:list_cameras')
    return redirect('management:list_cameras')


def asignar_grupos_usuario(user_id, grupos):
    usuario = get_object_or_404(User, id=user_id)
    for nombre_grupo in grupos:
        grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
        usuario.groups.add(grupo)
    return usuario


def asignar_permisos_grupo(grupo_nombre, permisos):
    grupo, creado = Group.objects.get_or_create(name=grupo_nombre)
    for nombre_permiso in permisos:
        permiso = get_object_or_404(Permission, codename=nombre_permiso)
        grupo.permissions.add(permiso)
    return grupo


@permission_required('auth.change_user', login_url='management:main')
@login_required(login_url='accounts:login')
def manage_user_groups(request, user_id):
    user = User.objects.get(id=user_id)
    groups = Group.objects.all() 

    if request.method == 'POST':
        selected_groups = request.POST.getlist('groups')
        user.groups.set(selected_groups)  
        user.save()
        return redirect('management:user_list')

    return render(request, 'management/manage_user_groups.html', {
        'user': user,
        'groups': groups,
    })

@permission_required('auth.change_group', login_url='management:main')
@login_required(login_url='accounts:login')
def manage_group_permissions(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == "POST":
        selected_permissions = request.POST.getlist('permissions')
        group.permissions.clear()
        for perm_id in selected_permissions:
            permission = get_object_or_404(Permission, id=perm_id)
            group.permissions.add(permission)
        return redirect('management:user_list')

    all_permissions = Permission.objects.all()
    assigned_permissions = group.permissions.all()

    available_permissions = all_permissions.exclude(id__in=assigned_permissions.values_list('id', flat=True))

    return render(request, 'management/manage_group_permissions.html', {
        'group': group,
        'available_permissions': available_permissions,
        'assigned_permissions': assigned_permissions,
    })


def translate_permission_name(permission_name):
    translations = {
        "Can add log entry": "Puede agregar entrada de registro",
    }
    return translations.get(permission_name, permission_name)


@login_required(login_url='accounts:login')
def get_group_permissions(request):
    group_id = request.GET.get('group_id')
    group = get_object_or_404(Group, id=group_id)
    permissions = group.permissions.all()
    permissions_data = [{'id': perm.id, 'name': translate_permission_name(perm.name)} for perm in permissions]
    return JsonResponse({'permissions': permissions_data})


@login_required(login_url='accounts:login')
@permission_required('auth.view_user', login_url='management:main')
def user_list(request):
    users = User.objects.filter(is_superuser=False)
    change_user = request.user.has_perm('auth.change_user')
    change_group = request.user.has_perm('auth.change_group')
    permissions = {
        'change_user' : change_user,
        'change_group' : change_group,
    }
    groups = Group.objects.all()   
    return render(request, 'management/user_list.html', {'users': users,'groups': groups, 'permissions': permissions})




