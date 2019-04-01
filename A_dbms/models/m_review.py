from django.db import models
import datetime


class Review(models.Model):
    custom = models.ForeignKey(to='Customes', verbose_name="客户",
                               on_delete=models.PROTECT,
                               related_name='review_custom')
    review_plan_date = models.DateField(verbose_name='保后计划', blank=True, null=True)
    REVIEW_STATE_LIST = [(1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后')]
    review_state = models.IntegerField(verbose_name='_保后状态', choices=REVIEW_STATE_LIST, default=1)
    REVIEW_STY_LIST = [(1, '现场检查'), (11, '电话回访')]
    review_sty = models.IntegerField(verbose_name='保后方式', choices=REVIEW_STY_LIST, blank=True, null=True)
    analysis = models.TextField(verbose_name='风险分析', blank=True, null=True)
    suggestion = models.TextField(verbose_name='风控建议', blank=True, null=True)
    CLASSIFICATION_LIST = [(1, '正常'), (11, '关注'), (21, '次级'), (31, '可疑'), (41, '损失')]
    classification = models.IntegerField(verbose_name='风险分类', choices=CLASSIFICATION_LIST, blank=True, null=True)
    review_date = models.DateField(verbose_name='保后日期', blank=True, null=True)
    reviewor = models.ForeignKey(to='Employees', verbose_name="保后人员",
                                 on_delete=models.PROTECT,
                                 related_name='reviewor_employee')

    class Meta:
        verbose_name_plural = '项目-保后检查'  # 指定显示名称
        db_table = 'dbms_review'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.custom, self.review_date)
