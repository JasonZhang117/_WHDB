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
        initial=datetime.date.today)
    article = fields.TypedMultipleChoiceField(
        label="参评项目",
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'placeholder': '选择项目'}))

    def __init__(self, *args, **kwargs):
        super(MeetingAddForm, self).__init__(*args, **kwargs)
        self.fields['article'].choices = \
            models.Articles.objects.filter(
                article_state=1).values_list(
                'id', 'article_num').order_by('article_num')
