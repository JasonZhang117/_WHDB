from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------代偿添加-------------------------#
class FormCompensatoryAdd(dform.ModelForm):
    class Meta:
        model = models.Compensatories
        fields = ['compensatory_date', 'compensatory_capital', 'compensatory_interest', 'default_interest']
        widgets = {
            'compensatory_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'compensatory_capital': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '代偿本金金额'}),
            'compensatory_interest': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '代偿利息金额'}),
            'default_interest': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '代偿罚息金额'})}


# -----------------------财产线索添加-------------------------#
class FormClueAdd(dform.Form):
    warrant = fields.TypedMultipleChoiceField(
        label="财产线索", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(FormClueAdd, self).__init__(*args, **kwargs)
        '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), 
        (31, '解保出库'), (99, '已注销'))'''
        '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
        self.fields['warrant'].choices = models.Warrants.objects.exclude(
            warrant_state=99).exclude(warrant_typ=99).values_list('id', 'warrant_num').order_by('warrant_num')


# -----------------------查封情况添加-------------------------#
class FormSealupAdd(dform.ModelForm):
    class Meta:
        model = models.Sealup
        fields = ['sealup_type', 'sealup_date', 'due_date', 'sealup_remark']
        widgets = {
            'sealup_type': dform.Select(attrs={'class': 'form-control'}),
            'sealup_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sealup_remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '查封备注'}),
        }


# -----------------------查询情况添加-------------------------#
class FormInquiryAdd(dform.ModelForm):
    class Meta:
        model = models.Inquiry
        fields = ['inquiry_type', 'inquiry_date', 'inquiry_detail']
        widgets = {
            'inquiry_type': dform.Select(attrs={'class': 'form-control'}),
            'inquiry_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inquiry_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '查询情况'}),
        }


# -----------------------挂网添加-------------------------#
class FormInquiryHangingAdd(dform.ModelForm):
    class Meta:
        model = models.Warrants
        fields = ['auction_date']
        widgets = {
            'auction_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# -----------------------成交添加-------------------------#
class FormInquiryTurnAdd(dform.ModelForm):
    class Meta:
        model = models.Warrants
        fields = ['auction_amount']
        widgets = {
            'auction_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '成交金额'}),
        }


# -----------------------台账添加-------------------------#
class FormStandingAdd(dform.ModelForm):
    class Meta:
        model = models.Standing
        fields = ['standing_detail']
        widgets = {
            'standing_detail': dform.Textarea(attrs={'class': 'form-control', 'placeholder': '追偿情况'}),
        }


# -----------------------追偿费用添加-------------------------#
class FormChargeAdd(dform.ModelForm):
    class Meta:
        model = models.Charge
        fields = ['charge_type', 'charge_amount', 'charge_date', 'charge_remark']
        widgets = {
            'charge_type': dform.Select(attrs={'class': 'form-control'}),
            'charge_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '费用金额'}),
            'charge_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'charge_remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'}),
        }


# -----------------------追偿费用添加-------------------------#
class FormRetrieveAdd(dform.ModelForm):
    class Meta:
        model = models.Retrieve
        fields = ['retrieve_type', 'retrieve_amount', 'retrieve_date', 'retrieve_remark']
        widgets = {
            'retrieve_type': dform.Select(attrs={'class': 'form-control'}),
            'retrieve_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '回收金额'}),
            'retrieve_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'retrieve_remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'}),
        }
