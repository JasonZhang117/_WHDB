import datetime
from django.db import models


class Process(models.Model):  # 审批流程
    name = models.CharField(verbose_name='流程名称',
                            max_length=32,
                            unique=True)
    TYP_LIST = [(1, '签批 '), (11, '内审'),  (21, '外审'), ]
    typ = models.IntegerField(verbose_name='流程类型', choices=TYP_LIST, default=1)
    creator = models.ForeignKey(to='Employees', verbose_name="创建人",
                                on_delete=models.PROTECT,
                                related_name='process_creator_employee')
    create_date = models.DateField(verbose_name='创建日期',
                                   default=datetime.date.today)

    class Meta:
        verbose_name_plural = '审批流程'  # 指定显示名称
        db_table = 'dbms_process'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s" % (self.name, self.typ)


class ProcessSet(models.Model):  # 流程配置
    process = models.ForeignKey(to='Process', verbose_name="流程名称",
                                on_delete=models.PROTECT,
                                related_name='process_set_process')
    approver = models.ForeignKey(to='Jobs', verbose_name="审批人",
                                 on_delete=models.PROTECT,
                                 related_name='approver_jobs')
    STEP_LIST = [(1, '创建 '), (11, '发起'), (21, '复核'), (31, '评审'),
                 (41, '审核'), (61, '审批'), ]
    step = models.IntegerField(verbose_name='审批步骤', choices=STEP_LIST, default=1)
    creator = models.ForeignKey(to='Employees', verbose_name="创建人",
                                on_delete=models.PROTECT,
                                related_name='process_set_creator_employee')
    create_date = models.DateField(verbose_name='创建日期',
                                   default=datetime.date.today)

    class Meta:
        verbose_name_plural = '审批流程-配置'  # 指定显示名称
        db_table = 'dbms_processset'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s-%s" % (self.process, self.approver, self.step)


class ProcessArticle(models.Model):  # 项目审批列表
    article = models.ForeignKey(to='Articles', verbose_name="项目",
                                on_delete=models.PROTECT,
                                related_name='process_article')
    process_set = models.ForeignKey(to='ProcessSet', verbose_name="流程步骤",
                                    on_delete=models.PROTECT,
                                    related_name='process_article_process_set')
    CONCLUSION_LIST = [(1, '同意'), (11, '不同意'), ]
    conclusion = models.IntegerField(verbose_name='结论', choices=CONCLUSION_LIST, default=1)
    detail = models.TextField(verbose_name='意见', blank=True, null=True)
    employee = models.ForeignKey(to='Employees', verbose_name="审批人",
                                 on_delete=models.PROTECT,
                                 related_name='process_article_employee')
    creator = models.ForeignKey(to='Employees', verbose_name="创建人",
                                on_delete=models.PROTECT,
                                related_name='process_article_creator_employee')
    create_date = models.DateField(verbose_name='创建日期',
                                   default=datetime.date.today)

    class Meta:
        verbose_name_plural = '审批流程-项目审批'  # 指定显示名称
        db_table = 'dbms_processarticle'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s-%s" % (self.article, self.process_set, self.employee)
