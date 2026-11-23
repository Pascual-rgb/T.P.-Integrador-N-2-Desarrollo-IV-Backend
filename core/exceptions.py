from django.http import JsonResponse
from rest_framework.views import exception_handler


def manejador_errores(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    codigo = response.status_code
    data = response.data
    cuerpo = {'codigo': codigo}

    if codigo == 400:
        cuerpo['mensaje'] = 'Hay errores en los datos enviados.'
        cuerpo['detalles'] = data if isinstance(data, dict) else {'non_field_errors': data}
    else:
        detalle = data.get('detail') if isinstance(data, dict) else None
        cuerpo['mensaje'] = str(detalle) if detalle else 'Error en la solicitud.'

    response.data = {'error': cuerpo}
    return response


def error_404(request, exception=None):
    return JsonResponse(
        {'error': {'codigo': 404, 'mensaje': 'Recurso no encontrado.'}}, status=404
    )


def error_500(request):
    return JsonResponse(
        {'error': {'codigo': 500, 'mensaje': 'Error interno del servidor.'}}, status=500
    )