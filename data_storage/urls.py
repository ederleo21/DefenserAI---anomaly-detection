from django.urls import path
from .views import (
    main,
    generar_informe,
    lista_reportes,
    eliminar_alerta,
    eliminar_reporte,
)

app_name = "data_storage"

urlpatterns = [
    path("main/", main, name="main"),
    path("reports/", lista_reportes, name="reports"),
    path("generar_informe/", generar_informe, name="generar_informe"),
    path("eliminar_alerta/<int:alerta_id>/", eliminar_alerta, name="eliminar_alerta"),
    path("eliminar_reporte/<int:reporte_id>/", eliminar_reporte, name="eliminar_reporte"),
]

