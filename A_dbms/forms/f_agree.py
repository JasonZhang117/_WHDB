from django import forms as dform
from django.forms import fields, widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------委托合同添加-------------------------#
class AgreeAddForm(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['lending', 'branch', 'agree_typ', 'guarantee_typ',
                  'agree_copies', 'agree_amount']


# -----------------------反担保合同添加-------------------------#
class AddCounterForm(dform.Form):  # 反担保合同添加
    agree_id = fields.IntegerField(
        label="委托合同", label_suffix="：",
        widget=widgets.Select(
            attrs={'class': 'form-control'}))
    COUNTER_TYP_LIST = models.Counters.COUNTER_TYP_LIST
    counter_typ = fields.IntegerField(
        label='反担保类型', label_suffix="：",
        widget=widgets.Select(
            choices=COUNTER_TYP_LIST, attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(AddCounterForm, self).__init__(*args, **kwargs)
        '''((1, '待签批'), (2, '已签批'), (3, '已落实'),
           (4, '已放款'), (5, '已解保'), (6, '已作废'))'''
        self.fields['agree_id'].widget.choices = models.Agrees.objects.filter(
            agree_state=1).values_list('id', 'agree_num').order_by('-id')


# -----------------------企业反担保合同添加-------------------------#
class CountersAssureC(dform.Form):
    custome_c = fields.TypedMultipleChoiceField(
        label="保证人", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CountersAssureC, self).__init__(*args, **kwargs)
        '''((1, '企业'), (2, '个人'))'''
        self.fields['custome_c'].choices = models.Customes.objects.filter(
            genre=1).values_list('id', 'name').order_by('name')


# -----------------------个人反担保合同添加-------------------------#
class CountersAssureP(dform.Form):
    custome_p = fields.TypedMultipleChoiceField(
        label="保证人", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CountersAssureP, self).__init__(*args, **kwargs)
        '''((1, '企业'), (2, '个人'))'''
        self.fields['custome_p'].choices = models.Customes.objects.filter(
            genre=2).values_list('id', 'name').order_by('name')


# -----------------------房产抵押反担保合同添加-------------------------#
class CountersHouse(dform.Form):
    house = fields.TypedMultipleChoiceField(
        label="房产", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CountersHouse, self).__init__(*args, **kwargs)
        self.fields['house'].choices = models.Houses.objects.values_list(
            'id', 'house_locate').order_by('id')


# -----------------------土地反担保合同添加-------------------------#
class CountersGround(dform.Form):
    ground = fields.TypedMultipleChoiceField(
        label="土地", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CountersGround, self).__init__(*args, **kwargs)
        self.fields['ground'].choices = models.Grounds.objects.values_list(
            'id', 'ground_locate').order_by('id')
