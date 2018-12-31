from django import forms as dform
from django.forms import fields, widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------委托合同添加-------------------------#
class AgreeAddForm(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['lending', 'branch', 'agree_typ', 'guarantee_typ', 'agree_copies', 'agree_amount']


# -----------------------反担保合同添加-------------------------#
class AddCounterForm(dform.ModelForm):  # 反担保合同添加
    class Meta:
        model = models.Counters
        fields = ['counter_typ']
