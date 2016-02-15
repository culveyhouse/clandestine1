from django.core.management.base import BaseCommand, CommandError
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep, JobStatus
from datetime import datetime

class Command(BaseCommand):
    help = 'This command manages the entire HomeSnacks real estate data cycle'
    dc = None
    
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

        """ Step 1 : Prepare """
        
        if options['full'] or (DataCycleStep.STEP1_PREPARE in options['steps']):            
            """ Run first step if full data cycle requested or Step 1 explicitly """
            self.stdout.write(self.style.SUCCESS('Starting the HomeSnacks data cycle'))   

            self.stdout.write(self.style.SUCCESS('Executing Step 1: Prepare'))
            step1 = Step1Prepare(self)
            self.dc = step1.execute()

        elif options['steps']:
            """ Otherwise at least grab the last data cycle created to continue with that """
            self.stdout.write(self.style.SUCCESS('Grabbing the most recent data cycle'))   
            self.dc = DataCycle.objects.latest('id')
            self.stdout.write(self.style.SUCCESS('Skipping Step 1, operating on existing data cycle %s instead' % self.dc.id))
        """ DLCZZZ: Finish up any other preparations, then move on to step 2 """
        
        
        """ Step 2 : Download """
        
        if options['full'] or (DataCycleStep.STEP2_DOWNLOAD in options['steps']):      
            
            self.stdout.write(self.style.SUCCESS('Executing Step 2: Download'))
            step2 = Step2Download(self)
            dc_step, mls_list = step2.execute()
            for mls in mls_list:
                self.stdout.write('mls id is %s' % (mls.id))
            
        """ Step 3 : Convert """
        
        if options['full'] or (DataCycleStep.STEP3_CONVERT in options['steps']):                  
            
            self.stdout.write(self.style.SUCCESS('Executing Step 3: Convert'))
            step3 = Step3Convert(self)
            dc_step = step3.execute()          

        
        """ Step 4 : Generate """
        
        if options['full'] or (DataCycleStep.STEP4_GENERATE in options['steps']):      
            
            self.stdout.write(self.style.SUCCESS('Executing Step 4: Generate HTML'))
            step4 = Step4Generate(self)
            dc_step = step4.execute()          

        
        """ Step 5 : Cleanup """
        
        if options['full'] or (DataCycleStep.STEP5_CLEANUP in options['steps']):                  
            
            self.stdout.write(self.style.SUCCESS('Executing Step 5: Clean Up'))
            step5 = Step5Cleanup(self)
            dc_step = step5.execute()       
    
    
class Step1Prepare(object):

    def __init__(self, dc_cmd):
        """ Just assign an integer to this step, probably 1 """
        self.step = DataCycleStep.STEP1_PREPARE 
        """ Use the passed Command(BaseCommand) object """ 
        self.dc_cmd = dc_cmd
        """ Use the generic Command class to access methods like stdout """
        self.cmd = Command() 
    
    def execute(self):
        """ Add new data cycle to _datacycle table """
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Adding new data cycle...'))
        self.dc = DataCycle.create()
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Data cycle %s created' % self.dc.id))
        
        """ Add a data cycle step to _datacyclestep table via a classmethod 
        and reference data_cycle_id foreign key in dc object """
        dc_step = DataCycleStep.create_step(self.step, self.dc)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Data cycle step %s created for data cycle %s (step_id=%s)' 
            % (dc_step.step_id, self.dc.id, dc_step.id)))
        
        """ In this first step class, the entire data cycle object is returned,
        while in steps 2 - 5, just the current data cycle step object is returned """
        return self.dc


class Step2Download(object):

    def __init__(self, dc_cmd):
        """ Just assign an integer to this step, probably 1 """
        self.step = DataCycleStep.STEP2_DOWNLOAD 
        """ Use the passed Command(BaseCommand) object """ 
        self.dc_cmd = dc_cmd
        """ Use the generic Command class to access methods like stdout """
        self.cmd = Command() 
    
    def execute(self):
        """ Add a data cycle step to _datacyclestep table via a classmethod 
        and reference data_cycle_id foreign key in dc object """
        dc_step = DataCycleStep.create_step(self.step, self.dc_cmd.dc)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Data cycle step %s created for data cycle %s (step_id=%s)' 
            % (dc_step.step_id, self.dc_cmd.dc.id, dc_step.id)))
        
        """ Load list of all MLSs objects that will be downloaded/extracted """
        mls_list = MLS.objects.all()            
        for mls in mls_list: 
            self.cmd.stdout.write('Mls %s' % mls.id)
            
        return (dc_step, mls_list)


class Step3Convert(object):

    def __init__(self, dc_cmd):
        """ Just assign an integer to this step, probably 1 """
        self.step = DataCycleStep.STEP3_CONVERT 
        """ Use the passed Command(BaseCommand) object """ 
        self.dc_cmd = dc_cmd
        """ Use the generic Command class to access methods like stdout """
        self.cmd = Command() 
    
    def execute(self):
        """ Add a data cycle step to _datacyclestep table via a classmethod 
        and reference data_cycle_id foreign key in dc object """
        dc_step = DataCycleStep.create_step(self.step, self.dc_cmd.dc)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Data cycle step %s created for data cycle %s (step_id=%s)' 
            % (dc_step.step_id, self.dc_cmd.dc.id, dc_step.id)))
        
        """ Load list of all MLSs objects that will be downloaded/extracted """
            
        return dc_step


class Step4Generate(object):

    def __init__(self, dc_cmd):
        """ Just assign an integer to this step, probably 1 """
        self.step = DataCycleStep.STEP4_GENERATE 
        """ Use the passed Command(BaseCommand) object """ 
        self.dc_cmd = dc_cmd
        """ Use the generic Command class to access methods like stdout """
        self.cmd = Command() 
    
    def execute(self):
        """ Add a data cycle step to _datacyclestep table via a classmethod 
        and reference data_cycle_id foreign key in dc object """
        dc_step = DataCycleStep.create_step(self.step, self.dc_cmd.dc)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Data cycle step %s created for data cycle %s (step_id=%s)' 
            % (dc_step.step_id, self.dc_cmd.dc.id, dc_step.id)))
        
        """ Load list of all MLSs objects that will be downloaded/extracted """
            
        return dc_step


class Step5Cleanup(object):

    def __init__(self, dc_cmd):
        """ Just assign an integer to this step, probably 1 """
        self.step = DataCycleStep.STEP5_CLEANUP 
        """ Use the passed Command(BaseCommand) object """ 
        self.dc_cmd = dc_cmd
        """ Use the generic Command class to access methods like stdout """
        self.cmd = Command() 
    
    def execute(self):
        """ Add a data cycle step to _datacyclestep table via a classmethod 
        and reference data_cycle_id foreign key in dc object """
        dc_step = DataCycleStep.create_step(self.step, self.dc_cmd.dc)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Data cycle step %s created for data cycle %s (step_id=%s)' 
            % (dc_step.step_id, self.dc_cmd.dc.id, dc_step.id)))
        
        """ Load list of all MLSs objects that will be downloaded/extracted """
            
        return dc_step


        
        
                