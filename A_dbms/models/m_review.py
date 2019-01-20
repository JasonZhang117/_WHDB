from django.db import models
import datetime


class Review(models.Model):
    custom = models.ForeignKey(to='Customes', verbose_name="客户",
                               on_delete=models.PROTECT,
                               related_name='review_custom')
    REVIEW_STY_LIST = [(1, '现场检查'), (11, '电话回访')]
    review_sty = models.IntegerField(verbose_name='保后方式', choices=REVIEW_STY_LIST, default=1)
    analysis = models.TextField(verbose_name='风险分析')
    suggestion = models.TextField(verbose_name='建议')
    control_option = models.TextField(verbose_name='风控意见')
    review_date = models.DateField(verbose_name='提交日期', default=datetime.date.today)
    reviewor = models.ForeignKey(to='Employees', verbose_name="保后人员",
                                 on_delete=models.PROTECT,
                                 related_name='reviewor_employee')

    class Meta:
        verbose_name_plural = '项目-保后检查'  # 指定显示名称
        db_table = 'dbms_review'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.custom, self.review_date)
