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


# -----------------------项目意见添加-------------------------#
class FormOpinion(dform.ModelForm):  # 风控反馈添加
    class Meta:
        model = models.Articles
        fields = ['article_repay_method', 'opinion', ]
        widgets = {
            'article_repay_method': dform.Select(attrs={'class': 'form-control'}),
            'opinion': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '项目经理意见'}), }


# -----------------------项目变更-------------------------#
class ArticleChangeForm(dform.ModelForm):  # 项目变更
    class Meta:
        model = models.ArticleChange
        fields = ['change_view', 'change_date', 'change_detail']
        widgets = {'change_view': dform.Select(attrs={'class': 'form-control'}),
                   'change_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                   'change_detail': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '变更情况'})}


# -----------------------项目状态变更-------------------------#
class ArticleStateChangeForm(dform.ModelForm):  # 项目变更
    class Meta:
        model = models.Articles
        fields = ['article_state', ]
        widgets = {'article_state': dform.Select(attrs={'class': 'form-control'}), }


# -----------------------委托合同添加-------------------------#
class ArticleAgreeAddForm(dform.ModelForm):
    branch = fields.ChoiceField(
        label="放款银行", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Agrees
        fields = ['agree_typ', 'guarantee_typ', 'agree_copies', 'agree_amount', 'amount_limit',
                  'agree_rate', 'investigation_fee', 'agree_term', 'agree_term_typ', 'other']
        widgets = {
            'agree_typ': dform.Select(attrs={'class': 'form-control'}),
            'guarantee_typ': dform.Select(attrs={'class': 'form-control'}),
            'agree_copies': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同份数'}),
            'agree_term': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '期限'}),
            'agree_term_typ': dform.Select(attrs={'class': 'form-control'}),
            'agree_rate': dform.Textarea(attrs={'class': 'form-control', 'rows': '2', 'placeholder': '如为单项合同输入纯数字,担保费率单位：百分之，小贷费率单位：千分之/每月'}),
            'investigation_fee': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '调查费率(%)'}),
            'agree_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同金额（元）'}),
            'amount_limit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '放款限额（元）'}),
            'other': dform.Textarea(attrs={'class': 'form-control', 'rows': '1', 'placeholder': '其他合同约定事项'}),
        }

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


# -----------------------小贷借款合同补充资料-------------------------#
class AgreeJkAddForm(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['agree_start_date', 'agree_due_date', 'acc_name', 'acc_num', 'acc_bank',
                  'repay_method', 'repay_ex']
        widgets = {
            'agree_start_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'agree_due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acc_name': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '户名'}),
            'acc_num': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '账号'}),
            'acc_bank': dform.TextInput(attrs={'class': 'form-control', 'placeholder': '开户行名称'}),
            'repay_method': dform.Select(attrs={'class': 'form-control', 'placeholder': '还本付息方式'}),
            'repay_ex': dform.Textarea(attrs={'class': 'form-control', 'rows': '1', 'placeholder': '还本付息描述'}),
        }


# -----------------------共借人添加-------------------------#
class FormBorrowerAdd(dform.Form):  # 共借人添加
    borrower = fields.ChoiceField(
        label="共借人", label_suffix="：", widget=widgets.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(FormBorrowerAdd, self).__init__(*args, **kwargs)
        '''GENRE_LIST = ((1, '企业'), (2, '个人'))'''
        self.fields['borrower'].choices = models.Customes.objects.values_list(
            'id', 'name').order_by('name')
