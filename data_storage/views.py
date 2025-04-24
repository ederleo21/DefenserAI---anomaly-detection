from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required, permission_required
from alerts.models import Alert
from io import BytesIO
from reportlab.pdfgen import canvas
import calendar
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from .models import Report
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from .models import Report

@login_required(login_url="accounts:login")
def main(request):
    alert_number = request.GET.get("alert_number")
    anomaly_type = request.GET.get("anomaly_type")
    confidence = request.GET.get("confidence")
    alert_date = request.GET.get("alert_date")

    alertas = Alert.objects.values(
        "id",
        "anomaly_type",
        "confidence",
        "frame_image",
        "timestamp",
        "created_by__username",
    )

    delete_alert = request.user.has_perm('alerts.delete_alert')
    view_alert = request.user.has_perm('alerts.view_alert')
    view_report = request.user.has_perm('data_storage.view_report')
    permissions = {
        'delete_alert' : delete_alert,
        'view_alert' : view_alert,
        'view_report' : view_report,
    }

    if alert_number:
        alertas = alertas.filter(id=alert_number)
    if anomaly_type:
        alertas = alertas.filter(anomaly_type__icontains=anomaly_type)
    if confidence:
        try:
            confidence_float = float(confidence)
            alertas = alertas.filter(confidence__gte=confidence_float / 100)
        except ValueError:
            pass
    if alert_date:
        alertas = alertas.filter(timestamp__date=alert_date)

    alertas_dict = list(alertas)
    for alerta in alertas_dict:
        alerta["confidence"] = int(round(alerta["confidence"] * 100, 2))

    return render(request, "data_storage/main.html", {"alertas_dict": alertas_dict, 'permissions': permissions})


@login_required(login_url="accounts:login")
def generar_informe(request):
    mes = int(request.POST.get("mes", 1))
    anio = int(request.POST.get("anio", 1))
    alertas = Alert.objects.filter(timestamp__year=anio, timestamp__month=mes)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(
        100, height - 80, f"Informe de Alertas - {calendar.month_name[mes]} {anio}"
    )
    p.setFont("Helvetica", 10)
    p.drawString(
        100,
        height - 100,
        "Este informe contiene un resumen detallado de las alertas registradas durante el mes seleccionado.",
    )
    p.drawString(
        100,
        height - 115,
        "A continuación, se listan los eventos capturados por el sistema de vigilancia en tiempo real.",
    )
    p.line(100, height - 130, width - 100, height - 130)

    y_position = height - 150
    for alerta in alertas:
        if y_position < 100:
            p.showPage()
            y_position = height - 100

        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.darkblue)
        p.drawString(100, y_position, f"Alerta ID: {alerta.id} - {alerta.anomaly_type}")
        y_position -= 15

        p.setFont("Helvetica", 10)
        p.setFillColor(colors.black)
        p.drawString(120, y_position, f"Confianza: {alerta.confidence * 100:.2f}%")
        y_position -= 15
        p.drawString(
            120,
            y_position,
            f"Fecha de Captura: {alerta.timestamp.strftime('%d/%m/%Y %H:%M:%S')}",
        )
        y_position -= 15
        p.drawString(
            120,
            y_position,
            f"Creado por: {alerta.created_by.username if alerta.created_by else 'Desconocido'}",
        )
        y_position -= 260

        if alerta.frame_image:
            image_path = alerta.frame_image.path
            try:

                image_height = 250
                image_width = 400
                p.drawImage(
                    image_path, 100, y_position, width=image_width, height=image_height
                )
            except Exception as e:
                print(f"Error al agregar la imagen de la alerta {alerta.id}: {e}")

        y_position -= 20

    p.showPage()
    p.save()

    buffer.seek(0)
    pdf_data = buffer.getvalue()

    report = Report(
        name=f"Informe de Alertas - {calendar.month_name[mes]} {anio}",
        description="Informe mensual detallado de alertas registradas en el sistema.",
        generated_at=datetime.now(),
    )
    report.pdf_file.save(f"informe_alertas_{mes}_{anio}.pdf", ContentFile(pdf_data))
    report.save()

    return HttpResponse(pdf_data, content_type="application/pdf")


@login_required(login_url="accounts:login")
def eliminar_alerta(request, alerta_id):
    alerta = get_object_or_404(Alert, id=alerta_id)
    alerta.delete()

    return redirect("data_storage:main")


def eliminar_reporte(request, reporte_id):
    reporte = get_object_or_404(Report, id=reporte_id)
    reporte.delete()
    return redirect("data_storage:reports")

@permission_required('data_storage.view_report', login_url='data_storage:main')
@login_required(login_url="accounts:login")
def lista_reportes(request):
    informes = Report.objects.all().order_by("-generated_at")
    delete_report = request.user.has_perm('data_storage.delete_report')
    permissions = {
        'delete_report' : delete_report,
    }
    return render(request, "data_storage/reports.html", {"informes": informes, 'permissions': permissions})
