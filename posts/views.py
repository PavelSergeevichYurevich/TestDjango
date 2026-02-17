
from django.db import OperationalError, connection
from rest_framework.views import APIView
from rest_framework.response import Response


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            connection.ensure_connection()
            db_status = "ok"
        except OperationalError:
            db_status = "error"

        if db_status == "ok":
            return Response({"status": "ok"}, status=200)

        return Response({"status": "error"}, status=503)
