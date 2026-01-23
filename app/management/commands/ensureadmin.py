from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Ensure default admin user exists with known password (dev only).'

    def handle(self, *args, **options):
        User = get_user_model()
        u, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
            },
        )
        u.is_superuser = True
        u.is_staff = True
        u.is_active = True
        u.set_password('123')
        u.save()
        self.stdout.write(self.style.SUCCESS(
            f"Admin ready. created={created}, username={u.username}"))
