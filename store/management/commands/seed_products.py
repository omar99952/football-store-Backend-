from django.core.management.base import BaseCommand
from store.models import Product  

class Command(BaseCommand):
    help = 'Seeds the database with football boots'

    def handle(self, *args, **kwargs):
        boots = [
            {
                "name": "Adidas F50 Elite",
                "brand": "Adidas",
                "price": 259.99,
                "image": "https://assets.adidas.com/images/w_1880,f_auto,q_auto/91f142e473404e57bc06ace8ab1101c5_9366/JH7615_HM1.jpg",
                "description": "Engineered for speed and precision on firm ground."
            },
            {
                "name": "Nike Mercurial Superfly",
                "brand": "Nike",
                "price": 279.50,
                "image": "https://example.com/mercurial.jpg",
                "description": "The choice of elite players for explosive acceleration."
            },
            {
                "name": "Puma Future Ultimate",
                "brand": "Puma",
                "price": 220.00,
                "image": "https://example.com/puma-future.jpg",
                "description": "Adaptive fit with FUZIONFIT+ technology for total control."
            },
            {
                "name": "NB Tekela V4+",
                "brand": "New Balance",
                "price": 210.00,
                "image": "https://example.com/nb-tekela.jpg",
                "description": "Laceless design for a pure striking surface."
            }
        ]

        for boot in boots:
            obj, created = Product.objects.get_or_create(
                name=boot['name'],
                defaults={
                    'brand': boot['brand'],
                    'price': boot['price'],
                    'image': boot['image'],
                    'description': boot['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Created {boot['name']}"))
            else:
                self.stdout.write(f"ℹ {boot['name']} already exists.")

        self.stdout.write(self.style.SUCCESS('--- Seeding Complete ---'))