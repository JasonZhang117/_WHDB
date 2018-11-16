from django import forms as dform
from django.forms import fields
from django.forms import widgets
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


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
