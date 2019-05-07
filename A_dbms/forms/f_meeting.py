from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime, time
from .. import models


# -----------------------评审会添加-------------------------#
class MeetingAddForm(dform.Form):  # 评审会添加
    REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
    review_model = fields.IntegerField(
        label='评审类型', label_suffix="：", initial=1,
        widget=widgets.Select(choices=REVIEW_MODEL_LIST, attrs={'class': 'form-control'}))
    review_date = fields.DateField(
        label='评审日期', label_suffix="：", initial=str(datetime.date.today()),
        widget=widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    article = fields.TypedMultipleChoiceField(
        label="参评项目", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(MeetingAddForm, self).__init__(*args, **kwargs)
        '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
        '''PROPOSE_LIST = ((1, '符合上会条件'), (11, '暂不符合上会条件'), (21, '建议终止项目'))'''
        self.fields['article'].choices = models.Articles.objects.filter(
            article_state=2, feedback_article__propose=1).values_list('id', 'article_num').order_by('article_num')


# -----------------------添加评审项目-------------------------#
class MeetingArticleAddForm(dform.Form):  # 添加评审项目

    article = fields.TypedMultipleChoiceField(
        label="参评项目", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(MeetingArticleAddForm, self).__init__(*args, **kwargs)
        '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
            (4, '已上会'), (5, '已签批'), (6, '已注销'))
            ((0, '--------------'), (1, '符合上会条件'),
            (2, '暂不符合上会条件'), (3, '建议终止项目'))'''
        self.fields['article'].choices = models.Articles.objects.filter(
            article_state=2, feedback_article__propose=1).values_list('id', 'article_num').order_by('article_num')


# -----------------------评审会修改-------------------------#
class MeetingEditForm(dform.Form):  # 评审会添加
    REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
    review_model = fields.IntegerField(
        label='评审类型', label_suffix="：",
        widget=widgets.Select(choices=REVIEW_MODEL_LIST, attrs={'class': 'form-control'}))
    review_date = fields.DateField(
        label='评审日期', label_suffix="：", initial=datetime.date.today,
        widget=widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}))


# -----------------------分配项目评委-------------------------#
class MeetingAllotForm(dform.Form):  # 分配项目评委
    expert = fields.TypedMultipleChoiceField(
        label="评审委员", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(MeetingAllotForm, self).__init__(*args, **kwargs)
        '''EXPERT_STATE_LIST = ((1, '正常'), (2, '注销'))'''
        self.fields['expert'].choices = models.Experts.objects.filter(
            expert_state=1).order_by('ordery').values_list('id', 'name')


# -----------------------单项额度-------------------------#
class SingleQuotaForm(dform.Form):  # 分配项目评委
    CREDIT_MODEL_LIST = models.SingleQuota.CREDIT_MODEL_LIST
    credit_model = fields.IntegerField(
        label='授信类型', label_suffix="：",
        widget=widgets.Select(choices=CREDIT_MODEL_LIST, attrs={'class': 'form-control'}))
    credit_amount = fields.FloatField(
        label='授信额度（元）', label_suffix="：",
        widget=widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': '授信额度（元）'}))
    flow_rate = fields.CharField(
        label='费率（%）', label_suffix="：",
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '费率'}))


# -----------------------放款次序-------------------------#
class FormLendingOrder(dform.ModelForm):  # 放款次序
    class Meta:
        model = models.LendingOrder
        fields = ['order', 'order_amount']
        widgets = {
            'order': dform.Select(attrs={'class': 'form-control'}),
            'order_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '拟放款金额（元）'})}
