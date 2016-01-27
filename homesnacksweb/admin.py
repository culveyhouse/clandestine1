from django.contrib import admin
from .models import MLS, City, PropertyCurrent, DataCycle, DataCycleStep

# Register your models here.
admin.site.register(MLS)
admin.site.register(City)
admin.site.register(PropertyCurrent)
admin.site.register(DataCycle)
admin.site.register(DataCycleStep)

