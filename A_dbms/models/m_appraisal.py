from django.db import models
import datetime


# ------------------------评审会模型--------------------------#
class Appraisals(models.Model):  # 评审会
    num = models.CharField(
        verbose_name='审保会编号',
        max_length=32,
        unique=True)
    REVIEW_MODEL_LIST = ((1, '内审'), (2, '外审'))
    review_model = models.IntegerField(
        verbose_name='评审类型',
        choices=REVIEW_MODEL_LIST)
    review_order = models.IntegerField(
        verbose_name='评审次序')
    review_date = models.DateField(
        verbose_name='评审日期',
        default=datetime.date.today)
    expert = models.ManyToManyField(
        to='Experts',
        verbose_name="评审",
        related_name='appraisal_expert')
    article = models.ManyToManyField(
        to='Articles',
        verbose_name="项目",
        related_name='appraisal_article')

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '评审-审保会'  # 指定显示名称
        db_table = 'dbms_appraisals'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s" % (self.review_model,
                          self.review_order)
