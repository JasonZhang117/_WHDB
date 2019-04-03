from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime
from .. import models


# -----------------------评审意见form-------------------------#
class CommentsAddForm(dform.Form):  # 评审会添加
    COMMENT_TYPE_LIST = models.Comments.COMMENT_TYPE_LIST
    comment_type = fields.IntegerField(
        label='评委意见', label_suffix="：",
        widget=widgets.Select(choices=COMMENT_TYPE_LIST, attrs={'class': 'form-control'}))
    concrete = fields.CharField(
        label='意见详情', label_suffix="：",
        widget=widgets.Textarea(attrs={'class': 'form-control', 'rows': '5', 'placeholder': '意见详情'}))


# -----------------------项目签批-------------------------#
class ArticlesSignForm(dform.Form):  # 项目签批
    SIGN_TYPE_LIST = models.Articles.SIGN_TYPE_LIST
    sign_type = fields.IntegerField(
        label='签批结论', label_suffix="：", initial=1,
        widget=widgets.Select(choices=SIGN_TYPE_LIST, attrs={'class': 'form-control'}))
    renewal = fields.FloatField(
        label='本次续贷', label_suffix="：",
        widget=widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': '本次续贷额度（元）'}))
    augment = fields.FloatField(
        label='本次新增', label_suffix="：",
        widget=widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': '本次新增额度（元）'}))
    credit_amount = fields.FloatField(
        label='客户授信总额', label_suffix="：",
        widget=widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': '客户授信总额（元）'}))
    rcd_opinion = fields.CharField(
        label='风控部意见', label_suffix="：",
        widget=widgets.Textarea(attrs={'class': 'form-control', 'rows': '1', 'placeholder': '风控部意见'}))
    convenor_opinion = fields.CharField(
        label='招集人意见', label_suffix="：",
        widget=widgets.Textarea(attrs={'class': 'form-control', 'rows': '1', 'placeholder': '招集人意见'}))
    sign_detail = fields.CharField(
        label='签批人意见', label_suffix="：",
        widget=widgets.Textarea(attrs={'class': 'form-control', 'rows': '2', 'placeholder': '签批详情'}))
    sign_date = fields.DateField(
        label='签批日期', label_suffix="：", initial=str(datetime.date.today()),
        widget=widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}))


# -----------------------反担保类型form-------------------------#
class LendingSuresForm(dform.ModelForm):
    class Meta:
        model = models.LendingSures
        fields = ['sure_typ']
        widgets = {'sure_typ': dform.Select(attrs={'class': 'form-control'})}


# -----------------------企业保证担保form-------------------------#
class LendingCustomsCForm(dform.Form):
    sure_c = fields.TypedMultipleChoiceField(
        label="反担保企业", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(LendingCustomsCForm, self).__init__(*args, **kwargs)
        self.fields['sure_c'].choices = models.Customes.objects.filter(genre=1).values_list(
            'id', 'name').order_by('name')


# -----------------------个人保证担保form-------------------------#
class LendingCustomsPForm(dform.Form):
    sure_p = fields.TypedMultipleChoiceField(
        label="反担保个人", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control', 'placeholder': '保证人'}))

    def __init__(self, *args, **kwargs):
        super(LendingCustomsPForm, self).__init__(*args, **kwargs)
        self.fields['sure_p'].choices = models.Customes.objects.filter(genre=2).values_list(
            'id', 'name').order_by('name')


# -----------------------房产担保form-------------------------#
class LendingHouseForm(dform.Form):
    sure_house = fields.TypedMultipleChoiceField(
        label="房产", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))
    '''  WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''

    def __init__(self, *args, **kwargs):
        super(LendingHouseForm, self).__init__(*args, **kwargs)
        self.fields['sure_house'].choices = models.Warrants.objects.filter(warrant_typ__in=[1, 2]).values_list(
            'id', 'warrant_num').order_by('warrant_num')


# -----------------------土地担保form-------------------------#
class LendingGroundForm(dform.Form):
    sure_ground = fields.TypedMultipleChoiceField(
        label="土地使用权", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))
    '''  WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''

    def __init__(self, *args, **kwargs):
        super(LendingGroundForm, self).__init__(*args, **kwargs)
        self.fields['sure_ground'].choices = models.Warrants.objects.filter(warrant_typ=5).values_list(
            'id', 'warrant_num').order_by('warrant_num')


# -----------------------在建工程担保form-------------------------#
class LendingConstructForm(dform.Form):
    sure_construct = fields.TypedMultipleChoiceField(
        label="在建工程", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))
    ''' WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''

    def __init__(self, *args, **kwargs):
        super(LendingConstructForm, self).__init__(*args, **kwargs)
        self.fields['sure_construct'].choices = models.Warrants.objects.filter(warrant_typ=6).values_list(
            'id', 'warrant_num').order_by('warrant_num')


# -----------------------应收账款质押form-------------------------#
class LendinReceivableForm(dform.Form):
    sure_receivable = fields.TypedMultipleChoiceField(
        label="应收账款", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))
    '''  WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''

    def __init__(self, *args, **kwargs):
        super(LendinReceivableForm, self).__init__(*args, **kwargs)
        self.fields['sure_receivable'].choices = models.Warrants.objects.filter(warrant_typ=11).values_list(
            'id', 'warrant_num').order_by('warrant_num')


# -----------------------股权质押form-------------------------#
class LendinStockForm(dform.Form):
    sure_stock = fields.TypedMultipleChoiceField(
        label="股权", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))
    '''  WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''

    def __init__(self, *args, **kwargs):
        super(LendinStockForm, self).__init__(*args, **kwargs)
        self.fields['sure_stock'].choices = models.Warrants.objects.filter(warrant_typ=21).values_list(
            'id', 'warrant_num').order_by('warrant_num')


# -----------------------票据质押form-------------------------#
class LendinDraftForm(dform.Form):
    sure_draft = fields.TypedMultipleChoiceField(
        label="票据", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(LendinDraftForm, self).__init__(*args, **kwargs)
        '''  WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        self.fields['sure_draft'].choices = models.Warrants.objects.filter(warrant_typ=31).values_list(
            'id', 'warrant_num').order_by('warrant_num')


# -----------------------车辆质押form-------------------------#
class LendinVehicleForm(dform.Form):
    sure_vehicle = fields.TypedMultipleChoiceField(
        label="车辆", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(LendinVehicleForm, self).__init__(*args, **kwargs)
        '''  WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        self.fields['sure_vehicle'].choices = models.Warrants.objects.filter(warrant_typ=41).values_list(
            'id', 'warrant_num').order_by('warrant_num')


# -----------------------动产抵押form-------------------------#
class LendinChattelForm(dform.Form):
    sure_chattel = fields.TypedMultipleChoiceField(
        label="动产", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(LendinChattelForm, self).__init__(*args, **kwargs)
        '''  WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        self.fields['sure_chattel'].choices = models.Warrants.objects.filter(warrant_typ=51).values_list(
            'id', 'warrant_num').order_by('warrant_num')


# -----------------------其他反担保物form-------------------------#
class LendinOtherForm(dform.Form):
    sure_other = fields.TypedMultipleChoiceField(
        label="其他资产", label_suffix="：", coerce=lambda x: int(x),
        widget=widgets.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(LendinOtherForm, self).__init__(*args, **kwargs)
        ''' WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        self.fields['sure_other'].choices = models.Warrants.objects.filter(warrant_typ=55).values_list(
            'id', 'warrant_num').order_by('warrant_num')
