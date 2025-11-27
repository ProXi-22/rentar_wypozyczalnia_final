from django.apps import AppConfig


class RentarAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rentar_app'

    def ready(self):
        pass
