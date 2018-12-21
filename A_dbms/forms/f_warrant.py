from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------权证添加-------------------------#
class WarrantAddForm(dform.ModelForm):
    class Meta:
        model = models.Warrants
        fields = ['warrant_num', 'warrant_typ']
        widgets = {
            'warrant_num': dform.TextInput(attrs={'class': 'form-control',
                                                  'placeholder': '权证编号'}),
        }


# -----------------------权证编辑-------------------------#
class WarrantEditForm(dform.ModelForm):
    class Meta:
        model = models.Warrants
        fields = ['warrant_num']
        widgets = {
            'warrant_num': dform.TextInput(attrs={'class': 'form-control',
                                                  'placeholder': '权证编号'}),
        }


# -----------------------添加房产form-------------------------#
class HouseAddForm(dform.Form):  # 添加房产form
    warrant_num = fields.CharField(
        label='房产编号',
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '房产编号'}))
    house_locate = fields.CharField(
        label='坐落',
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '坐落'}))
    HOUSE_APP_LIST = models.Houses.HOUSE_APP_LIST
    house_app = fields.IntegerField(
        label='用途',
        label_suffix="：",
        widget=widgets.Select(
            choices=HOUSE_APP_LIST,
            attrs={'class': 'form-control'}))
    house_area = fields.FloatField(
        label="建筑面积",
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '建筑面积（平方米)'}))


# -----------------------添加土地form-------------------------#
class GroundAddForm(dform.Form):  # 添加土地form
    warrant_num = fields.CharField(
        label='土地编号',
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '土地编号'}))
    ground_locate = fields.CharField(
        label='坐落',
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '坐落'}))
    GROUND_APP_LIST = models.Grounds.GROUND_APP_LIST
    ground_app = fields.IntegerField(
        label='用途',
        label_suffix="：",
        widget=widgets.Select(
            choices=GROUND_APP_LIST,
            attrs={'class': 'form-control'}))
    ground_area = fields.FloatField(
        label="面积",
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '面积（平方米)'}))


# -----------------------添加房产form-------------------------#
class HouseAddForm(dform.Form):  # 添加房产form
    warrant_num = fields.CharField(
        label='房产编号',
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '房产编号'}))
    house_locate = fields.CharField(
        label='坐落',
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '坐落'}))
    HOUSE_APP_LIST = models.Houses.HOUSE_APP_LIST
    house_app = fields.IntegerField(
        label='用途',
        label_suffix="：",
        widget=widgets.Select(
            choices=HOUSE_APP_LIST,
            attrs={'class': 'form-control'}))
    house_area = fields.FloatField(
        label="建筑面积",
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '建筑面积（平方米)'}))
