from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.template import Template, Context
from django.core.files import File
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep, JobStatus
from datetime import datetime
from itertools import chain
from decimal import Decimal  
import re, sys, math

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
                
                for field in [
                    'address_line_1','city','state','zip_code','price','bedrooms_total','bathrooms_total','seo_url',
                    'status','days_on_market','photo_count','size','house_style','property_description','rooms_total',
                    'year_built','water_source','sewer','property_type','family_room_level','bathrooms_full',
                    'bathrooms_half','bedroom_dimensions_all','living_room_dimensions','living_room_flooring',
                    'living_room_level','attic_info','basement_info', 'heating_info', 'cooling_info', 'garage_info', 
                    'fireplace_info', 'exterior_features', 'roof_info', 'foundation_info', 'lot_dimensions', 'lot_description',
                    'school_elementary', 'school_middle', 'school_high', 'agent_name', 'agent_phone', 'agent_phone_2'
                ]:
                    exec('p.' + field + '=property.' + field)

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
                        "Photo_Count, Total_SF_Apx, Style, Public_Remarks, Rooms, Year_Built, Water, Sewer, Property_Type, " \
                        "Family_Rm_Level, Full_Baths, Partial_Baths, Bedroom1_Dim, Bedroom2_Dim, Bedroom3_Dim, Bedroom4_Dim, " \
                        "Living_Rm_Dim, Living_Rm_Flooring, Living_Rm_Level, Attic, Basement, Heat, Cooling, Garage, Fireplace, " \
                        "Exterior_Features, Roof, Foundation, Lot_Size_Apx, Lot_Description, Elementary_School, Middle_School, High_School, "\
                        "LA_First_Name, LA_Last_Name, LA_Phone1, LA_Phone2 " \
                        "FROM homesnacksweb_propertyimport WHERE length(City)>0 and length(State)>0 "        
        cursor.execute(imported_sql)
        properties = cursor.fetchall()
        """List that will store a collection of properties from the _propertyimport table. (Currently every row)"""
        propertySEOs = []  

        for property in properties:

            property_vars = ['mls_id', 'mls_property_id', 'street_number', 'direction', 'street_name', 'city', 'state', 'zip_code', 'list_price', 'bedrooms', 'bathrooms', 
            'days_on_market', 'photo_count', 'size', 'house_style', 'property_description', 'total_rooms', 'year_built', 'water_source', 'sewer', 
            'property_type', 'family_room_level', 'bathrooms_full', 'bathrooms_half', 'bedroom_dim_1', 'bedroom_dim_2', 'bedroom_dim_3', 'bedroom_dim_4', 'living_room_dimensions', 
            'living_room_flooring', 'living_room_level', 'attic_info', 'basement_info', 'heating_info', 'cooling_info', 'garage_info', 'fireplace_info', 'exterior_features', 
            'roof_info', 'foundation_info', 'lot_dimensions', 'lot_description', 'school_elementary', 'school_middle', 'school_high', 'la_first_name', 'la_last_name',
            'la_phone1', 'la_phone2'
            ]
            
            for key in enumerate(property_vars):
                key_no, var_name = key
                exec('%s = property[%d]' % (var_name, key_no)) 
            
            full_address = "%s%s %s" % (street_number.title(), (' ' + direction.upper() if (direction is not None and len(direction)>0) else ''), street_name.title()) 
            city_state_zip = "%s, %s %s" % (city.title(), state.upper(), zip_code)
            seo_url = re.sub(r'[^A-za-z0-9- ]', r'', full_address.lower() + '-' + city_state_zip.lower() + '-' + str(mls_id) + mls_property_id)
            seo_url = re.sub(r' ', r'-', seo_url)
            seo_url = re.sub(r'-+', r'-', seo_url)
            family_room_level = str(family_room_level.strip())
            bedroom_dimension_list = [bedroom_dim_1.strip().replace(' ', '') , bedroom_dim_2.strip().replace(' ', '') , bedroom_dim_3.strip().replace(' ', '') , bedroom_dim_4.strip().replace(' ', '')]
            bedroom_dimensions = ', '.join(filter(None, bedroom_dimension_list)).lower()
            living_room_dimensions = living_room_dimensions.strip().replace(' ','').lower()
            attic_info = re.sub(r',([^ ])', r', \1', attic_info).strip()
            basement_info = re.sub(r',([^ ])', r', \1', basement_info).strip()
            heating_info = re.sub(r',([^ ])', r', \1', heating_info).strip()
            cooling_info = re.sub(r',([^ ])', r', \1', cooling_info).strip()
            garage_info = re.sub(r',([^ ])', r', \1', garage_info).strip()
            fireplace_info = re.sub(r',([^ ])', r', \1', fireplace_info).strip()
            roof_info = re.sub(r',([^ ])', r', \1', roof_info).strip()
            foundation_info = re.sub(r',([^ ])', r', \1', foundation_info).strip()
            lot_dimensions = lot_dimensions.strip().replace(' ','').lower()
            lot_description = re.sub(r',([^ ])', r', \1', lot_description).strip()
            water_source = re.sub(r',([^ ])', r', \1', water_source).strip()
            sewer = re.sub(r',([^ ])', r', \1', sewer).strip()
            agent_name = ' '.join([la_first_name.strip(), la_last_name.strip()])
            
            try:
                list_price_float = float(list_price)
            except ValueError, e:
                list_price_float = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id price %s/%s %s sharted.' % (mls_id, mls_property_id, list_price)))   

            try:
                bedrooms_float = float(bedrooms)
            except ValueError, e:
                bedrooms_float = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id bedrooms %s/%s %s sharted.' % (mls_id, mls_property_id, bedrooms)))   
                
            try:
                bathrooms_float = float(bathrooms)
            except ValueError, e:
                bathrooms_float = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id bathrooms %s/%s %s sharted.' % (mls_id, mls_property_id, bathrooms)))   
                
            try:
                days_on_market_int = int(days_on_market.strip())
            except ValueError, e:
                days_on_market_int = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id days_on_market_int %s/%s %s sharted.' % (mls_id, mls_property_id, days_on_market)))   
                
            try:
                photo_count_int = int(photo_count.strip())
            except ValueError, e:
                photo_count_int = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id photo_count %s/%s %s sharted.' % (mls_id, mls_property_id, photo_count)))   
                                
            try:
                size_int = int(size.strip())
            except ValueError, e:
                size_int = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id size %s/%s %s sharted.' % (mls_id, mls_property_id, size)))   
                                
            try:
                total_rooms_float = float(total_rooms)
            except ValueError, e:
                total_rooms_float = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id total_rooms %s/%s %s sharted.' % (mls_id, mls_property_id, total_rooms)))   
                                                
            try:
                year_built_int = int(year_built.strip())
            except ValueError, e:
                year_built_int = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id year_built %s/%s %s sharted.' % (mls_id, mls_property_id, year_built)))   
                                
            try:
                bathrooms_full_float = float(bathrooms_full)
            except ValueError, e:
                bathrooms_full_float = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id bathrooms_full %s/%s %s sharted.' % (mls_id, mls_property_id, bathrooms_full)))   
                                
            try:
                bathrooms_half_float = float(bathrooms_half)
            except ValueError, e:
                bathrooms_half_float = 0
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id bathrooms_half %s/%s %s sharted.' % (mls_id, mls_property_id, bathrooms_half)))   
            
            try:
                agent_phone = format(int(la_phone1[:-1]), ",").replace(",", "-") + la_phone1[-1] if la_phone1 else None
            except ValueError, e:
                agent_phone = None
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id listing agent phone %s/%s %s sharted.' % (mls_id, mls_property_id, agent_phone))) 
                   
            try:
                agent_phone_2 = format(int(la_phone2[:-1]), ",").replace(",", "-") + la_phone2[-1] if la_phone2 else None
            except ValueError, e:
                agent_phone_2 = None
                self.cmd.stdout.write(self.cmd.style.SUCCESS('mls/id listing agent phone 2 %s/%s %s sharted.' % (mls_id, mls_property_id, agent_phone_2))) 
                                     
            #self.cmd.stdout.write(self.cmd.style.SUCCESS('Formatting passed: %s-%s | addr: %s, %s / seo: %s / bathf: %s, bathh:%s ' % (str(mls_id), mls_property_id, full_address, city_state_zip, seo_url, bathrooms_full_float, bathrooms_half_float)))       
            
            propertySEOs.append(PropertyCurrent(
                mls_id=int(mls_id), mls_property_id=mls_property_id, address_line_1=full_address, 
                city=city.title(), state=state.upper(), zip_code=zip_code, price=list_price_float, 
                bedrooms_total=bedrooms_float, bathrooms_total=bathrooms_float, seo_url=seo_url,
                status=PropertyCurrent.STATUS_ACTIVE, days_on_market=days_on_market_int, photo_count=photo_count_int, 
                size=size_int, house_style=house_style, property_description=property_description, rooms_total=total_rooms_float, 
                year_built=year_built_int, water_source=water_source, sewer=sewer, property_type=property_type, family_room_level=family_room_level,
                bathrooms_full=bathrooms_full_float, bathrooms_half=bathrooms_half_float, bedroom_dimensions_all=bedroom_dimensions,
                living_room_dimensions=living_room_dimensions, living_room_flooring=living_room_flooring, living_room_level=living_room_level,
                attic_info=attic_info, basement_info=basement_info, heating_info=heating_info, cooling_info=cooling_info, garage_info=garage_info,
                fireplace_info=fireplace_info, exterior_features=exterior_features, roof_info=roof_info, foundation_info=foundation_info, 
                lot_dimensions=lot_dimensions, lot_description=lot_description, school_elementary=school_elementary, school_middle=school_middle,
                school_high=school_high, agent_name=agent_name, agent_phone=agent_phone, agent_phone_2=agent_phone_2 
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
        
        homepage_html = self.generateHomePage()
        city_pages_html = self.generateCityPages()
        pdp_pages_html = self.generatePDP()
        return dc_step

    def generateHomePage(self):
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Beginning the home page HTML page generation'))
        with open('/home/ubuntu/workspace/clandestine1/templates/HTML_generator_templates/real-estate-template.html', 'r') as f:
            home_page_HTML = File(f).read()
        t = Template(unicode(home_page_HTML))
        
        city_list = City.objects.filter(active=1).order_by('-property_count_current', 'name')[:30]
        city_list_top = []
        for city in city_list:
            # SEO regex that was repeated from above, make sure to refactor this DLC ZZZ
            seo_url = re.sub(r'[^A-za-z0-9- ]', r'', city.name.lower() + '-' + city.state.lower())
            seo_url = re.sub(r' ', r'-', seo_url)
            seo_url = re.sub(r'-+', r'-', seo_url)
            """ Produce a human-readable city, state string. E.g., Danville, IL """
            city_state = ', '.join([city.name, city.state]) 
            city_list_top.append(
                {"city_state": city_state,
                 "city_state_seo":seo_url,
                 "property_count":city.property_count_current}
            )
        
        city_list = City.objects.filter(active=1).order_by('name')
        city_list_bottom = []
        for city in city_list:
            # SEO regex that was repeated from above, make sure to refactor this DLC ZZZ
            seo_url = re.sub(r'[^A-za-z0-9- ]', r'', city.name.lower() + '-' + city.state.lower())
            seo_url = re.sub(r' ', r'-', seo_url)
            seo_url = re.sub(r'-+', r'-', seo_url)
            """ Produce a human-readable city, state string. E.g., Danville, IL """
            city_state = ', '.join([city.name, city.state]) 
            city_list_bottom.append(
                {"city_state": city_state,
                 "city_state_seo":seo_url,
                 "property_count":city.property_count_current}
            )
        
        property_slide_total = range(1, 15)

        carousel_properties = PropertyCurrent.objects.filter(price__gt = 100000).filter(photo_count__gt = 0).order_by('days_on_market')[:15]
        for property in carousel_properties:
            property.formatted_display_list_price = '{:,.0f}'.format(property.price)  
            property.property_primary_photo_url = '%d/Photo%s-1.jpeg' % (property.mls_id, property.mls_property_id)
            property.property_city_state = ', '.join([property.city, property.state])
        c = Context({   "city_list_top":city_list_top, 
                        "city_list_bottom":city_list_bottom,
                        "property_slide_total":property_slide_total,
                        "carousel_properties":carousel_properties
                    })
                     
        with open('/home/ubuntu/workspace/clandestine1/templates/HTML_generator_templates/generated_HTML/real-estate.html', 'w+') as final_html:   
            final_html.write(t.render(c))
            final_html.close()

    def generateCityPages(self):   
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Beginning the city HTML page generation'))
        cities = City.objects.all().filter(active=1)
        for city in cities: 
            city.property_count_current = 0 if (city.property_count_current is None) else city.property_count_current 
            total_pages = int(math.ceil(float(city.property_count_current) / float(15)))
            if total_pages > 1:
                self.cmd.stdout.write(self.cmd.style.SUCCESS(
                    '%s has %s props on %s pages' % (city.name, str(city.property_count_current), str(total_pages))))                
            for current_page in range(1, int(total_pages)+1):
                    
                next_page_no = current_page+1 if total_pages>1 else 0
                prev_page_no = current_page-1 if total_pages>1 else 0            
                show_pages = range(current_page-4, current_page+5)

                with open('/home/ubuntu/workspace/clandestine1/templates/HTML_generator_templates/city-template.html', 'r') as f:
                    city_HTML = File(f).read()
                t = Template(unicode(city_HTML))  
                
                seo_url = re.sub(r'[^A-za-z0-9- ]', r'', city.name.lower() + '-' + city.state.lower())
                seo_url = re.sub(r' ', r'-', seo_url)
                seo_url = re.sub(r'-+', r'-', seo_url)            
                
    
                city_properties = PropertyCurrent.objects.filter(city=city.name, state=city.state).order_by('days_on_market')[(current_page-1)*15:(current_page*15)]
                
                for property in city_properties:
                    property.formatted_display_list_price = '{:,.0f}'.format(property.price)  
                    property.property_primary_photo_url = '%d/Photo%s-1.jpeg' % (property.mls_id, property.mls_property_id)
                    property.property_city_state = ', '.join([property.city, property.state])
                    property.formatted_total_beds = '{0:g}'.format(float(property.bedrooms_total))
                    property.formatted_total_baths = '{0:g}'.format(float(property.bathrooms_total))
                    property.formatted_sqft = '{:,}'.format(int(property.size))

                c = Context({   "city":city, 
                                "seo_url":seo_url,
                                "total_pages":total_pages,
                                "current_page":current_page,
                                "prev_page_no":prev_page_no,
                                "next_page_no":next_page_no,
                                "total_pages_loop":range(1,int(total_pages)+1),
                                "city_properties":city_properties,
                                "show_pages":show_pages
                            })
                cur_page_url = ('-%d' % current_page) if current_page>1 else ''
                with open('/home/ubuntu/workspace/clandestine1/templates/HTML_generator_templates/generated_HTML/locations/' + seo_url + cur_page_url + '.html', 'w+') as final_html:   
                    final_html.write(t.render(c))
                    final_html.close()        
    
    def generatePDP(self): 
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Beginning the PDP HTML page generation'))
        property_batch_size = 100
        
        with open('/home/ubuntu/workspace/clandestine1/templates/HTML_generator_templates/pdp-template.html', 'r') as f:
            city_HTML = File(f).read()
            t = Template(unicode(city_HTML))        
        
        property_total = PropertyCurrent.objects.exclude(status=PropertyCurrent.STATUS_HIDDEN).count()
        
        batches = range(int(math.ceil(property_total / property_batch_size))+1)
        
        for batch in batches:
            self.cmd.stdout.write(self.cmd.style.SUCCESS(
                'Writing property batch %s of %s, %s of %s' % (str(batch+1), len(batches), (batch * property_batch_size), 
                    min(max((batch * property_batch_size),(batch+1) * property_batch_size), 
                    max(property_total,(batch+1) * property_batch_size),
                    max((batch * property_batch_size),property_total)))))
            properties = PropertyCurrent.objects.exclude(status=PropertyCurrent.STATUS_HIDDEN).order_by('days_on_market')[(batch * property_batch_size):((batch+1) * (property_batch_size))]
            for property in properties: 
                
                city_seo_url = re.sub(r'[^A-za-z0-9- ]', r'', property.city.lower() + '-' + property.state.lower())
                city_seo_url = re.sub(r' ', r'-', city_seo_url)
                city_seo_url = re.sub(r'-+', r'-', city_seo_url) 
                photo_loop = range(1, property.photo_count+1)
                property.formatted_display_list_price = '{:,.0f}'.format(property.price)  
                property.property_primary_photo_url = '%d/Photo%s-1.jpeg' % (property.mls_id, property.mls_property_id)
                property.property_city_state = ', '.join([property.city, property.state])
                property.formatted_total_beds = '{0:g}'.format(float(property.bedrooms_total))
                property.formatted_total_baths = '{0:g}'.format(float(property.bathrooms_total))
                property.formatted_sqft = '{:,}'.format(int(property.size))
                property.formatted_rooms_total = '{0:g}'.format(float(property.rooms_total))              
                property.formatted_full_baths = '{0:g}'.format(float(property.bathrooms_full))
                property.formatted_half_baths = '{0:g}'.format(float(property.bathrooms_half))
                property.exterior_features = [feature.strip() for feature in property.exterior_features.split(',')]
                property.exterior_features = [feature for feature in property.exterior_features if feature!='']

                
                
                """ Assemble a crackerjack list of nearby homes using several techniques """

                nearby_properties_in_zipcode = []
                nearby_properties_in_city = []
                nearby_properties_in_state = []
                
                nearby_properties_in_zipcode = PropertyCurrent.objects.filter(
                    zip_code=property.zip_code, bedrooms_total=property.bedrooms_total, bathrooms_total__range=(property.bathrooms_total-Decimal(0.5),property.bathrooms_total+Decimal(0.5))
                    ).exclude(status=PropertyCurrent.STATUS_HIDDEN).exclude(mls_property_id=property.mls_property_id).order_by('days_on_market')[:4]
                if len(nearby_properties_in_zipcode) < 4:
                    nearby_properties_in_city = PropertyCurrent.objects.filter(
                        city=property.city, bedrooms_total=property.bedrooms_total, bathrooms_total__range=(property.bathrooms_total-Decimal(0.5),property.bathrooms_total+Decimal(0.5))
                        ).exclude(status=PropertyCurrent.STATUS_HIDDEN).exclude(mls_property_id=property.mls_property_id).order_by('days_on_market')[:4]
                if len(nearby_properties_in_city) + len(nearby_properties_in_zipcode) < 4:
                    nearby_properties_in_state = PropertyCurrent.objects.filter(
                        state=property.state, bedrooms_total=property.bedrooms_total, bathrooms_total__range=(property.bathrooms_total-Decimal(0.5),property.bathrooms_total+Decimal(0.5))
                        ).exclude(status=PropertyCurrent.STATUS_HIDDEN).exclude(mls_property_id=property.mls_property_id).order_by('days_on_market')[:4]

                nearby_properties = sorted(
                    chain(nearby_properties_in_zipcode, nearby_properties_in_city, nearby_properties_in_state),
                    key=lambda prop: prop.days_on_market, reverse=False)
                deduped_properties = []
                for p in nearby_properties:
                    if p not in deduped_properties and len(deduped_properties)<4:
                        p.formatted_display_list_price = '{:,.0f}'.format(p.price)  
                        p.property_primary_photo_url = '%d/Photo%s-1.jpeg' % (p.mls_id, p.mls_property_id)
                        p.property_city_state = ', '.join([p.city, p.state])
                        p.formatted_total_beds = '{0:g}'.format(float(p.bedrooms_total))
                        p.formatted_total_baths = '{0:g}'.format(float(p.bathrooms_total))
                        p.formatted_sqft = '{:,}'.format(int(p.size))
                        deduped_properties.append(p)
                        
                nearby_properties = deduped_properties

                c = Context({   
                                "property":property,
                                "city_seo_url":city_seo_url,
                                "photo_loop":photo_loop,
                                "nearby_properties":nearby_properties
                            })
                
                with open('/home/ubuntu/workspace/clandestine1/templates/HTML_generator_templates/generated_HTML/properties/' + property.seo_url + '.html', 'w+') as final_html:   
                    final_html.write(t.render(c))
                    final_html.close()                  

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


        
        
                