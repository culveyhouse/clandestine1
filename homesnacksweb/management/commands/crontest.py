from django.core.management.base import BaseCommand, CommandError
from homesnacksweb.models import MLS, PropertyCurrent


class Command(BaseCommand):
    help = 'Just a first test for db and Django core connectivity'

    def add_arguments(self, parser):
        parser.add_argument('mls_input_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for mls_input_id in options['mls_input_id']:
            try:
                MLSobj = MLS.objects.get(pk=mls_input_id)
            except MLS.DoesNotExist:
                raise CommandError('MLS "%s" does not exist' % mls_input_id)

            name = MLSobj.mls_name 

            self.stdout.write('Oh, MLS %s is %s' % (mls_input_id, name))

