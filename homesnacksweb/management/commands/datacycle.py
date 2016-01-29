from django.core.management.base import BaseCommand, CommandError
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep, JobStatus
from datetime import datetime

class Command(BaseCommand):
    help = 'This command manages the entire HomeSnacks real estate data cycle'
    
    def add_arguments(self, parser):
    # Named (optional) arguments
        parser.add_argument('--full',
            action='store_true',
            dest='full',
            default=False,
            help='Run the full data cycle normally, with all steps')
            
    def handle(self, *args, **options):
        if options['full']:
            self.stdout.write(self.style.SUCCESS('Starting the HomeSnacks data cycle'))   
            """Add new data cycle to database"""
            dc = DataCycle(data_cycle_start=datetime.now())
            dc.save()
            