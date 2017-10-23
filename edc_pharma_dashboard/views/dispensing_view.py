from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import DashboardViewMixin
from edc_pharma.dispense.dispense import Dispense
from edc_pharma.models.prescription import Prescription

from django import forms
from django.apps import apps as django_apps
from django.contrib import messages
from django.core.management.color import color_style
from django.forms.forms import Form
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views.generic.base import TemplateView

from .dispense_print_label_mixin import DispensePrintLabelMixin


style = color_style()


class DispenseForm(Form):

    medications = forms.MultipleChoiceField()


app_config = django_apps.get_app_config('edc_pharma_dashboard')


class DispenseViewMixin(DispensePrintLabelMixin):

    dispense_cls = Dispense

    def get_success_url(self):
        return '/'

    def post(self, request, *args, **kwargs):
        subject_identifier = kwargs.get('subject_identifier')
        prescriptions = []

        error_message = None
        for key in self.request.POST:
            if key.startswith('med'):
                p = Prescription.objects.get(id=self.request.POST.get(key))
                if not p.dispense_appointment.is_dispensed:
                    error_message = "Dispensing is required before printing labels."
                    break
                prescriptions.append(p)
        if not error_message:
            action = self.request.POST.get('action')
            dispense = Dispense(prescriptions=prescriptions, action=action)
            if dispense.printed_labels:
                for label in dispense.printed_labels:
                    medication = label.get('medication')
                    subject_identifier = label.get('subject_identifier')
                    msg = f' Printed {medication} for {subject_identifier}.'
                    messages.add_message(request, messages.SUCCESS, msg)
            else:
                msg = f'Nothing selected for {subject_identifier} FFFF.'
                messages.add_message(request, messages.ERROR, msg)
        else:
            messages.add_message(request, messages.WARNING, error_message)
        url = reverse(
            app_config.appointment_listboard_url_name,
            kwargs={'subject_identifier': subject_identifier})
        return HttpResponseRedirect(url)


class DispensingView(DispenseViewMixin, DashboardViewMixin,
                     EdcBaseViewMixin, TemplateView):
    app_config_name = 'edc_pharma'
