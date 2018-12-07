from django.db import models


# -----------------------代偿模型-------------------------#
class Compensatories(models.Model):  # 代偿
    provide = models.OneToOneField(
        to='Provides',
        verbose_name="放款",
        on_delete=models.PROTECT,
        related_name='compensatory_provide')
    compensatory_date = models.DateField(
        verbose_name='代偿日期',
        default='2018-09-09')
    compensatory_capital = models.FloatField(
        verbose_name='代偿本金',
        default=0)
    compensatory_interest = models.FloatField(
        verbose_name='代偿利息',
        default=0)
    retrieve_amount = models.FloatField(
        verbose_name='追偿总额', default=0)
    SELECT_LIST = ((1, '起诉'), (2, '判决'),
                   (3, '执行'), (4, '和解结案'),
                   (5, '终止执行'))
    compensatory_implement = models.IntegerField(
        verbose_name='归档状态',
        choices=SELECT_LIST,
        default=1)

    class Meta:
        verbose_name_plural = '项目-代偿'  # 指定显示名称
        db_table = 'dbms_compensatories'  # 指定数据表的名称

    def __str__(self):
        return self.provide.agree.agree_num
