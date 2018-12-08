from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------项目添加-------------------------#
class ArticlesAddForm(dform.Form):  # 项目添加
    custom_id = fields.IntegerField(
        label='客户',
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择客户'}))
    renewal = fields.FloatField(
        label='续贷金额（元）',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '输入续贷金额'}))
    augment = fields.FloatField(
        label='新增金额（元）',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '输入新增金额'}))
    credit_term = fields.IntegerField(
        label='授信期限（月）',
        label_suffix="：",
        initial=12,
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '输入授信期限（月）'}))
    director_id = fields.IntegerField(
        label="项目经理",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择项目经理'}))
    assistant_id = fields.IntegerField(
        label="项目助理",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择项目助理'}))
    control_id = fields.IntegerField(
        label="风控专员",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择风控专员'}))

    def __init__(self, *args, **kwargs):
        super(ArticlesAddForm, self).__init__(*args, **kwargs)
        self.fields['custom_id'].widget.choices = \
            models.Customes.objects.values_list(
                'id', 'name').order_by('name')
        self.fields['director_id'].widget.choices = \
            models.Employees.objects.filter(
                job__name='项目经理').values_list(
                'id', 'name').order_by('name')
        self.fields['assistant_id'].widget.choices = \
            models.Employees.objects.filter(
                job__name='项目经理').values_list(
                'id', 'name').order_by('name')
        self.fields['control_id'].widget.choices = \
            models.Employees.objects.filter(
                job__name='风控专员').values_list(
                'id', 'name').order_by('name')


# -----------------------风控反馈添加-------------------------#
class FeedbackAddForm(dform.Form):  # 风控反馈添加
    PROPOSE_LIST = models.Feedback.PROPOSE_LIST
    propose = fields.IntegerField(
        label='上会建议',
        label_suffix="：",
        widget=widgets.Select(
            choices=PROPOSE_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '上会建议'}))

    suggestion = fields.CharField(
        label='风控意见',
        label_suffix="：",
        widget=widgets.Textarea(
            attrs={'class': 'form-control',
                   'placeholder': '风控意见'}))


# -----------------------项目签批-------------------------#
class ArticlesSingForm(dform.Form):  # 项目签批
    summary_num = fields.CharField(
        label='纪要编号',
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '纪要编号'}))

    SIGN_TYPE_LIST = models.Articles.SIGN_TYPE_LIST
    sign_type = fields.IntegerField(
        label='签批结论',
        label_suffix="：",
        widget=widgets.Select(
            choices=SIGN_TYPE_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '签批结论'}),
        initial=1)
    renewal = fields.FloatField(
        label='续贷金额（元）',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '续贷金额（元）'}))
    augment = fields.FloatField(
        label='新增金额（元）',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '新增金额（元）'}))
    sign_detail = fields.CharField(
        label='签批详情',
        label_suffix="：",
        widget=widgets.Textarea(
            attrs={'class': 'form-control',
                   'type': 'date',
                   'placeholder': '签批详情'}))
    sign_date = fields.DateField(
        label='签批日期',
        label_suffix="：",
        widget=widgets.DateInput(
            attrs={'class': 'form-control',
                   'type': 'date',
                   'placeholder': '签批日期'}),
        initial=str(datetime.date.today()))
