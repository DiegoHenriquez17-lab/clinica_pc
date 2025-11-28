from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from recepcion.models import Cliente              # 👈 ahora Cliente
from .serializers import ClienteSerializer        # 👈 y su serializer


class ClienteViewSet(viewsets.ModelViewSet):
    """
    API REST para gestionar Clientes.

    Endpoints:
    - GET    /api/clientes/
    - POST   /api/clientes/
    - GET    /api/clientes/{id}/
    - PUT    /api/clientes/{id}/
    - PATCH  /api/clientes/{id}/
    - DELETE /api/clientes/{id}/
    """

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
