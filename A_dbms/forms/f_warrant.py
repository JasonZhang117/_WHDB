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
                   'house_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '楼盘名称等'})}


# -----------------------房产包modelform2-------------------------#
class HouseBagAddEidtForm(dform.ModelForm):
    housebag_locate = fields.CharField(
        label="房产坐落", label_suffix="：", max_length=64,
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '房产坐落'}))

    class Meta:
        model = models.HouseBag
        fields = ['housebag_app', 'housebag_area']
        widgets = {'housebag_app': dform.Select(attrs={'class': 'form-control'}),
                   'housebag_area': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '面积（平方米'})}


# -----------------------土地modelform5-------------------------#
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


# -----------------------在建工程modelform6-------------------------#
class ConstructionAddForm(dform.ModelForm):
    coustruct_locate = fields.CharField(
        label="工程地址", label_suffix="：", max_length=64,
        widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '工程地址'}))

    class Meta:
        model = models.Construction
        fields = ['coustruct_app', 'coustruct_area']
        widgets = {'coustruct_app': dform.Select(attrs={'class': 'form-control'}),
                   'coustruct_area': dform.NumberInput(attrs={'class': 'form-control'})}


# ------------------------应收帐款FormReceivable11--------------------------#
class FormReceivable(dform.ModelForm):  # 应收帐款
    receive_owner = fields.IntegerField(
        label='所有权人', label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Receivable
        fields = ['receivable_detail']
        widgets = {'receivable_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3'})}

    def __init__(self, *args, **kwargs):
        super(FormReceivable, self).__init__(*args, **kwargs)
        self.fields['receive_owner'].widget.choices = models.Customes.objects.values_list('id', 'name').order_by('name')


# ------------------------应收帐款FormReceivableEdit--------------------------#
class FormReceivableEdit(dform.ModelForm):  #
    class Meta:
        model = models.Receivable
        fields = ['receivable_detail']
        widgets = {'receivable_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3'})}


# ------------------------应收帐款FormReceivExtend11--------------------------#
class FormReceivExtend(dform.ModelForm):  #
    class Meta:
        model = models.ReceiveExtend
        fields = ['receive_unit', ]
        widgets = {'receive_unit': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '付款单位'}), }


# ------------------------股权FormStockes21--------------------------#
class FormStockes(dform.ModelForm):  # 股权
    stock_owner = fields.IntegerField(
        label='所有权人', label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Stockes
        fields = ['target', 'ratio', 'registe', 'share', 'stock_typ', 'remark']
        widgets = {'target': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '目标企业'}),
                   'ratio': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '占比'}),
                   'registe': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '万元或万股'}),
                   'share': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '万元或万股'}),
                   'stock_typ': dform.Select(attrs={'class': 'form-control'}),
                   'remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'}), }

    def __init__(self, *args, **kwargs):
        super(FormStockes, self).__init__(*args, **kwargs)
        self.fields['stock_owner'].widget.choices = models.Customes.objects.values_list('id', 'name').order_by('name')


# ------------------------股权FormStockesEdit--------------------------#
class FormStockesEdit(dform.ModelForm):  #
    class Meta:
        model = models.Stockes
        fields = ['target', 'ratio', 'registe', 'share', 'stock_typ', 'remark']
        widgets = {'target': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '目标企业'}),
                   'ratio': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '占比'}),
                   'registe': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '万元或万股'}),
                   'share': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '万元或万股'}),
                   'stock_typ': dform.Select(attrs={'class': 'form-control'}),
                   'remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'}), }


# ------------------------票据31--------------------------#
class FormDraft(dform.ModelForm):  # 票据31
    draft_owner = fields.IntegerField(
        label='所有权人', label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Draft
        fields = ['draft_detail', 'denomination', 'typ']
        widgets = {'draft_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
                   'typ': dform.Select(attrs={'class': 'form-control'}),
                   'denomination': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '票面总额'}), }

    def __init__(self, *args, **kwargs):
        super(FormDraft, self).__init__(*args, **kwargs)
        self.fields['draft_owner'].widget.choices = models.Customes.objects.values_list('id', 'name').order_by('name')


# ------------------------票据31--------------------------#
class FormDraftEdit(dform.ModelForm):  # 票据31
    class Meta:
        model = models.Draft
        fields = ['draft_detail', 'denomination', 'typ']
        widgets = {'draft_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
                   'typ': dform.Select(attrs={'class': 'form-control'}),
                   'denomination': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '票面总额'}), }


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


