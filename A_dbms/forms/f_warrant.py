from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------添加房产form-------------------------#
class HouseAddForm(dform.Form):  # 评审会添加
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
