from django.db import models
import datetime


# ------------------------收费模型--------------------------#
class Charges(models.Model):  # 收费
    agree = models.ForeignKey(to='Agrees', verbose_name="委托合同",
                              on_delete=models.PROTECT,
                              related_name='charge_agree')
    amount = models.FloatField(verbose_name='收费金额')
    balance = models.FloatField(verbose_name='应收余额')
    charge_buildor = models.ForeignKey(to='Employees', verbose_name="创建者",
                                       on_delete=models.PROTECT, default=1,
                                       related_name='charge_buildor_employee')
    charge_date = models.DateField(verbose_name='收费日期', default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '放款-收费'  # 指定显示名称
        db_table = 'dbms_charges'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s" % (self.agree, self.amount)


# ------------------------Notify放款通知--------------------------#
class Notify(models.Model):  # Notify放款通知
    agree = models.ForeignKey(to='Agrees', verbose_name="委托保证合同",
                              on_delete=models.PROTECT,
                              related_name='notify_agree')
    notify_money = models.FloatField(verbose_name='通知金额')
    notify_date = models.DateField(verbose_name='日期', default=datetime.date.today)
    contracts_lease = models.CharField(verbose_name='借款合同编号', max_length=32, null=True, blank=True)
    contract_guaranty = models.CharField(verbose_name='保证合同编号', max_length=32, null=True, blank=True)
    remark = models.CharField(verbose_name='备注', max_length=256, null=True, blank=True)

    notify_provide_sum = models.FloatField(verbose_name='_放款金额', default=0)
    notify_repayment_sum = models.FloatField(verbose_name='_还款金额', default=0)

    notifyor = models.ForeignKey(to='Employees', verbose_name="_创建者",
                                 on_delete=models.PROTECT, default=1,
                                 related_name='notifyor_employee')

    class Meta:
        verbose_name_plural = '放款-放款通知'  # 指定显示名称
        db_table = 'dbms_notify'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s' % (self.agree.agree_num, self.notify_date, self.notify_money)


# ------------------------放款模型--------------------------#
class Provides(models.Model):  # 放款
    notify = models.ForeignKey(to='Notify', verbose_name="_放款通知",
                               on_delete=models.PROTECT,
                               related_name='provide_notify')
    PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'))
    provide_typ = models.IntegerField(verbose_name='放款种类', choices=PROVIDE_TYP_LIST)
    provide_money = models.FloatField(verbose_name='放款金额')
    provide_date = models.DateField(verbose_name='放款日期')
    due_date = models.DateField(verbose_name='到期日')

    IMPLEMENT_LIST = [(1, '未归档'), (11, '暂存风控'), (21, '已归档')]
    implement = models.IntegerField(verbose_name='_归档状态', choices=IMPLEMENT_LIST, default=1)
    file_num = models.CharField(verbose_name='档案编号', max_length=64, unique=True, null=True, blank=True)
    pigeonhole_date = models.DateField(verbose_name='归档日期', null=True, blank=True)

    PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]
    provide_status = models.IntegerField(verbose_name='_放款状态', choices=PROVIDE_STATUS_LIST, default=1)
    provide_repayment_sum = models.FloatField(verbose_name='_还款总额', default=0)
    providor = models.ForeignKey(to='Employees', verbose_name="_创建者",
                                 on_delete=models.PROTECT,
                                 related_name='providor_employee')
    providordate = models.DateField(verbose_name='_创建日期', default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '放款'  # 指定显示名称
        db_table = 'dbms_provides'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.notify, self.provide_money)


# ------------------------还款模型--------------------------#
class Repayments(models.Model):  # 还款
    provide = models.ForeignKey(to='Provides', verbose_name="放款",
                                on_delete=models.PROTECT,
                                limit_choices_to={'provide_status': 1},
                                related_name='repayment_provide')
    repayment_money = models.FloatField(verbose_name='还款金额')
    repayment_date = models.DateField(verbose_name='还款日期', default=datetime.date.today)
    repaymentor = models.ForeignKey(to='Employees', verbose_name="_创建者",
                                    on_delete=models.PROTECT, default=1,
                                    related_name='repaymentor_employee')
    repaymentdate = models.DateField(verbose_name='_创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目-还款'  # 指定显示名称
        db_table = 'dbms_repayments'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.provide, self.repayment_money)


# ------------------------归档模型--------------------------#
class Pigeonholes(models.Model):  # 归档
    provide = models.OneToOneField(to='Provides', verbose_name="放款",
                                   on_delete=models.PROTECT,
                                   related_name='pigeonhole_provide')
    pigeonholor = models.ForeignKey(to='Employees', verbose_name="_创建者",
                                    on_delete=models.PROTECT, default=1,
                                    related_name='pigeonholor_employee')
    pigeonhole_date = models.DateField(verbose_name='归档日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '放款-归档'  # 指定显示名称
        db_table = 'dbms_pigeonholes'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.provide, self.pigeonhole_date)
