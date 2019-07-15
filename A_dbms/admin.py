from django.contrib import admin
from A_dbms import models
from .usera import EmployeesAdmin


# -----------------------项目-------------------------#
class ArticlesAdmin(admin.ModelAdmin):
    list_display = (
        'article_num', 'summary_num', 'custom', 'amount', 'article_provide_sum', 'director', 'article_state',
        'build_date',
        'article_date', 'article_balance', 'article_state')  # 显示字段
    # list_per_page = 20  # 每页显示条目数
    search_fields = ['article_num', 'summary_num']  # 搜索字段
    ordering = ['-build_date']  # 排序字段


admin.site.register(models.Articles, ArticlesAdmin)  # 项目


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('article', 'feedback_date')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    # search_fields = ['article_num']  # 搜索字段
    ordering = ['-feedback_date']  # 排序字段


admin.site.register(models.Feedback, FeedbackAdmin)  # 风控反馈
admin.site.register(models.ArticleChange)  # 项目变更


class AppraisalsAdmin(admin.ModelAdmin):
    list_display = ('num', 'review_year', 'review_model', 'review_date')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    # search_fields = ['article_num']  # 搜索字段
    # ordering = ['num']  # 排序字段


admin.site.register(models.Appraisals, AppraisalsAdmin)  # 评审会


class SingleQuotaAdmin(admin.ModelAdmin):
    list_display = ('summary', 'credit_model', 'credit_amount', 'flow_rate')  # 显示字段
    list_per_page = 200  # 每页显示条目数
    # search_fields = ['article_num']  # 搜索字段
    # ordering = ['num']  # 排序字段


admin.site.register(models.SingleQuota, SingleQuotaAdmin)  # 单项额度
admin.site.register(models.Supply)  # 单项额度
admin.site.register(models.Comments)  # 评审意见
class LendingOrderAdmin(admin.ModelAdmin):
    list_display = ('summary', 'order', 'order_amount', 'lending_state', 'lending_provide_sum',
                    'lending_repayment_sum', 'lending_balance')  # 显示字段
    list_per_page = 200  # 每页显示条目数
    # search_fields = ['article_num']  # 搜索字段
    # ordering = ['num']  # 排序字段
admin.site.register(models.LendingOrder,LendingOrderAdmin)  # 发放次序


class LendingSuresAdmin(admin.ModelAdmin):
    list_display = ('lending', 'sure_typ',)  # 显示字段
    # list_per_page = 20  # 每页显示条目数
    # search_fields = ['lending']  # 搜索字段
    # ordering = ['num']  # 排序字段


admin.site.register(models.LendingSures, LendingSuresAdmin)  # 反担保
admin.site.register(models.LendingCustoms)  # 保证反担保
admin.site.register(models.LendingWarrants)  # 抵质押反担保


# -----------------------合同-------------------------#
class AgreesAdmin(admin.ModelAdmin):
    list_display = (
        'agree_num', 'agree_name', 'agree_typ', 'agree_amount', 'agree_term', 'agree_sign_date', 'agree_rate',
        'agree_date', 'agree_notify_sum', 'agree_provide_sum', 'agree_repayment_sum', 'agree_balance',
        'agree_state')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    search_fields = ['agree_num']  # 搜索字段
    ordering = ['-agree_date']  # 排序字段


admin.site.register(models.Agrees, AgreesAdmin)  # 合同


class AgreesResultState(admin.ModelAdmin):
    list_display = (
        'agree', 'custom', 'result_typ')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    search_fields = ['agree']  # 搜索字段
    ordering = ['-agree']  # 排序字段


admin.site.register(models.ResultState, AgreesResultState)  # 合同


class CountersAdmin(admin.ModelAdmin):
    list_display = (
        'counter_num', 'counter_name', 'agree', 'counter_typ', 'counter_copies')  # 显示字段
    # list_per_page = 20  # 每页显示条目数
    search_fields = ['counter_num']  # 搜索字段
    # ordering = ['-agree_date']  # 排序字段


