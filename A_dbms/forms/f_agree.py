from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------委托合同添加-------------------------#
class AgreeAddForm(dform.Form):  # 委托合同添加
    article_id = fields.IntegerField(
        label="纪要",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择客户'}))
    branch_id = fields.IntegerField(
        label="银行",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择客户'}))
    AGREE_TYP_LIST = models.Agrees.AGREE_TYP_LIST
    agree_typ = fields.IntegerField(
        label='合同类型',
        label_suffix="：",
        widget=widgets.Select(
            choices=AGREE_TYP_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '合同类型'}))
    agree_amount = fields.FloatField(
        label="合同金额(元)",
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '合同金额（元）'}))

    def __init__(self, *args, **kwargs):
        super(AgreeAddForm, self).__init__(*args, **kwargs)
        ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                              (3, '无补调'), (4, '需补调'),
                              (5, '已补调'), (6, '已签批'))
        self.fields['article_id'].widget.choices = \
            models.Articles.objects.filter(article_state=6). \
                values_list('id', 'summary_num'). \
                order_by('summary_num')
        self.fields['branch_id'].widget.choices = \
            models.Branches.objects.filter(branch_state=1). \
                values_list('id', 'name').order_by('name')
