from django.apps import AppConfig


class DatabaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'database'
    
    def ready(self):
        # Intentamos registrar un handler post_migrate que poblará feriados
        # si la librería `holidays` está instalada. Usamos post_migrate para
        # que esto ocurra después de aplicar migraciones (no en import-time).
        try:
            from django.db.models.signals import post_migrate
            from django.dispatch import receiver
            import datetime

            @receiver(post_migrate)
            def _populate_holidays(sender, **kwargs):
                # Evitar ejecución durante ciertas tareas de tests o si no hay DB
                # Importamos localmente para evitar problemas al ejecutar makemigrations
                try:
                    import holidays
                except Exception:
                    # Si la librería no está instalada, no hacemos nada
                    return

                try:
                    from database.models import Holiday
                except Exception:
                    return

                # Poblar solo el año actual por defecto
                year = datetime.datetime.now().year
                try:
                    ch = holidays.CountryHoliday('PE', years=[year])
                except Exception:
                    return

                for date, name in ch.items():
                    try:
                        Holiday.objects.update_or_create(fecha=date, defaults={'nombre': name})
                    except Exception:
                        # Si falla por alguna razón (p. ej. migraciones en curso), ignorar
                        pass
        except Exception:
            # Si algo falla al registrar el receptor, no queremos romper el arranque
            pass