admin.site.register(models.Counters, CountersAdmin)  # 反担保合同
admin.site.register(models.CountersAssure)  # 保证反担保合同
admin.site.register(models.CountersWarrants)  # 抵质押押反担保合同


# ------------------------担保物--------------------------#
class WarrantsAdmin(admin.ModelAdmin):
    list_display = ('warrant_num', 'warrant_typ', 'meeting_date', 'evaluate_state', 'evaluate_value',
                    'evaluate_date', 'warrant_state')
    list_per_page = 200  # 每页显示条目数
    search_fields = ['warrant_num']  # 搜索字段
    ordering = ['warrant_num']  # 排序字段


admin.site.register(models.Warrants, WarrantsAdmin)  # 担保物


class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('ownership_num', 'warrant', 'owner')
    list_per_page = 200  # 每页显示条目数
    search_fields = ['ownership_num']  # 搜索字段
    ordering = ['ownership_num']  # 排序字段


admin.site.register(models.Ownership, OwnershipAdmin)  # 产权证

admin.site.register(models.Hypothecs)  # 他权
admin.site.register(models.Houses)  # 房产
admin.site.register(models.HouseBag)  # 房产包
admin.site.register(models.Grounds)  # 土地
admin.site.register(models.Construction)  # 在建工程
admin.site.register(models.Stockes)  # 股权
admin.site.register(models.Receivable)  # 应收账款
admin.site.register(models.ReceiveExtend)  # 应收账款
admin.site.register(models.Draft)  # 票据
admin.site.register(models.DraftExtend)  # 票据列表
admin.site.register(models.Chattel)  # 动产
admin.site.register(models.Others)  # 动产
admin.site.register(models.Evaluate)  # 出入库


class StoragesAdmin(admin.ModelAdmin):
    list_display = ('warrant', 'storage_typ', 'storage_explain', 'transfer', 'conservator', 'storage_date')
    # list_per_page = 20  # 每页显示条目数
    # search_fields = ['notify']  # 搜索字段
    ordering = ['-storage_date']  # 排序字段


admin.site.register(models.Storages, StoragesAdmin)  # 评估
# -----------------------放款-------------------------#
admin.site.register(models.Charges)  # 收费


class ProvidesAdmin(admin.ModelAdmin):
    list_display = ('notify', 'provide_typ', 'provide_money', 'provide_date', 'due_date', 'implement',
                    'provide_repayment_sum', 'provide_balance', 'provide_status')
    # list_per_page = 20  # 每页显示条目数
    # search_fields = ['notify']  # 搜索字段
    ordering = ['-provide_date']  # 排序字段


admin.site.register(models.Provides, ProvidesAdmin)  # 放款
admin.site.register(models.Track)  # 跟踪


class NotifyAdmin(admin.ModelAdmin):
    list_display = ('agree', 'notify_money', 'notify_date', 'time_limit', 'weighting',
                    'notify_provide_sum', 'notify_repayment_sum')  # 显示字段
    # list_per_page = 20  # 每页显示条目数
    # search_fields = ['name', 'short_name']  # 搜索字段
    # ordering = ['-credit_amount', 'name']  # 排序字段


admin.site.register(models.Notify, NotifyAdmin)  # 放款通知
admin.site.register(models.Repayments)  # 还款
admin.site.register(models.Pigeonholes)  # 归档


# -----------------------追偿-------------------------#
class CompensatoriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'compensatory_date', 'compensatory_capital', 'dun_state')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    search_fields = ['title']  # 搜索字段
    ordering = ['title']  # 排序字段


admin.site.register(models.Compensatories, CompensatoriesAdmin)  # 代偿
admin.site.register(models.Dun)  # 追偿
admin.site.register(models.Agent)  # 代理情况
admin.site.register(models.Staff)  # 人员模型
admin.site.register(models.Charge)  # 费用情况
admin.site.register(models.Retrieve)  # 回收情况


class StageAdmin(admin.ModelAdmin):
    list_display = (
    'dun', 'stage_remark', 'stage_type', 'stage_state', 'stage_file', 'stage_date', 'page_amout')  # 显示字段
    list_per_page = 200  # 每页显示条目数
    search_fields = ['stage_remark','stage_file']  # 搜索字段
    # ordering = ['title']  # 排序字段


