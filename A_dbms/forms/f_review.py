from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------包后计划添加-------------------------#
class FormRewiewPlanAdd(dform.ModelForm):
    class Meta:
        model = models.Customes
        fields = ['review_plan_date']
        widgets = {
            'review_plan_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'})}
