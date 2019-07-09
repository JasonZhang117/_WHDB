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


# -----------------------追偿项目添加-------------------------#
class FormDunAdd(dform.Form):
    cmpensatory = fields.TypedMultipleChoiceField(
        label="财产线索", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(FormDunAdd, self).__init__(*args, **kwargs)
        '''DUN_STATE_LIST = ((1, '已代偿'), (11, '已起诉'), (21, '已判决'), (31, '已和解'), (41, '执行中'), 
                            (91, '结案'))'''
        self.fields['cmpensatory'].choices = models.Compensatories.objects.filter(
            dun_state=1).values_list('id', 'title').order_by('title')


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


# -----------------------被告人添加-------------------------#
class FormCustomAdd(dform.Form):
    custom = fields.TypedMultipleChoiceField(
        label="被告人", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(FormCustomAdd, self).__init__(*args, **kwargs)
        '''CUSTOM_STATE_LIST = ((1, '正常'), (99, '注销'))'''
        self.fields['custom'].choices = models.Customes.objects.filter(
            custom_state=1).values_list('id', 'name').order_by('name')


# -----------------------目录添加-------------------------#
class FormStageAdd(dform.ModelForm):
    class Meta:
        model = models.Stage
        fields = ['stage_type', 'stage_file', 'stage_date', 'stage_state', 'page_amout']
        widgets = {
            'stage_type': dform.Select(attrs={'class': 'form-control'}),
            'stage_file': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '文件'}),
            'stage_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'page_amout': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '页数'}),
            'stage_state': dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------联系人添加-------------------------#
class FormStaffAdd(dform.ModelForm):
    class Meta:
        model = models.Staff
        fields = ['staff_name', 'staff_type', 'contact_number', 'staff_remark']
        widgets = {
            'staff_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '姓名'}),
            'staff_type': dform.Select(attrs={'class': 'form-control'}),
            'contact_number': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '联系电话'}),
            'staff_remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'}),
        }


# -----------------------代理合同添加-------------------------#
class FormAgentAdd(dform.ModelForm):
    class Meta:
        model = models.Agent
        fields = ['agent_agree', 'agent_item', 'fee_scale', 'agent_date', 'due_date', 'agent_remark']
        widgets = {
            'agent_agree': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '合同编号'}),
            'agent_item': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '代理事项'}),
            'fee_scale': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '收费标准'}),
            'agent_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'agent_remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'}),
        }


# -----------------------判决书添加-------------------------#
class FormJudgmentAdd(dform.ModelForm):
    class Meta:
        model = models.Judgment
        fields = ['judgment_file', 'judgment_detail', 'judgment_unit', 'judgment_date']
        widgets = {
            'judgment_file': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '文件'}),
            'judgment_detail': dform.Textarea(attrs={'class': 'form-control', 'placeholder': '判决内容'}),
            'judgment_unit': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '单位'}),
            'judgment_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


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
        fields = ['inquiry_type', 'inquiry_detail']
        widgets = {
            'inquiry_type': dform.Select(attrs={'class': 'form-control'}),
            'inquiry_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '查询情况'}),
        }


# -----------------------评估添加-------------------------#
class FormInquiryEvaluateAdd(dform.ModelForm):
    class Meta:
        model = models.Inquiry
        fields = ['evaluate_date', 'evaluate_value']
        widgets = {
            'evaluate_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'evaluate_value': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '评估价格'}),
        }


# -----------------------挂网添加-------------------------#
class FormInquiryHangingAdd(dform.ModelForm):
    class Meta:
        model = models.Inquiry
        fields = ['auction_date', 'listing_price']
        widgets = {
            'auction_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'listing_price': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '挂网价格'}),
        }


# -----------------------成交添加-------------------------#
class FormInquiryTurnAdd(dform.ModelForm):
    class Meta:
        model = models.Inquiry
        fields = ['transaction_date', 'auction_amount']
        widgets = {
            'transaction_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
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
