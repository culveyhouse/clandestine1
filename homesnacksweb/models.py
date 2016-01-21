from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

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
    list_date = models.DateTimeField(default='2015-01-01', null=True, blank=True)        
    size = models.PositiveIntegerField(default=0)
    geo_lat = models.DecimalField(decimal_places=12, max_digits=24, null=True, blank=True)
    geo_long = models.DecimalField(decimal_places=12, max_digits=24, null=True, blank=True)
    photo_count = models.PositiveIntegerField(default=0)
    status = models.PositiveSmallIntegerField(choices=PROPERTY_STATUS, default=STATUS_ACTIVE,
        help_text='Choose whether this is a main section, a subsection, or a third-level section',
        validators=[MinValueValidator(1),
                    MaxValueValidator(3)])
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "PropertiesCurrent"
        
        
        
        