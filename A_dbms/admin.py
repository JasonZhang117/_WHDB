from django.contrib import admin
from A_dbms import models
from .usera import EmployeesAdmin

# -----------------------项目-------------------------#
admin.site.register(models.Articles)  # 项目
# -----------------------合同-------------------------#
admin.site.register(models.Agrees)  # 合同
admin.site.register(models.Counters)  # 反担保合同
admin.site.register(models.CountersAssure)  # 保证反担保合同
admin.site.register(models.CountersHouse)  # 房产抵押反担保合同
# ------------------------担保物--------------------------#
admin.site.register(models.Warrants)  # 担保物
admin.site.register(models.Ownership)  # 产权证
admin.site.register(models.Hypothecs)  # 他权
admin.site.register(models.Houses)  # 房产
admin.site.register(models.Grounds)  # 土地
admin.site.register(models.Evaluate)  # 出入库
admin.site.register(models.Storages)  # 评估
# -----------------------放款-------------------------#
admin.site.register(models.Provides)  # 放款
admin.site.register(models.Repayments)  # 还款
admin.site.register(models.Pigeonholes)  # 归档
# -----------------------追偿-------------------------#
admin.site.register(models.Compensatories)  # 代偿

# -----------------------客户-------------------------#
admin.site.register(models.Customes)  # 客户
admin.site.register(models.CustomesC)  # 企业客户
admin.site.register(models.CustomesP)  # 个人客户
admin.site.register(models.Districtes)  # 区域
admin.site.register(models.Industries)  # 行业

# -----------------------外部信息-------------------------#
admin.site.register(models.Cooperators)  # 授信机构
admin.site.register(models.Branches)  # 放款银行
admin.site.register(models.Experts)  # 评审专家


# -----------------------员工-------------------------#
# 部门
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ('name',)  # 显示字段
    list_per_page = 30  # 每页显示条目数
    search_fields = ['name']  # 搜索字段
    ordering = ['name']  # 排序字段


admin.site.register(models.Departments, DepartmentsAdmin)
# 岗位
admin.site.register(models.Jobs)
# 员工
admin.site.register(models.Employees, EmployeesAdmin)
