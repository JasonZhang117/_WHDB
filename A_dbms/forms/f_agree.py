from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------委托合同添加-------------------------#
class AgreeAddForm(dform.Form):  # 委托合同添加
    article_id = fields.IntegerField(
        label="项目纪要",
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
    GUARANTEE_TYP_LIST = models.Agrees.GUARANTEE_TYP_LIST
    guarantee_typ = fields.CharField(
        label='类型数量',
        label_suffix="：",
        widget=widgets.Select(
            choices=GUARANTEE_TYP_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '类型数量'}),
        initial='④')

    agree_copies = fields.IntegerField(
        label='合同份数',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '合同份数'}),
        initial=4)

    def __init__(self, *args, **kwargs):
        super(AgreeAddForm, self).__init__(*args, **kwargs)
        '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
           (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
        self.fields['article_id'].widget.choices = \
            models.Articles.objects.filter(article_state=5). \
                values_list('id', 'summary_num'). \
                order_by('-summary_num')
        self.fields['branch_id'].widget.choices = \
            models.Branches.objects.filter(branch_state=1). \
                values_list('id', 'name').order_by('name')
