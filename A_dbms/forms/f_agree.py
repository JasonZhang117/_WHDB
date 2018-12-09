from django import forms as dform
from django.forms import fields, widgets
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


# -----------------------反担保合同添加-------------------------#
class AddCounterForm(dform.Form):  # 反担保合同添加
    agree_id = fields.IntegerField(
        label="委托合同",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '委托合同'}))
    COUNTER_TYP_LIST = models.Counters.COUNTER_TYP_LIST
    counter_typ = fields.IntegerField(
        label='反担保类型',
        label_suffix="：",
        widget=widgets.Select(
            choices=COUNTER_TYP_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '反担保类型'}))

    def __init__(self, *args, **kwargs):
        super(AddCounterForm, self).__init__(*args, **kwargs)
        '''((1, '待签批'), (2, '已签批'), (3, '已落实'),
           (4, '已放款'), (5, '已解保'), (6, '已作废'))'''
        self.fields['agree_id'].widget.choices = \
            models.Agrees.objects.filter(agree_state=1). \
                values_list('id', 'agree_num'). \
                order_by('-id')
