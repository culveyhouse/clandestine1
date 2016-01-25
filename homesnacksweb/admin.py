from django.contrib import admin
from .models import MLS, PropertyCurrent, DataCycle, DataCycleStep

# Register your models here.
admin.site.register(MLS)
admin.site.register(PropertyCurrent)
admin.site.register(DataCycle)
admin.site.register(DataCycleStep)

