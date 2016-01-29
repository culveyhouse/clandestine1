from django.core.management.base import BaseCommand, CommandError
from homesnacksweb.models import MLS, PropertyCurrent, City, DataCycle, DataCycleStep, JobStatus


class Command(BaseCommand):
    help = 'This command manages the entire HomeSnacks real estate data cycle'