# ------------------------票据状态修改--------------------------#
class FormDraftStorage(dform.ModelForm):  # 票据状态修改
    class Meta:
        model = models.DraftExtend
        fields = ['draft_state', ]
        widgets = {'draft_state': dform.Select(attrs={'class': 'form-control'}),
                   }


# ------------------------车辆FormVehicle41--------------------------#
class FormVehicle(dform.ModelForm):  # 车辆FormVehicle41
    vehicle_owner = fields.IntegerField(
        label='所有权人', label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Vehicle
        fields = ['frame_num', 'plate_num', 'vehicle_brand', 'vehicle_remark']
        widgets = {'frame_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '车架号'}),
                   'plate_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '车牌号'}),
                   'vehicle_brand': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '品牌型号'}),
                   'vehicle_remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'}), }

    def __init__(self, *args, **kwargs):
        super(FormVehicle, self).__init__(*args, **kwargs)
        self.fields['vehicle_owner'].widget.choices = models.Customes.objects.values_list('id', 'name').order_by('name')


# ------------------------车辆FormVehicleEdit41--------------------------#
class FormVehicleEdit(dform.ModelForm):  # 车辆FormVehicle41
    frame_num = fields.CharField(
        label='车架号', label_suffix="：",
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '车架号'}))
    plate_num = fields.CharField(
        label='车牌号', label_suffix="：",
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '车牌号'}))

    class Meta:
        model = models.Vehicle
        fields = ['vehicle_brand', 'vehicle_remark']
        widgets = {'vehicle_brand': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '品牌型号'}),
                   'vehicle_remark': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '备注'}), }


# ------------------------动产FormChattel51--------------------------#
class FormChattel(dform.ModelForm):  # 动产FormChattel51
    chattel_owner = fields.IntegerField(
        label='所有权人', label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Chattel
        fields = ['chattel_typ', 'chattel_detail']
        widgets = {'chattel_typ': dform.Select(attrs={'class': 'form-control'}),
                   'chattel_detail': dform.Textarea(
                       attrs={'class': 'form-control', 'rows': '3', 'placeholder': '详细情况'})}

    def __init__(self, *args, **kwargs):
        super(FormChattel, self).__init__(*args, **kwargs)
        self.fields['chattel_owner'].widget.choices = models.Customes.objects.values_list('id', 'name').order_by('name')


# ------------------------动产FormChattelEdit51--------------------------#
class FormChattelEdit(dform.ModelForm):  # 动产FormChattel51

    class Meta:
        model = models.Chattel
        fields = ['chattel_typ', 'chattel_detail']
        widgets = {'chattel_typ': dform.Select(attrs={'class': 'form-control'}),
                   'chattel_detail': dform.Textarea(
                       attrs={'class': 'form-control', 'rows': '3', 'placeholder': '详细情况'})}


# ------------------------其他FormOthers55--------------------------#
class FormOthers(dform.ModelForm):  #
    other_owner = fields.IntegerField(
        label='所有权人', label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Others
        fields = ['other_typ', 'other_detail', 'cost']
        widgets = {'other_typ': dform.Select(attrs={'class': 'form-control'}),
                   'cost': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '价值'}),
                   'other_detail': dform.Textarea(
                       attrs={'class': 'form-control', 'rows': '3', 'placeholder': '详细情况'})}

    def __init__(self, *args, **kwargs):
        super(FormOthers, self).__init__(*args, **kwargs)
        self.fields['other_owner'].widget.choices = models.Customes.objects.values_list('id', 'name').order_by('name')


# ------------------------其他FormOthers55--------------------------#
class FormOthers41(dform.ModelForm):  #

    class Meta:
        model = models.Patent
        fields = ['patent_name', 'reg_num', 'patent_ty']
        widgets = {'patent_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '商标名称'}),
                   'reg_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '申请/注册号'}),
                   'patent_ty': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '国际分类'}), }


# ------------------------其他FormOthers55--------------------------#
class FormOthers41Edit(dform.ModelForm):  #
    reg_num = fields.CharField(
        label='申请/注册号', label_suffix="：", widget=widgets.TextInput(
            attrs={'class': 'form-control', 'placeholder': '申请/注册号'}))
    class Meta:
        model = models.Patent
        fields = ['patent_name', 'patent_ty']
        widgets = {'patent_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '商标名称'}),
                   'patent_ty': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '国际分类'}), }


# ------------------------其他FormOthersEdit55--------------------------#
class FormOthersEdit(dform.ModelForm):  #

    class Meta:
        model = models.Others
        fields = ['other_detail', 'cost']
        widgets = {'cost': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '价值'}),
                   'other_detail': dform.Textarea(
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
