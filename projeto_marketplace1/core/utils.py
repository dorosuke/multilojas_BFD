from rest_framework.response import Response


def api_response(data=None, message='', success=True, status_code=200):
    return Response(
        {
            'success': success,
            'data': data if data is not None else {},
            'message': message,
        },
        status=status_code,
    )
