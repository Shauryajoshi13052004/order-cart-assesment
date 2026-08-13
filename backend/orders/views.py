from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Sum
from .models import MenuItem, Order, OrderItem
from .serializers import (
    MenuItemSerializer, 
    OrderSerializer, 
    CreateOrderSerializer, 
    UpdateOrderStatusSerializer
)


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.filter(available=True)
    serializer_class = MenuItemSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '').strip()
        ordering = self.request.query_params.get('ordering', 'name')
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(description__icontains=search)
        return queryset.order_by(ordering if ordering in {'name', '-name', 'price', '-price'} else 'name')


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'

    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def insights(self, request):
        """Operational totals for the live order dashboard."""
        status_counts = {code: 0 for code, _ in Order.STATUS_CHOICES}
        status_counts.update(dict(Order.objects.values('status').annotate(total=Count('id')).values_list('status', 'total')))
        revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        return Response({
            'total_orders': Order.objects.count(),
            'total_revenue': revenue,
            'active_orders': Order.objects.exclude(status='delivered').count(),
            'status_counts': status_counts,
        })

    @action(detail=True, methods=['patch'])
    def update_status(self, request, id=None):
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        if serializer.is_valid():
            order.status = serializer.validated_data['status']
            order.save()
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def track(self, request, id=None):
        order = self.get_object()
        # Demo-friendly status simulation: each stage advances after 20 seconds.
        # A manually updated status is never moved backwards.
        stages = ['received', 'preparing', 'out_for_delivery', 'delivered']
        elapsed_stages = min(3, int((timezone.now() - order.created_at).total_seconds() // 20))
        if stages.index(order.status) < elapsed_stages:
            order.status = stages[elapsed_stages]
            order.save(update_fields=['status', 'updated_at'])
        serializer = OrderSerializer(order)
        return Response(serializer.data)
