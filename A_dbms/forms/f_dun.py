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


# -----------------------查封财产添加-------------------------#
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
