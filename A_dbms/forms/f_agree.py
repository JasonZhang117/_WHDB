from django import forms as dform
from django.forms import fields, widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------委托合同添加-------------------------#
class AgreeAddForm(dform.ModelForm):
    branch = fields.ChoiceField(
        label="放款银行", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Agrees
        fields = ['lending', 'agree_typ', 'guarantee_typ', 'agree_copies', 'agree_amount',
                  'amount_limit', 'agree_term', 'other']
        widgets = {'lending': dform.Select(attrs={'class': 'form-control'}),
                   'agree_typ': dform.Select(attrs={'class': 'form-control'}),
                   'guarantee_typ': dform.Select(attrs={'class': 'form-control'}),
                   'agree_copies': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同份数'}),
                   'agree_term': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '期限'}),
                   'agree_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同金额（元）'}),
                   'amount_limit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '放款限额（元）'}),
                   'other': dform.Textarea(attrs={'class': 'form-control', 'rows': '2', 'placeholder': '其他合同约定事项'}),
                   }

    def __init__(self, *args, **kwargs):
        super(AgreeAddForm, self).__init__(*args, **kwargs)
        self.fields['branch'].choices = models.Branches.objects.filter(branch_state=1).values_list(
            'id', 'name').order_by('name')


# -----------------------委托合同修改-------------------------#
class AgreeEditForm(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['branch', 'agree_typ', 'agree_amount', 'amount_limit', 'agree_rate', 'agree_term',
                  'guarantee_typ', 'agree_copies', 'other']
        widgets = {
            'branch': dform.Select(attrs={'class': 'form-control'}),
            'agree_typ': dform.Select(attrs={'class': 'form-control'}),
            'agree_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同金额（元）'}),
            'amount_limit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '放款限额（元）'}),
            'agree_rate': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '如为单项合同输入纯数字'}),
            'agree_term': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '期限'}),
            'guarantee_typ': dform.Select(attrs={'class': 'form-control'}),
            'agree_copies': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同份数'}),
            'other': dform.Textarea(attrs={'class': 'form-control', 'rows': '1', 'placeholder': '其他合同约定事项'}),
        }


# -----------------------声明承诺添加-------------------------#
class PromiseAddForm(dform.ModelForm):
    class Meta:
        model = models.ResultState
        fields = ['custom', 'result_typ', 'result_detail']
        widgets = {
            'custom': dform.Select(attrs={'class': 'form-control'}),
            'result_typ': dform.Select(attrs={'class': 'form-control'}),
            'result_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '决议声明内容'}),
        }


# -----------------------合同签批-------------------------#
class FormAgreeSign(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['agree_sign_date']
        widgets = {'agree_sign_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'})}


initial = str(datetime.date.today()),


# -----------------------反担保合同添加-------------------------#
class AddCounterForm(dform.ModelForm):  # 反担保合同添加
    class Meta:
        model = models.Counters
        fields = ['counter_typ', 'counter_other']
        widgets = {'counter_typ': dform.Select(attrs={'class': 'form-control'}),
                   'counter_other': dform.Textarea(
                       attrs={'class': 'form-control', 'rows': '1', 'placeholder': '其他合同约定事项'}), }
