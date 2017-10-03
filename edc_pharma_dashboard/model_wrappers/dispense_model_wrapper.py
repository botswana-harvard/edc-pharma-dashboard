from edc_model_wrapper import ModelWrapper
from edc_pharma.models import DispenseTimepoint
from edc_pharma.timepoint_descriptor import TimepointDescriptor

from django.apps import apps as django_apps


app_config = django_apps.get_app_config('edc_pharma_dashboard')
edc_pharma_app_config = django_apps.get_app_config('edc_pharma')


class DispenseModelWrapper(ModelWrapper):

    model = edc_pharma_app_config.dispense_model
    next_url_name = app_config.dispense_listboard_url_name
    querystring_attrs = ['subject_identifier', 'sid']

    @property
    def dispense_timepoint(self):
        if self.dispense_schedule:
            try:
                return DispenseTimepoint.objects.filter(
                    schedule__subject_identifier=self.subject_identifier,
                    is_dispensed=False
                ).order_by('created').first()
            except DispenseTimepoint.DoesNotExist:
                pass

    @property
    def dispense_timepoint_id(self):
        return str(self.dispense_timepoint.id)

    @property
    def dispense_timepoint_descriptor(self):
        descriptor = TimepointDescriptor(
            dispense_timepoint=self.dispense_timepoint)
        return descriptor
