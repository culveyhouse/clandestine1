from django.core.management.base import BaseCommand, CommandError
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep, JobStatus
from datetime import datetime

class Command(BaseCommand):
    help = 'This command manages the entire HomeSnacks real estate data cycle'
    
    def add_arguments(self, parser):
        """ All optional arguemnts (--) """    
        parser.add_argument('--full',
            action='store_true',
            dest='full',
            default=False,
            help='Run the full data cycle normally, with all steps')
            
    def handle(self, *args, **options):
        if options['full']:
            
            self.stdout.write(self.style.SUCCESS('Starting the HomeSnacks data cycle'))   
            """ Add new data cycle to _datacycle table """
            dc = DataCycle.create()
            
            """ Step 1 : Prepare """
            """ Add a data cycle step to _datacyclestep table via a classmethod 
            and reference data_cycle_id foreign key in dc object """
            dc_step = DataCycleStep.create_step(DataCycleStep.STEP1_PREPARE, dc)
            self.stdout.write(self.style.SUCCESS('Data cycle step %s created for dc %s' % (dc_step.step_id, dc_step.data_cycle_id)))
            
            