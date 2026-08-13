from django.db import transaction
from rest_framework import serializers
from .models import MenuItem, Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'available']
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_price = serializers.DecimalField(source='menu_item.price', read_only=True, max_digits=6, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'menu_item_price', 'quantity', 'price']
        read_only_fields = ['id', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'customer_address', 'customer_phone', 
                  'status', 'status_display', 'total_amount', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_address', 'customer_phone', 'items']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        for item in value:
            if 'menu_item_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError("Each item must have menu_item_id and quantity.")
            if not isinstance(item['quantity'], int) or isinstance(item['quantity'], bool) or item['quantity'] < 1:
                raise serializers.ValidationError("Quantity must be at least 1.")
            if not isinstance(item['menu_item_id'], int) or isinstance(item['menu_item_id'], bool):
                raise serializers.ValidationError("menu_item_id must be an integer.")
        menu_ids = {item['menu_item_id'] for item in value}
        available_ids = set(MenuItem.objects.filter(id__in=menu_ids, available=True).values_list('id', flat=True))
        if menu_ids != available_ids:
            raise serializers.ValidationError("One or more selected menu items are unavailable.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in items_data:
            menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
            quantity = item_data['quantity']
            price = menu_item.price * quantity
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=price
            )
            total_amount += price
        
        order.total_amount = total_amount
        order.save()
        return order


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
