from django.db import models
import datetime


# ------------------------收费模型--------------------------#
class Charges(models.Model):  # 收费
    agree = models.ForeignKey(to='Agrees',
                              verbose_name="委托合同",
                              on_delete=models.PROTECT,
                              related_name='charge_agree')
    amount = models.FloatField(verbose_name='收费金额')
    charge_date = models.DateField(
        verbose_name='收费日期', default=datetime.date.today)
    balance = models.FloatField(verbose_name='应收余额')

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '放款-收费'  # 指定显示名称
        db_table = 'dbms_charges'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s" % (self.agree, self.amount)


# ------------------------Notify放款通知--------------------------#
class Notify(models.Model):  # Notify放款通知
    agree = models.ForeignKey(to='Agrees',
                              verbose_name="委托保证合同",
                              on_delete=models.PROTECT,
                              related_name='notify_agree')
    notify_money = models.FloatField(verbose_name='通知金额')

    class Meta:
        verbose_name_plural = '项目-放款通知'  # 指定显示名称
        db_table = 'dbms_notify'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.agree, self.notify_money)


# ------------------------放款模型--------------------------#
class Provides(models.Model):  # 放款
    notify = models.ForeignKey(to='Notify',
                               verbose_name="放款通知",
                               on_delete=models.PROTECT,
                               related_name='provide_notify')
    SELECT_LIST = ((1, '流贷'), (2, '承兑'), (3, '保函'))
    provide_typ = models.IntegerField(
        verbose_name='放款种类', choices=SELECT_LIST, default=1)
    provide_money = models.FloatField(verbose_name='放款金额')
    provide_date = models.DateField(
        verbose_name='放款日期', default=datetime.date.today)
    due_date = models.DateField(
        verbose_name='到期日', default=datetime.date.today)
    provide_balance = models.FloatField(verbose_name='余额')
    IMPLEMENT_LIST = ((1, '未归档'), (2, '暂存风控'), (3, '已归档'))
    implement = models.IntegerField(
        verbose_name='归档状态', choices=IMPLEMENT_LIST, default=1)
    STATUS_LIST = ((1, '在保'), (2, '解保'), (3, '代偿'))
    provide_status = models.IntegerField(
        verbose_name='放款状态', choices=STATUS_LIST, default=1)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '项目-放款'  # 指定显示名称
        db_table = 'dbms_provides'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.notify.agree, self.provide_money)


# ------------------------还款模型--------------------------#
class Repayments(models.Model):  # 还款
    provide = models.ForeignKey(to='Provides',
                                verbose_name="放款",
                                on_delete=models.PROTECT,
                                related_name='repayment_provide')
    repayment_money = models.FloatField(verbose_name='还款金额')
    repayment_date = models.DateField(
        verbose_name='还款日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目-还款'  # 指定显示名称
        db_table = 'dbms_repayments'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.provide, self.repayment_money)


# ------------------------归档模型--------------------------#
class Pigeonholes(models.Model):  # 归档
    provide = models.OneToOneField(to='Provides',
                                   verbose_name="放款",
                                   on_delete=models.PROTECT,
                                   related_name='pigeonhole_provide')
    pigeonhole_date = models.DateField(
        verbose_name='归档日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目-归档'  # 指定显示名称
        db_table = 'dbms_pigeonholes'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.provide, self.pigeonhole_date)
