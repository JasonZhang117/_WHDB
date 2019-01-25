from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------权证添加-------------------------#
class WarrantAddForm(dform.ModelForm):
    class Meta:
        model = models.Warrants
        fields = ['warrant_num', 'warrant_typ']
        widgets = {
            'warrant_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '权证编码'}),
            'warrant_typ': dform.Select(attrs={'class': 'form-control'})}


# -----------------------权证编辑-------------------------#
class WarrantEditForm(dform.Form):
    warrant_num = fields.CharField(
        label='权证编码', label_suffix="：",
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '权证编码'}))


# ------------------OwerShipEditForm产权证编辑-------------------#
class OwerShipAddForm(dform.ModelForm):  # OwerShipEditForm产权证编辑
    ownership_num = fields.CharField(
        label="产权证编号", label_suffix="：", max_length=32,
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '产权证编号'}))

    class Meta:
        model = models.Ownership
        fields = ['owner']
        widgets = {'owner': dform.Select(attrs={'class': 'form-control'})}


# -----------------------房产modelform1-------------------------#
class HouseAddEidtForm(dform.ModelForm):
    house_locate = fields.CharField(
        label="房产坐落", label_suffix="：", max_length=64,
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '房产坐落'}))

    class Meta:
        model = models.Houses
        fields = ['house_app', 'house_area', 'house_name']
        widgets = {'house_app': dform.Select(attrs={'class': 'form-control'}),
                   'house_area': dform.NumberInput(attrs={'class': 'form-control'}),
                   'house_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '楼盘名称'})}


# -----------------------房产包modelform1-------------------------#
class HouseBagAddEidtForm(dform.ModelForm):
    housebag_locate = fields.CharField(
        label="房产坐落", label_suffix="：", max_length=64,
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '房产坐落'}))

    class Meta:
        model = models.HouseBag
        fields = ['housebag_app', 'housebag_area']
        widgets = {'housebag_app': dform.Select(attrs={'class': 'form-control'}),
                   'housebag_area': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '面积（平方米'})}


# -----------------------土地modelform2-------------------------#
class GroundAddEidtForm(dform.ModelForm):
    ground_locate = fields.CharField(
        label="土地坐落", label_suffix="：", max_length=64,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '土地坐落'}))

    class Meta:
        model = models.Grounds
        fields = ['ground_app', 'ground_area']
        widgets = {'ground_app': dform.Select(attrs={'class': 'form-control'}),
                   'ground_area': dform.NumberInput(attrs={'class': 'form-control'})}


# ------------------------应收帐款FormReceivable11--------------------------#
class FormReceivable(dform.ModelForm):  # 应收帐款
    class Meta:
        model = models.Receivable
        fields = ['receive_owner', 'receivable_detail']
        widgets = {'receive_owner': dform.Select(attrs={'class': 'form-control'}),
                   'receivable_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3'})}


# ------------------------股权FormStockes21--------------------------#
class FormStockes(dform.ModelForm):  # 股权
    class Meta:
        model = models.Stockes
        fields = ['stock_owner', 'target', 'share', 'stock_typ']
        widgets = {'stock_owner': dform.Select(attrs={'class': 'form-control'}),
                   'target': dform.TextInput(attrs={'class': 'form-control'}),
                   'share': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '土地坐落'}),
                   'stock_typ': dform.Select(attrs={'class': 'form-control'})}


# ------------------------票据31--------------------------#
class FormDraft(dform.ModelForm):  # 票据31
    class Meta:
        model = models.Draft
        fields = ['draft_owner', 'draft_detail']
        widgets = {'draft_owner': dform.Select(attrs={'class': 'form-control'}),
                   'draft_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3'})}


# ------------------------票据包31--------------------------#
class FormDraftExtend(dform.ModelForm):  # 票据31
    class Meta:
        model = models.DraftExtend
        fields = ['draft_typ', 'draft_num', 'draft_acceptor', 'draft_amount', 'issue_date', 'due_date']
        widgets = {'draft_typ': dform.Select(attrs={'class': 'form-control'}),
                   'draft_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '票据号码'}),
                   'draft_acceptor': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '承兑人'}),
                   'draft_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '票面金额'}),
                   'issue_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': '出票日'}),
                   'due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': '到期日'})
                   }


# ------------------------车辆FormVehicle41--------------------------#
class FormVehicle(dform.ModelForm):  # 车辆FormVehicle41
    class Meta:
        model = models.Vehicle
        fields = ['vehicle_owner', 'frame_num', 'plate_num']
        widgets = {'vehicle_owner': dform.Select(attrs={'class': 'form-control'}),
                   'frame_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '车架号'}),
                   'plate_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '车牌号'})}


# ------------------------动产FormChattel51--------------------------#
class FormChattel(dform.ModelForm):  # 动产FormChattel51
    class Meta:
        model = models.Chattel
        fields = ['chattel_owner', 'chattel_typ', 'chattel_detail']
        widgets = {'chattel_owner': dform.Select(attrs={'class': 'form-control'}),
                   'chattel_typ': dform.Select(attrs={'class': 'form-control'}),
                   'chattel_detail': dform.Textarea(
                       attrs={'class': 'form-control', 'rows': '3', 'placeholder': '详细情况'})}


# -----------------------HypothecsAddEidtForm他权-------------------------#
class HypothecsAddEidtForm(dform.ModelForm):
    class Meta:
        model = models.Hypothecs
        fields = ['agree']
        widgets = {'agree': dform.Select(attrs={'class': 'form-control'})}


# -----------------------StoragesAddEidtForm出入库-------------------------#
class StoragesAddEidtForm(dform.ModelForm):
    class Meta:
        model = models.Storages
        fields = ['storage_typ', 'storage_date', 'transfer', 'storage_explain']

        widgets = {'storage_typ': dform.Select(attrs={'class': 'form-control'}),
                   'storage_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                   'transfer': dform.Select(attrs={'class': 'form-control'}),
                   'storage_explain': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '出入库说明'})}


# -----------------------EvaluateAddEidtForm评估-------------------------#
class EvaluateAddEidtForm(dform.ModelForm):
    class Meta:
        model = models.Evaluate
        fields = ['evaluate_state', 'evaluate_value', 'evaluate_date', 'evaluate_explain']

        widgets = {'evaluate_state': dform.Select(attrs={'class': 'form-control'}),
                   'evaluate_value': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '评估价值（元）'}),
                   'evaluate_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                   'evaluate_explain': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '评估说明'})}
