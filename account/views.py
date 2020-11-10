from rest_framework import viewsets
from rest_framework import pagination
from rest_framework import filters

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from .models import Account
from .serializers import AccountSerializer, TransactionSerializer
from .actions import process_transaction


class AccountViewSet(viewsets.ModelViewSet):
    """Контроллер для работы с таблицей Account"""
    pagination_class = pagination.PageNumberPagination
    serializer_class = AccountSerializer
    queryset = Account.objects.all().order_by("inn")
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]

    search_fields = ('inn', 'user__login',)

    filterset_fields = ('inn', 'user__login',)

    # Method for transaction processing
    @action(methods=['POST'],
            detail=False,
            serializer_class=TransactionSerializer)
    def send_money(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = process_transaction(request.data["amount"],
                                     request.data["sender"],
                                     request.data["recipients"])
        return Response(report)
