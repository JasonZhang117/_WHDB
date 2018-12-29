from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------权证添加-------------------------#
class WarrantAddForm(dform.ModelForm):
    class Meta:
        model = models.Warrants
        fields = ['warrant_num', 'warrant_typ']
        widgets = {
            'warrant_num': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '权证编码'})}


# -----------------------权证编辑-------------------------#
class WarrantEditForm(dform.Form):
    warrant_num = fields.CharField(
        label='权证编码', label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '权证编码'}))


# ------------------OwerShipEditForm产权证编辑-------------------#
class OwerShipAddForm(dform.ModelForm):  # OwerShipEditForm产权证编辑
    ownership_num = fields.CharField(
        label="产权证编号", label_suffix="：", max_length=32,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '产权证编号'}))

    class Meta:
        model = models.Ownership
        fields = ['owner']


# -----------------------房产modelform-------------------------#
class HouseAddEidtForm(dform.ModelForm):
    house_locate = fields.CharField(
        label="房产坐落", label_suffix="：", max_length=64,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '房产坐落'}))

    class Meta:
        model = models.Houses
        fields = ['house_app', 'house_area']


# -----------------------土地modelform-------------------------#
class GroundAddEidtForm(dform.ModelForm):
    ground_locate = fields.CharField(
        label="土地坐落", label_suffix="：", max_length=64,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '土地坐落'}))

    class Meta:
        model = models.Grounds
        fields = ['ground_app', 'ground_area']


# -----------------------HypothecsAddEidtForm他权-------------------------#
class HypothecsAddEidtForm(dform.ModelForm):
    class Meta:
        model = models.Hypothecs
        fields = ['agree']


# -----------------------HypothecsAddEidtForm他权-------------------------#
class HypothecGuarantyAddEidtForm(dform.Form):
    warrant = fields.TypedMultipleChoiceField(
        label="抵押物", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(HypothecGuarantyAddEidtForm, self).__init__(*args, **kwargs)
        '''((1, '企业'), (2, '个人'))'''
        self.fields['warrant'].choices = models.Warrants.objects.exclude(
            warrant_typ__exact=9).values_list('id', 'warrant_num')


# -----------------------StoragesAddEidtForm出入库-------------------------#
class StoragesAddEidtForm(dform.ModelForm):
    class Meta:
        model = models.Storages
        fields = ['storage_typ', 'storage_date', 'transfer']

    widgets = {
        'storage_date': widgets.DateInput(
            attrs={'class': 'form-control', 'type': 'date',
                   'placeholder': '权证编码'})}
