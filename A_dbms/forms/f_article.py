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
    article_date = fields.DateField(
        label='提交日期',
        label_suffix="：",
        widget=widgets.DateInput(
            attrs={'class': 'form-control',
                   'type': 'date',
                   'placeholder': '项目提交日期'}),
        initial=datetime.date.today)

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


# -----------------------项目只读-------------------------#
class ArticlesAdForm(dform.Form):  # 项目只读
    article_num = fields.CharField(
        label='项目编号',
        label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '项目编号',
                   'disabled': ''}))
    custom_id = fields.IntegerField(
        label='客户',
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择客户',
                   'disabled': ''}))
    renewal = fields.FloatField(
        label='续贷金额（元）',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '输入续贷金额',
                   'disabled': ''}))
    augment = fields.FloatField(
        label='新增金额（元）',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '输入新增金额',
                   'disabled': ''}))
    credit_term = fields.IntegerField(
        label='授信期限（月）',
        label_suffix="：",
        initial=12,
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '输入授信期限（月）',
                   'disabled': ''}))
    director_id = fields.IntegerField(
        label="项目经理",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择项目经理',
                   'disabled': ''}))
    assistant_id = fields.IntegerField(
        label="项目助理",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择项目助理',
                   'disabled': ''}))
    control_id = fields.IntegerField(
        label="风控专员",
        label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control',
                   'placeholder': '选择风控专员',
                   'disabled': ''}))
    article_date = fields.DateField(
        label='提交日期',
        label_suffix="：",
        widget=widgets.DateInput(
            attrs={'class': 'form-control',
                   'type': 'date',
                   'placeholder': '项目提交日期',
                   'disabled': ''}),
        initial=datetime.date.today)

    def __init__(self, *args, **kwargs):
        super(ArticlesAdForm, self).__init__(*args, **kwargs)
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


# -----------------------项目上会-------------------------#
class AppraisalForm(dform.Form):  # 行业form
    expert = fields.TypedMultipleChoiceField(
        label='评审',
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'placeholder': '选择评审'}))
    review_order = fields.IntegerField(
        label="评审次序",
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '输入评审次序'}))
    review_date = fields.DateField(
        label='评审日期',
        label_suffix="：",
        widget=widgets.DateInput(
            attrs={'class': 'form-control',
                   'type': 'date',
                   'placeholder': '输入日期'}),
        initial=datetime.date.today)

    def __init__(self, *args, **kwargs):
        super(AppraisalForm, self).__init__(*args, **kwargs)
        self.fields['expert'].choices = \
            models.Experts.objects.values_list('id', 'name')


# -----------------------项目签批-------------------------#
class ArticlesSignForm(dform.Form):  # 行业form
    summary_num = fields.CharField(label='纪要编号',
                                   label_suffix="：")
    flow_credit = fields.FloatField(label='流贷额度（元）',
                                    label_suffix="：", )
    flow_rate = fields.FloatField(label='流贷费率（%）',
                                  label_suffix="：", )
    honour_credit = fields.FloatField(label='承兑额度（元）',
                                      label_suffix="：", )
    honour_rate = fields.FloatField(label='承兑费率（%）',
                                    label_suffix="：", )
    accept_credit = fields.FloatField(label='保函额度（元）',
                                      label_suffix="：", )
    accept_rate = fields.FloatField(label='保函费率（%）',
                                    label_suffix="：", )
    sign_date = fields.DateField(label='签批日期',
                                 label_suffix="：",
                                 initial=datetime.date.today)


# -----------------------纪要-------------------------#
class SummaryForm(dform.Form):  # 纪要
    ARTICLE_STATE_LIST = [('待反馈', '待反馈'), ('待上会', '待上会'),
                          ('无补调', '无补调'), ('需补调', '需补调'),
                          ('已补调', '已补调'), ('已签批', '已签批')]
    REVIEW_MODEL_LIST = [('内审', '内审'), ('外审', '外审')]
    article_num = fields.CharField(label='_项目编号',
                                   label_suffix="：",
                                   disabled=True)
    custom_id = fields.IntegerField(label='客户',
                                    label_suffix="：",
                                    widget=widgets.Select(),
                                    disabled=True)
    renewal = fields.FloatField(label='续贷金额（元）',
                                label_suffix="：",
                                disabled=True)
    augment = fields.FloatField(label='新增金额（元）',
                                label_suffix="：",
                                disabled=True)
    credit_term = fields.IntegerField(label='授信期限（月）',
                                      label_suffix="：",
                                      initial=12,
                                      disabled=True)
    director_id = fields.IntegerField(label="项目经理",
                                      label_suffix="：",
                                      widget=widgets.Select(),
                                      disabled=True)
    assistant_id = fields.IntegerField(label="项目助理",
                                       label_suffix="：",
                                       widget=widgets.Select(),
                                       disabled=True)
    control_id = fields.IntegerField(label="风控专员",
                                     label_suffix="：",
                                     widget=widgets.Select(),
                                     disabled=True)
    article_date = fields.DateField(label='提交日期',
                                    label_suffix="：",
                                    initial=datetime.date.today,
                                    disabled=True)
    article_state = fields.CharField(
        label='项目状态',
        label_suffix="：",
        widget=widgets.Select(choices=ARTICLE_STATE_LIST))
    expert = fields.TypedMultipleChoiceField(
        label='评审',
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(), )
    review_model = fields.CharField(
        label='评审类型',
        label_suffix="：",
        widget=widgets.Select(choices=REVIEW_MODEL_LIST))
    review_order = fields.IntegerField(label="评审次序",
                                       label_suffix="：")
    review_date = fields.DateField(label='评审日期',
                                   label_suffix="：")
    flow_credit = fields.FloatField(label='流贷额度（元）',
                                    label_suffix="：", )
    flow_rate = fields.FloatField(label='流贷费率（%）',
                                  label_suffix="：", )
    honour_credit = fields.FloatField(label='承兑额度（元）',
                                      label_suffix="：", )
    honour_rate = fields.FloatField(label='承兑费率（%）',
                                    label_suffix="：", )
    accept_credit = fields.FloatField(label='保函额度（元）',
                                      label_suffix="：", )
    accept_rate = fields.FloatField(label='保函费率（%）',
                                    label_suffix="：", )
    sign_date = fields.DateField(label='签批日期',
                                 label_suffix="：")

    def __init__(self, *args, **kwargs):
        super(SummaryForm, self).__init__(*args, **kwargs)
        self.fields['custom_id'].widget.choices = \
            models.Customes.objects.values_list(
                'id', 'name').order_by('name')
        self.fields['director_id'].widget.choices = \
            models.Employees.objects.filter(
                job__job_name='项目经理').values_list(
                'id', 'name').order_by('name')
        self.fields['assistant_id'].widget.choices = \
            models.Employees.objects.filter(
                job__job_name='项目经理').values_list(
                'id', 'name').order_by('name')
        self.fields['control_id'].widget.choices = \
            models.Employees.objects.filter(
                job__job_name='风控专员').values_list(
                'id', 'name').order_by('name')
        self.fields['expert'].choices = \
            models.Experts.objects.values_list(
                'id', 'name')
