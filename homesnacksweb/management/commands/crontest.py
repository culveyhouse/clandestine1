from django.core.management.base import BaseCommand, CommandError
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep, JobStatus


class Command(BaseCommand):
    help = 'Just a first test for db and Django core connectivity'

    def add_arguments(self, parser):
        parser.add_argument('mls_input_id', nargs='*', type=int)
            # Named (optional) arguments
        parser.add_argument('--job_status_const_test',
            action='store_true',
            dest='job_status_const_test',
            default=False,
            help='Execute the model class constants in different places')

    def handle(self, *args, **options):
        if options['job_status_const_test']:
            self.stdout.write(self.style.SUCCESS('Starting the class constant test'))
            
            self.stdout.write(self.style.SUCCESS('Now printing the global constants...'))  
            jsObj = JobStatus()
            for i,j in jsObj.JOB_STATUS[0:2]:
                self.stdout.write(self.style.SUCCESS('%s: %s' % (i,j)))  
                
            self.stdout.write(self.style.SUCCESS('Printing the class constants first...'))            
            dcsObject = DataCycleStep()
            for i,j in dcsObject.JobStatusCodes.JOB_STATUS[0:2]:
                self.stdout.write(self.style.SUCCESS('%s: %s' % (i,j)))
           
        if options['mls_input_id']: 
            for mls_input_id in options['mls_input_id']:
                try:
                    MLSobj = MLS.objects.get(pk=mls_input_id)
                except MLS.DoesNotExist:
                    raise CommandError('MLS "%s" does not exist' % mls_input_id)
    
                name = MLSobj.mls_name 
                self.stdout.write(self.style.SUCCESS('Oh, MLS %s is %s' % (mls_input_id, name)))

