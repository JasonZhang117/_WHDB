from django import forms as dform
from django.forms import fields
from django.forms import widgets
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------客户添加-------------------------#
class CustomAddForm(dform.ModelForm):
    class Meta:
        model = models.Customes
        fields = [
            'name',
            'short_name',
            'contact_addr',
            'linkman',
            'contact_num',
            'genre',
            'idustry',
            'district',
        ]
        widgets = {
            'name':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '客户名称'
            }),
            'short_name':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '客户简称'
            }),
            'genre':
            dform.Select(attrs={'class': 'form-control'}),
            'contact_addr':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '联系地址'
            }),
            'linkman':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '联系人'
            }),
            'contact_num':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '联系电话'
            }),
            'idustry':
            dform.Select(attrs={'class': 'form-control'}),
            'district':
            dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------客户编辑-------------------------#
class CustomEditForm(dform.ModelForm):
    name = fields.CharField(label="客户名称",
                            label_suffix="：",
                            max_length=32,
                            widget=widgets.TextInput(attrs={
                                'class': 'form-control',
                                'placeholder': '客户名称'
                            }))
    short_name = fields.CharField(
        label="客户简称",
        label_suffix="：",
        max_length=32,
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '客户简称'
        }))

    class Meta:
        model = models.Customes
        fields = [
            'contact_addr',
            'linkman',
            'contact_num',
            'idustry',
            'district',
        ]
        widgets = {
            'contact_addr':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '联系地址'
            }),
            'linkman':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '联系人'
            }),
            'contact_num':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '联系电话'
            }),
            'idustry':
            dform.Select(attrs={'class': 'form-control'}),
            'district':
            dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------客户状态编辑-------------------------#
class CustomChangeForm(dform.ModelForm):
    class Meta:
        model = models.Customes
        fields = [
            'custom_typ', 'credit_amount', 'custom_state', 'managementor'
        ]
        widgets = {
            'custom_typ':
            dform.Select(attrs={'class': 'form-control'}),
            'credit_amount':
            dform.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '授信总额'
            }),
            'custom_state':
            dform.Select(attrs={'class': 'form-control'}),
            'managementor':
            dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------变更客户风控专员-------------------------#
class CustomControlerForm(dform.ModelForm):
    class Meta:
        model = models.Customes
        fields = ['controler']
        widgets = {
            'controler': dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------企业客户添加-------------------------#
class CustomCAddForm(dform.ModelForm):  # 企业客户
    class Meta:
        model = models.CustomesC
        fields = [
            'credit_code', 'custom_nature', 'typing', 'industry_c', 'capital',
            'decisionor', 'registered_addr', 'representative'
        ]
        widgets = {
            'credit_code':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '统一社会信用代码'
            }),
            'custom_nature':
            dform.Select(attrs={'class': 'form-control'}),
            'typing':
            dform.Select(attrs={'class': 'form-control'}),
            'industry_c':
            dform.Select(attrs={'class': 'form-control'}),
            'capital':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '注册资本'
            }),
            'registered_addr':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '注册地址'
            }),
            'representative':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '法人代表'
            }),
            'decisionor':
            dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------客户附加信息-------------------------#
class CustomSubsidiaryForm(dform.ModelForm):  # 客户附加信息
    class Meta:
        model = models.Customes
        fields = [
            'data_date', 'sales_revenue', 'total_assets', 'people_engaged'
        ]
        widgets = {
            'data_date':
            dform.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'sales_revenue':
            dform.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '销售收入(万)'
            }),
            'total_assets':
            dform.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '资产总额(万)'
            }),
            'people_engaged':
            dform.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '从业人数(人)'
            }),
        }


# -----------------------股权信息添加-------------------------#
class FormShareholderAdd(dform.ModelForm):  # 股权信息添加
    class Meta:
        model = models.Shareholders
        fields = ['shareholder_name', 'invested_amount', 'shareholding_ratio']
        widgets = {
            'shareholder_name':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '股东名称'
            }),
            'invested_amount':
            dform.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '投资额'
            }),
            'shareholding_ratio':
            dform.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '持股比例（%）'
            })
        }


# -----------------------董事信息添加-------------------------#
class FormTrusteeAdd(dform.ModelForm):  # 股权信息添加
    class Meta:
        model = models.Trustee
        fields = [
            'trustee_name',
        ]
        widgets = {
            'trustee_name':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '董事姓名'
            }),
        }


# -----------------------个人客户添加-------------------------#
class CustomPAddForm(dform.ModelForm):  # 个人客户添加
    license_num = fields.CharField(
        label="身份证号",
        label_suffix="：",
        max_length=18,
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '身份证号'
        }))

    class Meta:
        model = models.CustomesP
        fields = ['household_nature', 'license_addr', 'marital_status']
        widgets = {
            'household_nature':
            dform.Select(attrs={'class': 'form-control'}),
            'license_addr':
            dform.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '身份证地址'
            }),
            'marital_status':
            dform.Select(attrs={'class': 'form-control'}),
        }


# -----------------------配偶添加-------------------------#
class FormCustomSpouseAdd(dform.Form):  # 项目添加
    spouses = fields.ChoiceField(
        label="配偶",
        label_suffix="：",
        widget=widgets.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(FormCustomSpouseAdd, self).__init__(*args, **kwargs)
        '''GENRE_LIST = ((1, '企业'), (2, '个人'))'''
        self.fields['spouses'].choices = models.Customes.objects.filter(
            genre=2).values_list('id', 'name').order_by('name')
