from django.apps import AppConfig as DjangoAppConfig
from django.db.models.signals import post_migrate

class AppConfig(DjangoAppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = 'App'

    def ready(self):
        from .signals import ensure_admin_user
        post_migrate.connect(ensure_admin_user, sender=self)
