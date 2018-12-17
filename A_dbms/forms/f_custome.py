from django import forms as dform
from django.forms import fields
from django.forms import widgets
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------客户添加-------------------------#
class CustomAddForm(dform.ModelForm):
    class Meta:
        model = models.Customes
        fields = ['name', 'genre', 'contact_addr',
                  'linkman', 'contact_num']


# -----------------------企业客户添加-------------------------#
class CustomCAddForm(dform.ModelForm):  # 企业客户
    class Meta:
        model = models.CustomesC
        fields = ['short_name', 'capital', 'registered_addr',
                  'representative', 'idustry', 'district']


# -----------------------客户form-------------------------#
class CustomPAddForm(dform.ModelForm):  # 客户form
    class Meta:
        model = models.CustomesP
        fields = ['license_num', 'registered_addr']
