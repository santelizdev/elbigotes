import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Espera a que la base de datos esté lista antes de arrancar procesos dependientes."

    def handle(self, *args, **options):
        self.stdout.write("Esperando disponibilidad de PostgreSQL/PostGIS...")
        connection = connections["default"]

        for attempt in range(1, 31):
            try:
                connection.ensure_connection()
            except OperationalError:
                self.stdout.write(f"Intento {attempt}/30 sin conexión. Reintentando...")
                time.sleep(2)
            else:
                self.stdout.write(self.style.SUCCESS("Base de datos disponible."))
                return

        raise OperationalError("No fue posible conectar con la base de datos.")

