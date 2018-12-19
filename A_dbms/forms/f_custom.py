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
                  'linkman', 'contact_num', 'idustry', 'district']
        widgets = {
            'name': dform.TextInput(attrs={'class': 'form-control',
                                           'placeholder': '客户名称'}),
            'contact_addr': dform.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': '联系地址'}),
            'linkman': dform.TextInput(attrs={'class': 'form-control',
                                              'placeholder': '联系人'}),
            'contact_num': dform.TextInput(attrs={'class': 'form-control',
                                                  'placeholder': '联系电话'}),
        }


# -----------------------企业客户添加-------------------------#
class CustomCAddForm(dform.ModelForm):  # 企业客户
    class Meta:
        model = models.CustomesC
        fields = ['short_name', 'capital', 'registered_addr',
                  'representative']
        widgets = {
            'short_name': dform.TextInput(attrs={'class': 'form-control',
                                                 'placeholder': '简称'}),
            'capital': dform.TextInput(attrs={'class': 'form-control',
                                              'placeholder': '注册资本'}),
            'registered_addr': dform.TextInput(attrs={'class': 'form-control',
                                                      'placeholder': '注册地址'}),
            'representative': dform.TextInput(attrs={'class': 'form-control',
                                                     'placeholder': '法人代表'}),
        }


# -----------------------客户form-------------------------#
class CustomPAddForm(dform.ModelForm):  # 客户form
    class Meta:
        model = models.CustomesP
        fields = ['license_num', 'license_addr']
        widgets = {
            'license_num': dform.TextInput(attrs={'class': 'form-control',
                                                  'placeholder': '身份证号'}),
            'license_addr': dform.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': '身份证地址'}),
        }
