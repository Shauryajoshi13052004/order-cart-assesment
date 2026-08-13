from django.core.management.base import BaseCommand
from orders.models import MenuItem


class Command(BaseCommand):
    help = 'Load sample menu items'

    def handle(self, *args, **kwargs):
        menu_items = [
            {
                'name': 'Margherita Pizza',
                'description': 'Classic pizza with tomato sauce, mozzarella cheese, and fresh basil',
                'price': 12.99,
                'image': 'https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400'
            },
            {
                'name': 'Pepperoni Pizza',
                'description': 'Pizza topped with pepperoni and mozzarella cheese',
                'price': 14.99,
                'image': 'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400'
            },
            {
                'name': 'Classic Burger',
                'description': 'Juicy beef patty with lettuce, tomato, onion, and special sauce',
                'price': 9.99,
                'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400'
            },
            {
                'name': 'Cheese Burger',
                'description': 'Beef patty with cheddar cheese, lettuce, and tomato',
                'price': 10.99,
                'image': 'https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400'
            },
            {
                'name': 'Caesar Salad',
                'description': 'Fresh romaine lettuce with parmesan cheese and croutons',
                'price': 8.99,
                'image': 'https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400'
            },
            {
                'name': 'Chicken Wings',
                'description': 'Crispy chicken wings with your choice of sauce',
                'price': 11.99,
                'image': 'https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=400'
            },
            {
                'name': 'Pasta Carbonara',
                'description': 'Creamy pasta with bacon, egg, and parmesan cheese',
                'price': 13.99,
                'image': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=400'
            },
            {
                'name': 'Fish and Chips',
                'description': 'Battered fish with crispy fries and tartar sauce',
                'price': 15.99,
                'image': 'https://images.unsplash.com/photo-1579208030886-b937da0925dc?w=400'
            },
        ]

        for item_data in menu_items:
            MenuItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample menu items'))
