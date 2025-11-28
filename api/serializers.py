from rest_framework import serializers
from recepcion.models import Cliente   # 👈 IMPORT CORRECTO


class ClienteSerializer(serializers.ModelSerializer):
    """
    Convierte objetos Cliente a JSON y viceversa.
    """

    class Meta:
        model = Cliente
        fields = "__all__"   # o una lista de campos si quieres limitar
