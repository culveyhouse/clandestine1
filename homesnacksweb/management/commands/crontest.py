from django.core.management.base import BaseCommand, CommandError
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep


class Command(BaseCommand):
    help = 'Just a first test for db and Django core connectivity'

    def add_arguments(self, parser):
        parser.add_argument('mls_input_id', nargs='*', type=int)
            # Named (optional) arguments
        parser.add_argument('--const_test',
            action='store_true',
            dest='const_test',
            default=False,
            help='Execute the model class constants in different places')

    def handle(self, *args, **options):
        if options['const_test']:
            self.stdout.write(self.style.SUCCESS('Starting the class constant test'))
            Mlss = MLS.objects.get(pk=101)
            self.stdout.write(Mlss.mls_name)
           
        if options['mls_input_id']: 
            for mls_input_id in options['mls_input_id']:
                try:
                    MLSobj = MLS.objects.get(pk=mls_input_id)
                except MLS.DoesNotExist:
                    raise CommandError('MLS "%s" does not exist' % mls_input_id)
    
                name = MLSobj.mls_name 
    
                self.stdout.write(self.style.SUCCESS('Oh, MLS %s is %s' % (mls_input_id, name)))

