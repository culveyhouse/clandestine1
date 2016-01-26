from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class MLS(models.Model):
    """The MLS model defines each MLS that we have added to our data cycle to extract listings"""
    user = models.ForeignKey(User, null=True, blank=True)
    mls_id = models.CharField(max_length=128, null=True, blank=True, 
        help_text='Alphanumeric id or designation as issued by MLS')
    mls_name = models.CharField(max_length=500, help_text='Business name of the MLS')
    rets_url = models.URLField(null=True, blank=True)
    business_url = models.URLField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "MLSs"    

class City(models.Model):
    """City table is a growing list of cities that appeared at least once
    in any of the data feeds. It is incomplete, but rather it reflects the
    cities that we cover or have covered"""
    user = models.ForeignKey(User, null=True, blank=True)    
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    rets_city_id = models.PositiveIntegerField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Cities"    
        
class PropertyCurrent(models.Model):
    """PropertyCurrent is the model/table that holds all normalized property data 
    that was most recently used to generate the full set of static HTML listing pages"""
    STATUS_ACTIVE = 1
    STATUS_PENDING = 2
    STATUS_SOLD = 3
    STATUS_OFF_MARKET = 4
    PROPERTY_STATUS = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_SOLD, 'Sold'),
        (STATUS_OFF_MARKET, 'Off Market')
    )
    
    user = models.ForeignKey(User, null=True, blank=True)
    mls = models.ForeignKey(MLS)
    mls_property_id = models.CharField(max_length=50, 
        help_text='The property_id as defined by the MLS, usually an integer')
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    address_line_3 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    homesnacks_city_id = models.ForeignKey
    zip_code = models.CharField(max_length=5, 
        help_text='The required 5 digit zip code of the U.S. address for this property')
    zip_ext = models.CharField(max_length=4, null=True, blank=True, 
        help_text='The optional 4 digit ZIP+4 extension for this property')
    days_on_market = models.PositiveIntegerField(null=True, blank=True)
    agent_name = models.CharField(max_length=255, null=True, blank=True)
    agent_id = models.PositiveIntegerField(null=True, blank=True)
    agent_email = models.CharField(max_length=255, null=True, blank=True)
    agent_listing_office_name = models.CharField(max_length=255, null=True, blank=True)
    property_description = models.TextField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=16, default=0)
    bedrooms_total = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    bathrooms_total = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    bedrooms_full = models.DecimalField(decimal_places=2, max_digits=5, default=0, null=True, blank=True)
    bathrooms_full = models.DecimalField(decimal_places=2, max_digits=5, default=0, null=True, blank=True)
    bedrooms_half = models.DecimalField(decimal_places=2, max_digits=5, default=0, null=True, blank=True)
    bathrooms_half = models.DecimalField(decimal_places=2, max_digits=5, default=0, null=True, blank=True)
    rooms_total = models.DecimalField(decimal_places=2, max_digits=5, default=0, null=True, blank=True)        
    list_date = models.DateField(default=date(2015, 1, 1) , null=True, blank=True)        
    size = models.PositiveIntegerField(default=0)
    geo_lat = models.DecimalField(decimal_places=12, max_digits=24, null=True, blank=True)
    geo_long = models.DecimalField(decimal_places=12, max_digits=24, null=True, blank=True)
    photo_count = models.PositiveIntegerField(default=0)
    status = models.PositiveSmallIntegerField(choices=PROPERTY_STATUS, default=STATUS_ACTIVE,
        help_text='For sale / sold status of the property',
        validators=[MinValueValidator(1),
                    MaxValueValidator(4)])
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "PropertiesCurrent"
        
class DataCycle(models.Model):
    """The DataCycle model maintains rows of data cycle runs, 
    and records current status of all parts of the data cycle"""
    STATUS_NOT_STARTED = 1
    STATUS_RUNNING = 2
    STATUS_COMPLETE = 3
    STATUS_COMPLETE_W_ERROR = 4
    STATUS_ABEND = 5 
    JOB_STATUS = (
        (STATUS_NOT_STARTED, 'Not Started'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETE, 'Finished'),
        (STATUS_COMPLETE_W_ERROR, 'Finished with errors'),
        (STATUS_ABEND, 'Abended/Aborted')
    )
    user = models.ForeignKey(User, null=True, blank=True)    
    """step1 includes any preparations needed before the MLS feed step begins"""
    step1_prep_status = models.PositiveSmallIntegerField(choices=JOB_STATUS, default=STATUS_NOT_STARTED)
    """step2 is the main feed downloader which loops through each MLS data pipe"""
    step2_download_status = models.PositiveSmallIntegerField(choices=JOB_STATUS, default=STATUS_NOT_STARTED)
    step3_convert_status = models.PositiveSmallIntegerField(choices=JOB_STATUS, default=STATUS_NOT_STARTED)
    step4_pagegen_status = models.PositiveSmallIntegerField(choices=JOB_STATUS, default=STATUS_NOT_STARTED)
    step5_cleanup_status = models.PositiveSmallIntegerField(choices=JOB_STATUS, default=STATUS_NOT_STARTED)
    last_step_completed = models.PositiveSmallIntegerField(default=0)    
    data_cycle_start = models.DateTimeField(null=True, blank=True)
    data_cycle_finish = models.DateTimeField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
               
class DataCycleStep(models.Model):
    """The data cycle steps model is a many-to-one table detailing each step
    completed of each data cycle, in individual step-rows"""
    STEP1_PREPARE = 1
    STEP2_DOWNLOAD = 2
    STEP3_CONVERT = 3
    STEP4_GENERATE = 4
    STEP5_CLEANUP = 5
    CYCLE_STEPS = (
        (STEP1_PREPARE, 'Prepare data cycle with pre-download steps'),
        (STEP2_DOWNLOAD, 'Download/extract all real estate data & media'),
        (STEP3_CONVERT, 'Normalize all downloaded data into tables'),
        (STEP4_GENERATE, 'Generate all front-end pages and assets'),
        (STEP5_CLEANUP, 'Finish post-processing cleanup tasks')
    )
    
    STATUS_NOT_STARTED = 1
    STATUS_RUNNING = 2
    STATUS_COMPLETE = 3
    STATUS_COMPLETE_W_ERROR = 4
    STATUS_ABEND = 5 
    JOB_STATUS = (
        (STATUS_NOT_STARTED, 'Not Started'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETE, 'Finished'),
        (STATUS_COMPLETE_W_ERROR, 'Finished with errors'),
        (STATUS_ABEND, 'Abended/Aborted')
    )    
    user = models.ForeignKey(User, null=True, blank=True)    
    data_cycle = models.ForeignKey(DataCycle)
    step_id = models.PositiveSmallIntegerField(choices=CYCLE_STEPS, 
        validators=[MinValueValidator(1),
                    MaxValueValidator(5)])
    step_status = models.PositiveSmallIntegerField(choices=JOB_STATUS, default=STATUS_NOT_STARTED)
    step_start = models.DateTimeField(null=True, blank=True)
    step_finish = models.DateTimeField(null=True, blank=True)    
    notes = models.TextField(null=True, blank=True, help_text='Optional data cycle notes about this step.')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)    
