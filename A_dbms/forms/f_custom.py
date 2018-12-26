from django import forms as dform
from django.forms import fields
from django.forms import widgets
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------客户添加-------------------------#
class CustomAddForm(dform.ModelForm):
    class Meta:
        model = models.Customes
        fields = ['name', 'contact_addr', 'linkman', 'contact_num', 'genre']
        widgets = {
            'name': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '客户名称'}),
            'contact_addr': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '联系地址'}),
            'linkman': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '联系人'}),
            'contact_num': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '联系电话'})}


# -----------------------客户编辑-------------------------#
class CustomEditForm(dform.ModelForm):
    name = fields.CharField(
        label="客户名称", label_suffix="：", max_length=32,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '客户名称'}))

    class Meta:
        model = models.Customes
        fields = ['contact_addr', 'linkman', 'contact_num']
        widgets = {
            'contact_addr': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '联系地址'}),
            'linkman': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '联系人'}),
            'contact_num': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '联系电话'})}


# -----------------------企业客户添加-------------------------#
class CustomCAddForm(dform.ModelForm):  # 企业客户
    short_name = fields.CharField(
        label="客户简称", label_suffix="：", max_length=32,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '客户简称'}))

    class Meta:
        model = models.CustomesC
        fields = ['idustry', 'district', 'capital', 'registered_addr', 'representative']
        widgets = {
            'capital': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '注册资本'}),
            'registered_addr': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '注册地址'}),
            'representative': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '法人代表'})}

    # -----------------------客户form-------------------------#


class CustomPAddForm(dform.ModelForm):  # 客户form
    license_num = fields.CharField(
        label="身份证号",
        label_suffix="：",
        max_length=18,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '身份证号'}))

    class Meta:
        model = models.CustomesP
        fields = ['license_addr']
        widgets = {
            'license_addr': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '身份证地址'})}
