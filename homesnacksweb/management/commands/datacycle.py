from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep, JobStatus
from datetime import datetime
import re, sys

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
        """ Just assign an integer to this step, probably 2 """
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
        """ Just assign an integer to this step, probably 3 """
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
        
        self.cmd.stdout.write(self.cmd.style.SUCCESS('.1: Grabbing property object collection from _propertyimport'))        
        properties = self.generateSEOProperties()
        for property in properties:
            try: 
                #self.cmd.stdout.write(self.cmd.style.SUCCESS("Getting %s-%s" % (property.mls_id, property.mls_property_id) ))
                p = PropertyCurrent.objects.get(
                    mls_id=property.mls_id, 
                    mls_property_id=property.mls_property_id
                )
                #self.cmd.stdout.write(self.cmd.style.SUCCESS("Found %s-%s, id is %s" % (p.mls_id, p.mls_property_id, p.id) ))
                p.address_line_1=property.address_line_1
                p.city=property.city
                p.state=property.state
                p.zip_code=property.zip_code
                p.price=property.price
                p.bedrooms_total=property.bedrooms_total
                p.bathrooms_total=property.bathrooms_total
                p.seo_url=property.seo_url   
                p.status = PropertyCurrent.STATUS_ACTIVE
                p.days_on_market = property.days_on_market
                p.photo_count = property.photo_count
                p.save()
                self.cmd.stdout.write(self.cmd.style.SUCCESS("Found & updated %s-%s" % (p.mls_id, p.mls_property_id) ))
            except: 
                property.save()
                self.cmd.stdout.write(self.cmd.style.SUCCESS("Created %s-%s" % (property.mls_id, property.mls_property_id) ))

            
        return dc_step
        
    def generateSEOProperties(self):
        """ Build full property list with supporting info (including SEO URLs) and either update or add to _propertycurrent. 
        Assumes that data is in a _propertyimport table (not in the models.py) """
        
        cursor = connection.cursor()
        imported_sql =  "SELECT mls_id, MLS_Number, Street_Number, Direction, Street_Name, " \
                        "City, State, Zip_Code, List_Price, Bedrooms, Ttl_Baths, Days_On_Market, " \
                        "Photo_Count " \
                        "FROM homesnacksweb_propertyimport WHERE length(City)>0 and length(State)>0 "        
        cursor.execute(imported_sql)
        properties = cursor.fetchall()
        """List that will store a collection of properties from the _propertyimport table. (Currently every row)"""
        propertySEOs = []  

        for property in properties:
            mls_id =            property[0]
            mls_property_id =   property[1]
            street_number =     property[2]
            direction =         property[3]
            street_name =       property[4]
            city =              property[5]
            state =             property[6]
            zip_code =          property[7]
            list_price =        property[8]
            bedrooms =          property[9]
            bathrooms =         property[10]
            days_on_market =    property[11]
            photo_count =       property[12]
            full_address = "%s%s %s" % (street_number.title(), (' ' + direction.upper() if (direction is not None and len(direction)>0) else ''), street_name.title()) 
            city_state_zip = "%s, %s %s" % (city.title(), state.upper(), zip_code)
            seo_url = re.sub(r'[^A-za-z0-9- ]', r'', full_address.lower() + '-' + city_state_zip.lower() + '-' + str(mls_id) + mls_property_id)
            seo_url = re.sub(r' ', r'-', seo_url)
            seo_url = re.sub(r'-+', r'-', seo_url)
            try:
                list_price_float = float(list_price)
                bedrooms_float = float(bedrooms)
                bathrooms_float = float(bathrooms)
                days_on_market_int = int(days_on_market.strip())
                photo_count_int = int(photo_count.strip())
                self.cmd.stdout.write(self.cmd.style.SUCCESS('price/beds/baths/dom/photoct "%s/%s/%s/%s/%s" cleared.' % (list_price, bedrooms, bathrooms, days_on_market_int, photo_count_int)))                  
            except ValueError, e:
                list_price_float = bedrooms_float = bathrooms_float = float(0)
                days_on_market_int = photo_count_int = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('price/beds/baths/dom/photoct "%s/%s/%s/%s/%s" sharted.' % (list_price, bedrooms, bathrooms, days_on_market_int, photo_count_int)))      

            #self.cmd.stdout.write(self.cmd.style.SUCCESS('%s-%s | addr: %s, %s  /  seo: %s' % (str(mls_id), mls_property_id, full_address, city_state_zip, seo_url)))       
            
            propertySEOs.append(PropertyCurrent(
                mls_id=int(mls_id), mls_property_id=mls_property_id, address_line_1=full_address, 
                city=city.title(), state=state.upper(), zip_code=zip_code, price=list_price_float, 
                bedrooms_total=bedrooms_float, bathrooms_total=bathrooms_float, seo_url=seo_url,
                status=PropertyCurrent.STATUS_ACTIVE, days_on_market=days_on_market_int, photo_count=photo_count_int
            ))
        
        cursor.close()
        return propertySEOs
        
    def storeSEOURLs(self):
        pass
        

class Step4Generate(object):

    def __init__(self, dc_cmd):
        """ Just assign an integer to this step, probably 4 """
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
        """ Just assign an integer to this step, probably 5 """
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


        
        
                