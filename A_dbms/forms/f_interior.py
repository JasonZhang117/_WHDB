from django import forms as dform
from django.forms import fields
from django.forms import widgets
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------部门form-------------------------#
class DepartmentForm(dform.Form):  # 部门form
    name = fields.CharField(label='部门名称',
                            label_suffix="：",
                            required=False,  # 是否必填
                            initial='风控部')


# -----------------------岗位form-------------------------#
class JobForm(dform.Form):  # 岗位form
    name = fields.CharField(label='岗位名称',
                            label_suffix="：",
                            required=False,  # 是否必填
                            initial='项目经理')


# -----------------------员工form-------------------------#
class EmployeeForm(dform.Form):  # 员工form
    EMPLOYEE_STATUS_LIST = [('在职', '在职'), ('离职', '离职')]
    employee_num = fields.CharField(
        label='用户名',
        label_suffix="：",
        required=True,
        # 记录上一次输入数
        show_hidden_initial=True,
        # 覆盖默认错误提示
        error_messages={'required': '不能为空'},
        disabled=False,  # 是否允许编辑
        # 可自定义HTML属性
        widget=widgets.TextInput(attrs={'class': 'ci'}),
        max_length=16,
        min_length=3)
    name = fields.CharField(label='员工姓名',
                            label_suffix="：",
                            max_length=16)
    id_code = fields.CharField(label='身份证号',
                               label_suffix="：",
                               max_length=18)
    department_id = fields.IntegerField(
        label='所属部门',
        label_suffix="：",
        widget=widgets.Select())
    job = fields.TypedMultipleChoiceField(
        label='岗位',
        label_suffix="：",
        coerce=lambda x: int(x),
        widget=widgets.SelectMultiple())
    age = fields.IntegerField(label='年龄',
                              label_suffix="：",
                              max_value=100,
                              min_value=12)
    e_mail = fields.EmailField(label='电子邮箱',
                               label_suffix="：",
                               max_length=64)
    password = fields.CharField(
        label='密码',
        label_suffix="：",
        max_length=16,
        widget=widgets.PasswordInput())
    employee_status = fields.IntegerField(
        label='状态',
        label_suffix="：",
        widget=widgets.Select(choices=EMPLOYEE_STATUS_LIST))

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['department'].widget.choices = \
            models.Departments.objects.values_list(
                'id', 'name').order_by('name')
        self.fields['job'].choices = \
            models.Jobs.objects.values_list(
                'id', 'name').order_by('name')
    # def clean_license_num(self):
    #     v = self.cleaned_data['license_num']
    #     if models.Customes.objects.filter(license_num=v).count():
    #         raise ValidationError('用户名已存在')
    #     return v
    # def clean(self):
    #     value_dice = self.cleaned_data
    #     v1 = value_dice.get('license_num')
    #     v2 = value_dice.get('name')
    #     if v1 and v2:
    #         raise ValidationError('整体错误信息')
    #     return self.cleaned_data
