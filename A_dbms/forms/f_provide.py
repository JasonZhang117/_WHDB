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


# -----------------------预收保费-------------------------#
class FormChargeAdd(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['charge', 'charge_fee', ]
        widgets = {
            'charge': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '预收保费（元）'}),
            'charge_fee': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '预收调查费（元）'}),}


# -----------------------收费-------------------------#
class FormProvideChargeAdd(dform.ModelForm):
    class Meta:
        model = models.Charges
        fields = ['charge_typ','rate','amount', 'charge_date', ]
        widgets = {
            'charge_typ': dform.Select(attrs={'class': 'form-control'}),
            'rate': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '费率(%)'}),
            'amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '收费金额（元）'}),
            'charge_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            }


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
        fields = ['contracts_lease', 'contract_guaranty', 'time_limit', 'remark']
        widgets = {
            'contracts_lease': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '借款合同编号'}),
            'contract_guaranty': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '保证合同编号'}),
            'time_limit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '期限'}),
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


# -----------------------放款说明添加-------------------------#
class FormProvideEx(dform.ModelForm):
    class Meta:
        model = models.Provides
        fields = ['obj_typ', 'credit_typ', ]
        widgets = {
            'obj_typ': dform.Select(attrs={'class': 'form-control'}),
            'credit_typ': dform.Select(attrs={'class': 'form-control'}), }


# -----------------------展期-------------------------#
class FormExtensionAdd(dform.ModelForm):
    class Meta:
        model = models.Extension
        fields = ['extension_amount', 'extension_date', 'extension_due_date']
        widgets = {
            'extension_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '展期金额'}),
            'extension_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'extension_due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'})}


# -----------------------放款状态修改-------------------------#
class FormProvideStateChange(dform.ModelForm):
    class Meta:
        model = models.Provides
        fields = ['provide_status', ]
        widgets = {
            'provide_status': dform.Select(attrs={'class': 'form-control'}), }


# -----------------------还款添加-------------------------#
class FormRepaymentAdd(dform.ModelForm):
    class Meta:
        model = models.Repayments
        fields = ['repayment_money', 'repayment_int', 'repayment_pen', 'repayment_date']
        widgets = {
            'repayment_money': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '还款金额'}),
            'repayment_int': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '还款金额'}),
            'repayment_pen': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '还款金额'}),
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
        fields = ['track_typ', 'plan_date', 'proceed', 'term_pri']
        widgets = {
            'track_typ': dform.Select(attrs={'class': 'form-control'}),
            'plan_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proceed': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '跟踪事项'}),
            'term_pri': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '还款金额'}),
             }


# -----------------------跟踪计划-------------------------#
class FormTrackAdd(dform.ModelForm):
    class Meta:
        model = models.Track
        fields = ['track_state']
        widgets = {
            'track_state': dform.Select(attrs={'class': 'form-control'}),}


# -----------------------计划还款明细-------------------------#
class FormTrackEXAdd(dform.ModelForm):
    class Meta:
        model = models.TrackEX
        fields = ['ex_pried','ex_inted','ex_pened','ex_track_date','ex_condition',]
        widgets = {
            'ex_pried': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '本金金额'}),
            'ex_inted': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '利息金额'}),
            'ex_pened': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '违约金金额'}),
            'ex_track_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ex_condition': dform.Textarea(attrs={'class': 'form-control', 'rows': '2', 'placeholder': '备注'}), 
            }
