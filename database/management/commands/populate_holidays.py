from django.core.management.base import BaseCommand
from datetime import datetime


class Command(BaseCommand):
    help = 'Popula la tabla Holiday para un país y años especificados (usa la librería `holidays`).\n\nEjemplo:\n  python manage.py populate_holidays --country PE --years 2024 2025'

    def add_arguments(self, parser):
        parser.add_argument('--country', default='PE', help='Código de país (ej: PE)')
        parser.add_argument('--years', nargs='*', type=int, help='Años a poblar (ej: 2024 2025)')

    def handle(self, *args, **options):
        country = options.get('country') or 'PE'
        years = options.get('years')
        if not years:
            years = [datetime.now().year]

        try:
            import holidays
        except Exception as e:
            self.stderr.write('La librería `holidays` no está instalada. Instálala con `pip install holidays`.')
            return

        try:
            from database.models import Holiday
        except Exception as e:
            self.stderr.write(f'No se pudo importar el modelo Holiday: {e}')
            return

        try:
            country_holidays = holidays.CountryHoliday(country, years=years)
        except Exception as e:
            self.stderr.write(f'Error al obtener feriados para {country}: {e}')
            return

        created = 0
        updated = 0
        for date, name in country_holidays.items():
            obj, was_created = Holiday.objects.update_or_create(fecha=date, defaults={'nombre': name})
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Feriados procesados: {created} creados, {updated} actualizados (pais={country}, years={years})'))
