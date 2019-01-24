from django.contrib import admin
from A_dbms import models
from .usera import EmployeesAdmin


# -----------------------项目-------------------------#
class ArticlesAdmin(admin.ModelAdmin):
    list_display = ('article_num', 'custom', 'amount', 'director', 'article_state')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    search_fields = ['article_num']  # 搜索字段
    ordering = ['-build_date']  # 排序字段


admin.site.register(models.Articles, ArticlesAdmin)  # 项目
admin.site.register(models.Feedback)  # 风控反馈
admin.site.register(models.ArticleChange)  # 项目变更
admin.site.register(models.Appraisals)  # 评审会
admin.site.register(models.SingleQuota)  # 单项额度
admin.site.register(models.Comments)  # 评审意见
admin.site.register(models.LendingOrder)  # 发放次序
admin.site.register(models.LendingSures)  # 反担保
admin.site.register(models.LendingCustoms)  # 保证反担保
admin.site.register(models.LendingWarrants)  # 抵质押反担保


# -----------------------合同-------------------------#
class AgreesAdmin(admin.ModelAdmin):
    list_display = ('agree_num', 'agree_typ', 'agree_amount', 'agree_sign_date', 'ascertain_date', 'agree_date')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    search_fields = ['agree_num']  # 搜索字段
    ordering = ['-agree_date']  # 排序字段


admin.site.register(models.Agrees, AgreesAdmin)  # 合同
admin.site.register(models.AgreeesExtend)  # 合同扩展
admin.site.register(models.Counters)  # 反担保合同
admin.site.register(models.CountersAssure)  # 保证反担保合同
admin.site.register(models.CountersWarrants)  # 抵质押押反担保合同


# ------------------------担保物--------------------------#
class WarrantsAdmin(admin.ModelAdmin):
    list_display = ('warrant_num', 'warrant_typ', 'evaluate_state', 'evaluate_value', 'evaluate_date', 'warrant_state')
    list_per_page = 20  # 每页显示条目数
    search_fields = ['warrant_num']  # 搜索字段
    ordering = ['warrant_num']  # 排序字段


admin.site.register(models.Warrants, WarrantsAdmin)  # 担保物
admin.site.register(models.Ownership)  # 产权证
admin.site.register(models.Hypothecs)  # 他权
admin.site.register(models.Houses)  # 房产
admin.site.register(models.HouseBag)  # 房产包
admin.site.register(models.Grounds)  # 土地
admin.site.register(models.Stockes)  # 股权
admin.site.register(models.Receivable)  # 应收账款
admin.site.register(models.Evaluate)  # 出入库
admin.site.register(models.Storages)  # 评估
# -----------------------放款-------------------------#
admin.site.register(models.Charges)  # 收费
admin.site.register(models.Provides)  # 放款
admin.site.register(models.Notify)  # 放款通知
admin.site.register(models.Repayments)  # 还款
admin.site.register(models.Pigeonholes)  # 归档
# -----------------------追偿-------------------------#
admin.site.register(models.Compensatories)  # 代偿


# -----------------------客户-------------------------#
class CustomesAdmin(admin.ModelAdmin):
    list_display = ('name', 'genre', 'contact_addr', 'linkman', 'contact_num', 'credit_amount',
                    'custom_flow', 'custom_accept', 'custom_back')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    search_fields = ['name']  # 搜索字段
    ordering = ['-credit_amount', 'name']  # 排序字段


admin.site.register(models.Customes, CustomesAdmin)  # 客户
admin.site.register(models.CustomesC)  # 企业客户
admin.site.register(models.CustomesP)  # 个人客户
admin.site.register(models.Districtes)  # 区域
admin.site.register(models.Industries)  # 行业
admin.site.register(models.Shareholders)  # 股东
# -----------------------保后-------------------------#
admin.site.register(models.Review)  # 行业


# -----------------------外部信息-------------------------#
class CooperatorsAdmin(admin.ModelAdmin):
    list_display = ('name', 'cooperator_state', 'credit_date', 'due_date', 'flow_credit', 'flow_limit',
                    'back_credit', 'back_limit')  # 显示字段
    list_per_page = 30  # 每页显示条目数
    search_fields = ['name']  # 搜索字段
    ordering = ['-flow_credit', '-flow_limit']  # 排序字段


admin.site.register(models.Cooperators, CooperatorsAdmin)  # 合作机构


class BranchesAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch_flow', 'branch_accept', 'branch_back')  # 显示字段
    list_per_page = 30  # 每页显示条目数
    search_fields = ['name']  # 搜索字段
    ordering = ['-branch_flow', '-branch_accept']  # 排序字段


admin.site.register(models.Branches, BranchesAdmin)  # 放款银行


class ExpertsAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'job', 'level', 'contact_numb', 'email', 'ordery', 'expert_state',)  # 显示字段
    list_per_page = 30  # 每页显示条目数
    search_fields = ['name']  # 搜索字段
    ordering = ['name']  # 排序字段


admin.site.register(models.Experts, ExpertsAdmin)  # 评审专家


# -----------------------员工-------------------------#
# 部门
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ('name',)  # 显示字段
    list_per_page = 30  # 每页显示条目数
    search_fields = ['name']  # 搜索字段
    ordering = ['name']  # 排序字段


admin.site.register(models.Departments, DepartmentsAdmin)


# 岗位
class JobsAdmin(admin.ModelAdmin):
    list_display = ('name',)  # 显示字段
    list_per_page = 30  # 每页显示条目数
    filter_horizontal = ("menu",)


admin.site.register(models.Jobs, JobsAdmin)
# 员工
admin.site.register(models.Employees, EmployeesAdmin)


#
# -----------------------员工-------------------------#
# 部门
class MenusAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_name', 'ordery')  # 显示字段
    list_per_page = 30  # 每页显示条目数
    search_fields = ['name']  # 搜索字段
    ordering = ['ordery', ]  # 排序字段


admin.site.register(models.Menus, MenusAdmin)
