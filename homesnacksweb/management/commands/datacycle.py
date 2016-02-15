from django.core.management.base import BaseCommand, CommandError
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep, JobStatus
from datetime import datetime

class Command(BaseCommand):
    help = 'This command manages the entire HomeSnacks real estate data cycle'
    
    def add_arguments(self, parser):
        """ All optional arguments (--) """    
        parser.add_argument('--full',
            action='store_true',
            dest='full',
            default=False,
            help='Run the full data cycle normally, with all steps')
            
        parser.add_argument('--steps',
            nargs='+',
            type=int,
            dest='steps',
            default=False,
            help='Run a specific selection of steps within the data cycle')

            
    def handle(self, *args, **options):

        if options['full'] or (DataCycleStep.STEP1_PREPARE in options['steps']):            
            self.stdout.write(self.style.SUCCESS('Starting the HomeSnacks data cycle'))   
            """ Add new data cycle to _datacycle table """
            dc = DataCycle.create()


            """ Step 1 : Prepare """
            self.stdout.write(self.style.SUCCESS('Executing Step 1: Prepare'))
            """ Add a data cycle step to _datacyclestep table via a classmethod 
            and reference data_cycle_id foreign key in dc object """
            dc_step = DataCycleStep.create_step(DataCycleStep.STEP1_PREPARE, dc)
            self.stdout.write(self.style.SUCCESS('Data cycle step %s created for dc %s' % (dc_step.step_id, dc.id)))
            
            """ pseudo: Finish up any other preparations, then move on to step 2 """
        
        elif options['steps']:
            self.stdout.write(self.style.SUCCESS('Grabbing the most recent data cycle'))   
            dc = DataCycle.objects.latest('id')
            
        if options['full'] or (DataCycleStep.STEP2_DOWNLOAD in options['steps']):      
            
            """ Step 2 : Download """
            self.stdout.write(self.style.SUCCESS('Executing Step 2: Download'))
            dc_step = DataCycleStep.create_step(DataCycleStep.STEP2_DOWNLOAD, dc)
            self.stdout.write(self.style.SUCCESS('Data cycle step %s created for dc %s' % (dc_step.step_id, dc.id)))
            """ Load list of all MLSs objects that will be downloaded/extracted """
  
        if options['full'] or (DataCycleStep.STEP3_CONVERT in options['steps']):                  
            
            """ Step 3 : Convert """
            self.stdout.write(self.style.SUCCESS('Executing Step 3: Convert'))
            dc_step = DataCycleStep.create_step(DataCycleStep.STEP3_CONVERT, dc)
            self.stdout.write(self.style.SUCCESS('Data cycle step %s created for dc %s' % (dc_step.step_id, dc.id)))            

        if options['full'] or (DataCycleStep.STEP4_GENERATE in options['steps']):      

            """ Step 4 : Generate """
            self.stdout.write(self.style.SUCCESS('Executing Step 4: Generate'))
            dc_step = DataCycleStep.create_step(DataCycleStep.STEP4_GENERATE, dc)
            self.stdout.write(self.style.SUCCESS('Data cycle step %s created for dc %s' % (dc_step.step_id, dc.id)))            

        if options['full'] or (DataCycleStep.STEP5_CLEANUP in options['steps']):                  
            
            """ Step 5 : Cleanup """
            self.stdout.write(self.style.SUCCESS('Executing Step 5: Cleanup'))
            dc_step = DataCycleStep.create_step(DataCycleStep.STEP5_CLEANUP, dc)
            self.stdout.write(self.style.SUCCESS('Data cycle step %s created for dc %s' % (dc_step.step_id, dc.id)))
            
    
class Step1Prepare(object):

    def __init__(self):
        self.step = DataCycleStep.STEP1_PREPARE
    
    def step1(self):
        print(self.step)
    