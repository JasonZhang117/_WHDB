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
