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


# -----------------------分类-------------------------#
class FormFicationAdd(dform.ModelForm):
    class Meta:
        model = models.Fication
        fields = ['fic_date', 'fication', 'explain', ]
        widgets = {
            'fic_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fication': dform.Select(attrs={'class': 'form-control'}),
            'explain': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '分类说明'}),
        }


# -----------------------一件分类-------------------------#
class FormFicationAll(dform.ModelForm):
    class Meta:
        model = models.Fication
        fields = ['fic_date', 'fication', ]
        widgets = {
            'fic_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fication': dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------保后添加-------------------------#
class FormRewiewAdd(dform.ModelForm):
    class Meta:
        model = models.Review
        fields = ['review_sty', 'analysis', 'suggestion', 'classification', 'review_date']
        widgets = {
            'review_sty': dform.Select(attrs={'class': 'form-control'}),
            'analysis': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '风险分析'}),
            'suggestion': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '风控建议'}),
            'classification': dform.Select(attrs={'class': 'form-control'}),
            'review_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}), }


# -----------------------补调添加-------------------------#
class FormInvestigateAdd(dform.ModelForm):
    class Meta:
        model = models.Investigate
        fields = ['inv_typ', 'i_analysis', 'i_suggestion', 'i_classification', 'inv_date']
        widgets = {
            'inv_typ': dform.Select(attrs={'class': 'form-control'}),
            'i_analysis': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '风险分析'}),
            'i_suggestion': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '风控建议'}),
            'i_classification': dform.Select(attrs={'class': 'form-control'}),
            'inv_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}), }
