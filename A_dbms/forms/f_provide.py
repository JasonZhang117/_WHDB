from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------风控落实添加-------------------------#
class FormAscertainAdd(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['agree_state', 'agree_remark']
        widgets = {
            'agree_state': dform.Select(attrs={'class': 'form-control'}),
            'agree_remark': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '落实情况'})}


# -----------------------合同签订-------------------------#
class FormAgreeSignAdd(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['sign_date', ]
        widgets = {
            'sign_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}), }


# -----------------------合同状态修改-------------------------#
class FormAgreeChangeState(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['agree_state', ]
        widgets = {
            'agree_state': dform.Select(attrs={'class': 'form-control'}), }


# -----------------------反担保合同签订-------------------------#
class FormCounterSignAdd(dform.ModelForm):
    class Meta:
        model = models.Counters
        fields = ['counter_state', 'counter_sign_date', 'counter_remark']
        widgets = {
            'counter_state': dform.Select(attrs={'class': 'form-control'}),
            'counter_sign_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'counter_remark': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '签订情况'})}


# -----------------------放款通知添加-------------------------#
class FormNotifyAdd(dform.ModelForm):
    class Meta:
        model = models.Notify
        fields = ['notify_money', 'time_limit', 'notify_date', 'contracts_lease', 'contract_guaranty', 'remark']
        widgets = {
            'notify_money': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '通知金额'}),
            'time_limit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '期限'}),
            'notify_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contracts_lease': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '借款合同编号'}),
            'contract_guaranty': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '保证合同编号'}),
            'remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'})}


# -----------------------放款通知修改-------------------------#
class FormNotifyEdit(dform.ModelForm):
    class Meta:
        model = models.Notify
        fields = ['contracts_lease', 'contract_guaranty', 'remark']
        widgets = {
            'contracts_lease': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '借款合同编号'}),
            'contract_guaranty': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '保证合同编号'}),
            'remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'})}


# -----------------------放款添加-------------------------#
class FormProvideAdd(dform.ModelForm):
    class Meta:
        model = models.Provides
        fields = ['provide_typ', 'old_amount', 'new_amount', 'provide_date', 'due_date']
        widgets = {
            'provide_typ': dform.Select(attrs={'class': 'form-control'}),
            'old_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '续贷金额'}),
            'new_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '新增金额'}),
            'provide_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'})}


# -----------------------还款添加-------------------------#
class FormRepaymentAdd(dform.ModelForm):
    class Meta:
        model = models.Repayments
        fields = ['repayment_money', 'repayment_date']
        widgets = {
            'repayment_money': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '还款金额'}),
            'repayment_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'})}


# -----------------------归档添加-------------------------#
class FormImplementAdd(dform.ModelForm):
    class Meta:
        model = models.Pigeonholes
        fields = ['implement']
        '''IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), (41, '已归档')]'''
        widgets = {'implement': dform.Select(attrs={'class': 'form-control'})}


# -----------------------归档添加-------------------------#
class FormPigeonholeAdd(dform.ModelForm):
    class Meta:
        model = models.Pigeonholes
        fields = ['pigeonhole_transfer', 'pigeonhole_explain']
        widgets = {
            'pigeonhole_transfer': dform.Select(attrs={'class': 'form-control'}),
            'pigeonhole_explain': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '归档说明'})}


# -----------------------归档添加-------------------------#
class FormPigeonholeNumAdd(dform.ModelForm):
    class Meta:
        model = models.Provides
        fields = ['file_num']
        widgets = {
            'file_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '档案编号'})}


# -----------------------跟踪计划-------------------------#
class FormTrackPlan(dform.ModelForm):
    class Meta:
        model = models.Track
        fields = ['track_typ', 'plan_date', 'proceed']
        widgets = {
            'track_typ': dform.Select(attrs={'class': 'form-control'}),
            'plan_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proceed': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '跟踪事项'}), }


# -----------------------跟踪计划-------------------------#
class FormTrackAdd(dform.ModelForm):
    class Meta:
        model = models.Track
        fields = ['condition']
        widgets = {
            'condition': dform.Textarea(attrs={'class': 'form-control', 'placeholder': '跟踪情况'}), }
