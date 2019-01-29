from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------保后计划添加-------------------------#
class FormRewiewPlanAdd(dform.ModelForm):
    class Meta:
        model = models.Customes
        fields = ['review_plan_date']
        widgets = {
            'review_plan_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'})}


# -----------------------保后添加-------------------------#
class FormRewiewAdd(dform.ModelForm):
    class Meta:
        model = models.Review
        fields = ['review_sty', 'analysis', 'suggestion', 'classification']
        widgets = {
            'review_sty': dform.Select(attrs={'class': 'form-control'}),
            'analysis': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '风险分析'}),
            'suggestion': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '风控建议'}),
            'classification': dform.Select(attrs={'class': 'form-control'})}
