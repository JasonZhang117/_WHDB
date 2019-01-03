from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------权证添加-------------------------#
class WarrantAddForm(dform.ModelForm):
    class Meta:
        model = models.Warrants
        fields = ['warrant_num', 'warrant_typ']
        widgets = {
            'warrant_num': dform.TextInput(
                attrs={'class': 'form-control', 'placeholder': '权证编码'})}


# -----------------------权证编辑-------------------------#
class WarrantEditForm(dform.Form):
    warrant_num = fields.CharField(
        label='权证编码', label_suffix="：",
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '权证编码'}))


# ------------------OwerShipEditForm产权证编辑-------------------#
class OwerShipAddForm(dform.ModelForm):  # OwerShipEditForm产权证编辑
    ownership_num = fields.CharField(
        label="产权证编号", label_suffix="：", max_length=32,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '产权证编号'}))

    class Meta:
        model = models.Ownership
        fields = ['owner']


# -----------------------房产modelform1-------------------------#
class HouseAddEidtForm(dform.ModelForm):
    house_locate = fields.CharField(
        label="房产坐落", label_suffix="：", max_length=64,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '房产坐落'}))

    class Meta:
        model = models.Houses
        fields = ['house_app', 'house_area']


# -----------------------土地modelform2-------------------------#
class GroundAddEidtForm(dform.ModelForm):
    ground_locate = fields.CharField(
        label="土地坐落", label_suffix="：", max_length=64,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '土地坐落'}))

    class Meta:
        model = models.Grounds
        fields = ['ground_app', 'ground_area']


# ------------------------应收帐款FormReceivable11--------------------------#
class FormReceivable(dform.ModelForm):  # 应收帐款
    class Meta:
        model = models.Receivable
        fields = ['receive_owner', 'receivable_detail']


# ------------------------股权FormStockes21--------------------------#
class FormStockes(dform.ModelForm):  # 股权
    class Meta:
        model = models.Stockes
        fields = ['stock_owner', 'target', 'share', 'stock_typ']

# ------------------------票据31--------------------------#
class FormDraft(dform.ModelForm):  # 股权
    class Meta:
        model = models.Draft
        fields = ['draft_owner', 'draft_typ', 'draft_detail']


# ------------------------车辆FormVehicle41--------------------------#
class FormVehicle(dform.ModelForm):  # 股权
    class Meta:
        model = models.Vehicle
        fields = ['vehicle_owner', 'frame_num', 'plate_num']


# ------------------------动产FormChattel51--------------------------#
class FormChattel(dform.ModelForm):  # 股权
    class Meta:
        model = models.Chattel
        fields = ['chattel_owner', 'chattel_typ', 'chattel_detail']


# -----------------------HypothecsAddEidtForm他权-------------------------#
class HypothecsAddEidtForm(dform.ModelForm):
    class Meta:
        model = models.Hypothecs
        fields = ['agree']


# -----------------------StoragesAddEidtForm出入库-------------------------#
class StoragesAddEidtForm(dform.ModelForm):
    class Meta:
        model = models.Storages
        fields = ['storage_typ', 'storage_date', 'transfer']

    widgets = {
        'storage_date': widgets.DateInput(
            attrs={'class': 'form-control', 'type': 'date',
                   'placeholder': '权证编码'})}
