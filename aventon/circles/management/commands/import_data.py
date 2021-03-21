from django.core.management.base import BaseCommand
import csv
from aventon.circles.models import Circle


class Command(BaseCommand):
    help = 'importa datos relacionados a los circulos'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+', type=str)

        parser.add_argument(
            '--init',
            action='store_true',
            help='Agrega datos de prueba',
        )

    def handle(self, *args, **options):
        if options['init']:
            with open(options['file'][0], mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    circle = Circle(**row)
                    if int(circle.members_limit) > 0:
                        circle.is_limited = True
                    else:
                        circle.is_limited = False
                    circle.save()
                    print(circle.name)

        else:
            self.stdout.write('usa --init para cargar datos de prueba o --help para ayuda')
