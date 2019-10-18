from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------项目添加-------------------------#
class ArticlesAddForm(dform.Form):  # 项目添加
    custom_id = fields.IntegerField(
        label='客户名称', label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))
    product_id = fields.IntegerField(
        label='业务品种', label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))
    renewal = fields.FloatField(
        label='续贷金额（元）', label_suffix="：",
        widget=widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': '输入续贷金额'}))
    augment = fields.FloatField(
        label='新增金额（元）', label_suffix="：",
        widget=widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': '输入新增金额'}))
    credit_term = fields.IntegerField(
        label='授信期限（月）', label_suffix="：", initial=12,
        widget=widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': '输入授信期限（月）'}))
    process_id = fields.IntegerField(
        label="审批流程", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))
    director_id = fields.IntegerField(
        label="项目经理", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))
    assistant_id = fields.IntegerField(
        label="项目助理", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))
    control_id = fields.IntegerField(
        label="风控专员", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(ArticlesAddForm, self).__init__(*args, **kwargs)
        self.fields['custom_id'].widget.choices = models.Customes.objects.values_list('id', 'name')
        self.fields['product_id'].widget.choices = models.Product.objects.values_list('id', 'name')
        self.fields['process_id'].widget.choices = models.Process.objects.values_list('id', 'name')
        self.fields['director_id'].widget.choices = models.Employees.objects.filter(
            job__name='项目经理', employee_status=1).values_list('id', 'name')
        self.fields['assistant_id'].widget.choices = models.Employees.objects.filter(
            job__name='项目经理', employee_status=1).values_list('id', 'name')
        self.fields['control_id'].widget.choices = models.Employees.objects.filter(
            job__name='风控专员', employee_status=1).values_list('id', 'name')


# -----------------------项目提交-------------------------#
class ArticleSubForm(dform.ModelForm):  # 项目提交
    class Meta:
        model = models.ProcessArticle
        fields = ['conclusion', 'detail', ]
        widgets = {'conclusion': dform.Select(attrs={'class': 'form-control'}),
                   'detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '审批意见'})}


# -----------------------风控反馈添加-------------------------#
class FeedbackAddForm(dform.Form):  # 风控反馈添加
    PROPOSE_LIST = models.Feedback.PROPOSE_LIST
    propose = fields.IntegerField(
        label='上会建议', label_suffix="：",
        widget=widgets.Select(choices=PROPOSE_LIST, attrs={'class': 'form-control'}))
    analysis = fields.CharField(
        label='风险分析', label_suffix="：", widget=widgets.Textarea(
            attrs={'class': 'form-control', 'rows': '7',
                   'placeholder': '分析项目主要风险(行业风险、流动性风险、经营风险、法律风险等)'}))
    suggestion = fields.CharField(
        label='风控建议', label_suffix="：", widget=widgets.Textarea(
            attrs={'class': 'form-control', 'rows': '5',
                   'placeholder': '提出项目风控措施建议（额度、担保措施、过程控制、保后要求等）'}))


# -----------------------项目变更-------------------------#
class ArticleChangeForm(dform.ModelForm):  # 项目变更
    class Meta:
        model = models.ArticleChange
        fields = ['change_view', 'change_date', 'change_detail']
        widgets = {'change_view': dform.Select(attrs={'class': 'form-control'}),
                   'change_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                   'change_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '变更情况'})}


# -----------------------委托合同添加-------------------------#
class ArticleAgreeAddForm(dform.ModelForm):
    branch = fields.ChoiceField(
        label="放款银行", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Agrees
        fields = ['agree_typ', 'guarantee_typ', 'agree_copies', 'agree_amount', 'amount_limit',
                  'agree_rate', 'agree_term']
        widgets = {
            'agree_typ': dform.Select(attrs={'class': 'form-control'}),
            'guarantee_typ': dform.Select(attrs={'class': 'form-control'}),
            'agree_copies': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同份数'}),
            'agree_term': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '期限'}),
            'agree_rate': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '如为单项合同输入纯数字'}),
            'agree_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同金额（元）'}),
            'amount_limit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '放款限额（元）'})}

    def __init__(self, *args, **kwargs):
        super(ArticleAgreeAddForm, self).__init__(*args, **kwargs)
        self.fields['branch'].choices = models.Branches.objects.filter(branch_state=1).values_list('id', 'name')


# -----------------------委托出具保函合同-------------------------#
class LetterGuaranteeAddForm(dform.ModelForm):
    class Meta:
        model = models.LetterGuarantee
        fields = ['letter_typ', 'beneficiary', 'basic_contract', 'basic_contract_num', 'starting_date',
                  'due_date']
        widgets = {
            'letter_typ': dform.Select(attrs={'class': 'form-control'}),
            'beneficiary': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '受益人'}),
            'basic_contract': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '基础合同名称'}),
            'basic_contract_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '基础合同编号'}),
            'starting_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}), }
