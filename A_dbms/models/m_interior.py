from django.db import models


# -----------------------------部门模型------------------------------#
class Departments(models.Model):  # 部门
    name = models.CharField(verbose_name='部门名称', max_length=16, unique=True)

    class Meta:
        verbose_name_plural = '内部-部门'  # 指定显示名称
        db_table = 'dbms_departments'  # 指定数据表的名称

    def __str__(self):
        return self.name
