from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime
from .. import models


# -----------------------评审意见form-------------------------#
class CommentsAddForm(dform.Form):  # 评审会添加
    COMMENT_TYPE_LIST = models.Comments.COMMENT_TYPE_LIST
    comment_type = fields.IntegerField(
        label='评委意见',
        label_suffix="：",
        widget=widgets.Select(
            choices=COMMENT_TYPE_LIST,
            attrs={'class': 'form-control',
                   'placeholder': '评委意见'}))
    concrete = fields.CharField(
        label='意见详情',
        label_suffix="：",
        widget=widgets.Textarea(
            attrs={'class': 'form-control',
                   'type': 'date',
                   'placeholder': '意见详情'}))


# -----------------------企业保证担保form-------------------------#
class WarrandiceCustomForm(dform.Form):
    sure = fields.TypedMultipleChoiceField(
        label="保证人",
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'placeholder': '保证人'}))

    def __init__(self, *args, **kwargs):
        super(WarrandiceCustomForm, self).__init__(*args, **kwargs)
        self.fields['sure'].choices = \
            models.Customes.objects.filter(
                genre=1).values_list(
                'id', 'name').order_by('name')


# -----------------------个人保证担保form-------------------------#
class WarrandicePersonForm(dform.Form):
    sure = fields.TypedMultipleChoiceField(
        label="保证人",
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'placeholder': '保证人'}))

    def __init__(self, *args, **kwargs):
        super(WarrandicePersonForm, self).__init__(*args, **kwargs)
        self.fields['sure'].choices = \
            models.Customes.objects.filter(
                genre=2).values_list(
                'id', 'name').order_by('name')
