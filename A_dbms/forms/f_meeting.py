from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime
from .. import models


# -----------------------评审会添加-------------------------#
class MeetingAddForm(dform.Form):  # 评审会添加
    REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
    review_model = fields.IntegerField(
        label='评审类型',
        label_suffix="：",
        widget=widgets.Select(
            choices=REVIEW_MODEL_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '评审类型'}))
    review_date = fields.DateField(
        label='评审日期',
        label_suffix="：",
        widget=widgets.DateInput(
            attrs={'class': 'form-control',
                   'type': 'date',
                   'placeholder': '评审日期'}),
        initial=str(datetime.date.today))
    article = fields.TypedMultipleChoiceField(
        label="参评项目",
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'placeholder': '选择项目'}))

    def __init__(self, *args, **kwargs):
        super(MeetingAddForm, self).__init__(*args, **kwargs)
        '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                                  (4, '已上会'), (5, '已签批'), (6, '已注销'))
                                  (5, '已签批')-->才能出合同'''
        self.fields['article'].choices = \
            models.Articles.objects.filter(
                article_state=2).values_list(
                'id', 'article_num').order_by('article_num')


# -----------------------添加评审项目-------------------------#
class MeetingArticleAddForm(dform.Form):  # 添加评审项目

    article = fields.TypedMultipleChoiceField(
        label="参评项目",
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'placeholder': '选择项目'}))

    def __init__(self, *args, **kwargs):
        super(MeetingArticleAddForm, self).__init__(*args, **kwargs)
        '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                                  (4, '已上会'), (5, '已签批'), (6, '已注销'))
                                  (5, '已签批')-->才能出合同'''
        self.fields['article'].choices = \
            models.Articles.objects.filter(
                article_state=2).values_list(
                'id', 'article_num').order_by('article_num')


# -----------------------评审会修改-------------------------#
class MeetingEditForm(dform.Form):  # 评审会添加
    REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
    review_model = fields.IntegerField(
        label='评审类型',
        label_suffix="：",
        widget=widgets.Select(
            choices=REVIEW_MODEL_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '评审类型'}))
    review_date = fields.DateField(
        label='评审日期',
        label_suffix="：",
        widget=widgets.DateInput(
            attrs={'class': 'form-control',
                   'type': 'date',
                   'placeholder': '评审日期'}),
        initial=datetime.date.today)


# -----------------------分配项目评委-------------------------#
class MeetingAllotForm(dform.Form):  # 分配项目评委
    expert = fields.TypedMultipleChoiceField(
        label="评审委员",
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'placeholder': '选择评委'}))

    def __init__(self, *args, **kwargs):
        super(MeetingAllotForm, self).__init__(*args, **kwargs)
        self.fields['expert'].choices = \
            models.Experts.objects.order_by(
                'ordery').values_list('id', 'name')


# -----------------------单项额度-------------------------#
class SingleQuotaForm(dform.Form):  # 分配项目评委
    CREDIT_MODEL_LIST = models.SingleQuota.CREDIT_MODEL_LIST
    credit_model = fields.IntegerField(
        label='授信类型',
        label_suffix="：",
        widget=widgets.Select(
            choices=CREDIT_MODEL_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '授信类型'}))
    credit_amount = fields.FloatField(
        label='授信额度（元）',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '授信额度（元）'}))
    flow_rate = fields.FloatField(
        label='费率（%）',
        label_suffix="：",
        widget=widgets.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '费率（%）'}))
