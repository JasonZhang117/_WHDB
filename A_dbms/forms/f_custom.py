from django import forms as dform
from django.forms import fields
from django.forms import widgets
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------客户添加-------------------------#
class CustomAddForm(dform.ModelForm):
    class Meta:
        model = models.Customes
        fields = ['name', 'short_name', 'contact_addr', 'linkman', 'contact_num', 'genre', 'custom_state']
        widgets = {
            'name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '客户名称'}),
            'short_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '客户简称'}),
            'genre': dform.Select(attrs={'class': 'form-control'}),
            'contact_addr': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '联系地址'}),
            'linkman': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '联系人'}),
            'contact_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '联系电话'}),
            'custom_state': dform.Select(attrs={'class': 'form-control'}), }


# -----------------------客户编辑-------------------------#
class CustomEditForm(dform.ModelForm):
    name = fields.CharField(
        label="客户名称", label_suffix="：", max_length=32,
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '客户名称'}))
    short_name = fields.CharField(
        label="客户简称", label_suffix="：", max_length=32,
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '客户简称'}))

    class Meta:
        model = models.Customes
        fields = ['counter_only', 'contact_addr', 'linkman', 'contact_num', 'custom_state']
        widgets = {
            'contact_addr': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '联系地址'}),
            'linkman': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '联系人'}),
            'contact_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '联系电话'}),
            'custom_state': dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------企业客户添加-------------------------#
class CustomCAddForm(dform.ModelForm):  # 企业客户

    class Meta:
        model = models.CustomesC
        fields = ['district', 'capital', 'idustry', 'decisionor', 'registered_addr', 'representative']
        widgets = {
            'capital': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '注册资本'}),
            'registered_addr': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '注册地址'}),
            'representative': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '法人代表'}),
            'idustry': dform.Select(attrs={'class': 'form-control'}),
            'district': dform.Select(attrs={'class': 'form-control'}),
            'decisionor': dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------股权信息添加-------------------------#
class FormShareholderAdd(dform.ModelForm):  # 股权信息添加
    class Meta:
        model = models.Shareholders
        fields = ['shareholder_name', 'invested_amount', 'shareholding_ratio']
        widgets = {
            'shareholder_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '股东名称'}),
            'invested_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '投资额'}),
            'shareholding_ratio': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '持股比例（%）'})}


# -----------------------董事信息添加-------------------------#
class FormTrusteeAdd(dform.ModelForm):  # 股权信息添加
    class Meta:
        model = models.Trustee
        fields = ['trustee_name', ]
        widgets = {
            'trustee_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '董事姓名'}), }


# -----------------------个人客户添加-------------------------#
class CustomPAddForm(dform.ModelForm):  # 个人客户添加
    license_num = fields.CharField(
        label="身份证号", label_suffix="：", max_length=18,
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '身份证号'}))

    class Meta:
        model = models.CustomesP
        fields = ['license_addr', 'marital_status']
        widgets = {
            'license_addr': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '身份证地址'}),
            'marital_status': dform.Select(attrs={'class': 'form-control'}), }


# -----------------------配偶添加-------------------------#
class FormCustomSpouseAdd(dform.Form):  # 项目添加
    spouses = fields.ChoiceField(
        label="配偶", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(FormCustomSpouseAdd, self).__init__(*args, **kwargs)
        '''GENRE_LIST = ((1, '企业'), (2, '个人'))'''
        self.fields['spouses'].choices = models.Customes.objects.filter(genre=2).values_list(
            'id', 'name').order_by('name')