admin.site.register(models.Stage, StageAdmin)  # 阶段情况
admin.site.register(models.Judgment)  # 判决
admin.site.register(models.Standing)  # 台账
admin.site.register(models.Seal)  # 财产线索
admin.site.register(models.Sealup)  # 查封情况
admin.site.register(models.Inquiry)  # 查询情况


# -----------------------客户-------------------------#
class CustomesAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'short_name', 'genre', 'custom_state', 'idustry', 'managementor', 'linkman', 'contact_num',
        'credit_amount',
        'custom_flow', 'custom_accept', 'custom_back', 'amount')  # 显示字段
    list_per_page = 20  # 每页显示条目数
    search_fields = ['name', 'short_name']  # 搜索字段
    ordering = ['-credit_amount', 'name']  # 排序字段


admin.site.register(models.Customes, CustomesAdmin)  # 客户


class CustomesCAdmin(admin.ModelAdmin):
    list_display = ('custome', 'idustry', 'district', 'capital', 'representative')  # 显示字段
    # list_per_page = 20  # 每页显示条目数
    # search_fields = ['name', 'short_name']  # 搜索字段
    ordering = ['idustry', 'district']  # 排序字段


admin.site.register(models.CustomesC, CustomesCAdmin)  # 企业客户


# -----------------------客户-------------------------#
class CustomesPAdmin(admin.ModelAdmin):
    list_display = ('custome', 'spouses', 'license_num', 'license_addr')  # 显示字段
    # list_per_page = 20  # 每页显示条目数
    search_fields = ['license_num', 'license_addr']  # 搜索字段
    ordering = ['id']  # 排序字段


admin.site.register(models.CustomesP, CustomesPAdmin)  # 个人客户
admin.site.register(models.Districtes)  # 区域


class IndustriesAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'cod_nam')  # 显示字段
    # list_per_page = 20  # 每页显示条目数
    search_fields = ['code', 'name']  # 搜索字段
    ordering = ['code']  # 排序字段


admin.site.register(models.Industries, IndustriesAdmin)  # 行业
admin.site.register(models.Shareholders)  # 股东
admin.site.register(models.Trustee)  # 董事

# -----------------------保后-------------------------#
admin.site.register(models.Review)  # 保后
admin.site.register(models.Investigate)  # 补调


# -----------------------外部信息-------------------------#
class CooperatorsAdmin(admin.ModelAdmin):
    list_display = ('name', 'cooperator_type', 'credit_date', 'due_date', 'flow_credit', 'flow_limit',
                    'back_credit', 'back_limit')  # 显示字段
    list_per_page = 30  # 每页显示条目数
    search_fields = ['name']  # 搜索字段
    # ordering = ['-flow_credit', '-flow_limit']  # 排序字段


admin.site.register(models.Cooperators, CooperatorsAdmin)  # 合作机构
admin.site.register(models.Agreements)  # 合作机构


class BranchesAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'branch_flow', 'branch_accept', 'branch_back')  # 显示字段
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
    filter_horizontal = ("authority",)


admin.site.register(models.Jobs, JobsAdmin)


class AuthoritiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'url_name', 'carte', 'ordery')  # 显示字段
    # list_per_page = 30  # 每页显示条目数
    search_fields = ['name', 'url_name']  # 搜索字段
    # filter_horizontal = ("menu", "authority")
    ordering = ['ordery', ]  # 排序字段


admin.site.register(models.Authorities, AuthoritiesAdmin)


class CartesAdmin(admin.ModelAdmin):
    list_display = ('caption', 'ordery', 'parent')  # 显示字段
    list_per_page = 30  # 每页显示条目数
    # filter_horizontal = ("menu", "authority")
    ordering = ['ordery', ]  # 排序字段


admin.site.register(models.Cartes, CartesAdmin)
# 员工
admin.site.register(models.Employees, EmployeesAdmin)
