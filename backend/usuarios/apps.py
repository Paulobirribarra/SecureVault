from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usuarios"
    verbose_name = "Gestión de Usuarios"
    
    def ready(self):
        """Importa los signals cuando la app esté lista."""
        import usuarios.signals
