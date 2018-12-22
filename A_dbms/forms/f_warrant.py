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
                attrs={'class': 'form-control',
                       'placeholder': '权证编号'}),
        }


# -----------------------权证编辑-------------------------#
class WarrantEditForm(dform.Form):
    warrant_num = fields.CharField(
        label="权证编号",
        label_suffix="：",
        max_length=32,
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '权证编号'}))


# -----------------------房产modelform-------------------------#
class HouseAddEidtForm(dform.ModelForm):
    house_locate = fields.CharField(
        label="房产坐落",
        label_suffix="：",
        max_length=64,
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '房产坐落'}))

    class Meta:
        model = models.Houses
        fields = ['house_app', 'house_area']


# -----------------------土地modelform-------------------------#
class GroundAddEidtForm(dform.ModelForm):
    ground_locate = fields.CharField(
        label="土地坐落",
        label_suffix="：",
        max_length=64,
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '土地坐落'}))

    class Meta:
        model = models.Grounds
        fields = ['ground_app', 'ground_area']
