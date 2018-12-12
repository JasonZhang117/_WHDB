from django import forms as dform
from django.forms import fields
from django.forms import widgets
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------客户添加-------------------------#
class CustomeAddForm(dform.Form):  # 客户添加
    name = fields.CharField(
        label="客户名称",
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '客户名称'}))
    branch_id = fields.IntegerField(
        label="银行",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择客户'}))
    contact_addr = fields.CharField(
        label="联系地址",
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '联系地址'}))
    linkman = fields.CharField(
        label="联系人",
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '联系人'}))
    contact_num = fields.CharField(
        label="联系电话",
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '联系电话'}))
    GENRE_LIST = models.Customes.GENRE_LIST
    genre = fields.IntegerField(
        label='客户类型',
        label_suffix="：",
        widget=widgets.Select(
            choices=GENRE_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '客户类型'}))


# -----------------------企业客户添加-------------------------#
class CustomesCAddForm(dform.Form):  # 企业客户
    custome_id = fields.IntegerField(
        label="客户",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择客户'}))
    short_name = fields.CharField(
        label="客户简称",
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '客户简称'}))
    capital = fields.FloatField(
        label="注册资本（股本）",
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '注册资本（股本）'}))
    registered_addr = fields.CharField(
        label="注册地址",
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '注册地址'}))
    representative = fields.CharField(
        label="法人代表",
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '法人代表'}))
    idustry = fields.IntegerField(
        label="所属行业",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '所属行业'}))
    district = fields.IntegerField(
        label="所属区域",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '所属区域'}))


# -----------------------客户form-------------------------#
class CustomeForm(dform.Form):  # 客户form
    GENRE_LIST = (('企业', '企业'), ('个人', '个人'))
    name = fields.CharField(label='单位名称',
                            label_suffix="：",
                            max_length=32)
    contact_addr = fields.CharField(label='联系地址',
                                    label_suffix="：",
                                    max_length=64)
    linkman = fields.CharField(label='联系人',
                               label_suffix="：",
                               max_length=16)
    contact_num = fields.CharField(label='联系电话',
                                   label_suffix="：",
                                   max_length=16)
    genre = fields.CharField(
        label='客户类型',
        label_suffix="：",
        widget=widgets.Select(choices=GENRE_LIST))


# -----------------------行业form-------------------------#
class IndustryForm(dform.Form):  # 行业form
    code = dform.CharField(label='行业代码',
                           label_suffix="：",
                           initial='C4190')
    name = dform.CharField(label='行业名称',
                           label_suffix="：",
                           initial='其他未列明制造业')
