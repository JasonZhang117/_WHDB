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
    time_limit = models.IntegerField(verbose_name='期限（月）')
    weighting = models.FloatField(verbose_name='加权金额')
    notify_provide_sum = models.FloatField(verbose_name='_放款金额', default=0)
    notify_repayment_sum = models.FloatField(verbose_name='_还款金额', default=0)
    notify_balance = models.FloatField(verbose_name='_在保余额', default=0)

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
    PROVIDE_TYP_LIST = [(1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'),
                        (41, '过桥贷'), (52, '房抵贷'), (53, '担保贷')]
    provide_typ = models.IntegerField(verbose_name='放款种类', choices=PROVIDE_TYP_LIST)
    old_amount = models.FloatField(verbose_name='续贷金额', default=0)
    new_amount = models.FloatField(verbose_name='新增金额', default=0)
    provide_money = models.FloatField(verbose_name='放款金额', default=0)
    provide_date = models.DateField(verbose_name='放款日期')
    due_date = models.DateField(verbose_name='到期日')

    IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), (41, '已归档'), (99, '无需归档')]
    implement = models.IntegerField(verbose_name='_归档状态', choices=IMPLEMENT_LIST, default=1)
    file_num = models.CharField(verbose_name='档案编号', max_length=64, unique=True, null=True, blank=True)

    PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]
    provide_status = models.IntegerField(verbose_name='_放款状态', choices=PROVIDE_STATUS_LIST, default=1)
    provide_repayment_sum = models.FloatField(verbose_name='_还款总额', default=0)
    provide_balance = models.FloatField(verbose_name='_在保余额', default=0)
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
                                    on_delete=models.PROTECT,
                                    related_name='repaymentor_employee')
    repaymentdate = models.DateField(verbose_name='_创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目-还款'  # 指定显示名称
        db_table = 'dbms_repayments'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.provide, self.repayment_money)


# ------------------------归档模型--------------------------#
class Pigeonholes(models.Model):  # 归档
    provide = models.ForeignKey(to='Provides', verbose_name="放款",
                                on_delete=models.PROTECT,
                                related_name='pigeonhole_provide')
    IMPLEMENT_LIST = Provides.IMPLEMENT_LIST
    implement = models.IntegerField(verbose_name='归档状态', choices=IMPLEMENT_LIST, default=1)
    pigeonhole_date = models.DateField(verbose_name='归档日期', default=datetime.date.today)
    pigeonhole_explain = models.CharField(verbose_name='归档说明', max_length=128, null=True, blank=True)
    pigeonhole_transfer = models.ForeignKey(to='Employees', verbose_name="移交人",
                                            on_delete=models.PROTECT,
                                            limit_choices_to={'employee_status': 1},
                                            related_name='pigeonhole_transfer_employee')
    pigeonholor = models.ForeignKey(to='Employees', verbose_name="_创建者",
                                    on_delete=models.PROTECT,
                                    related_name='pigeonholor_employee')

    class Meta:
        verbose_name_plural = '放款-归档'  # 指定显示名称
        db_table = 'dbms_pigeonholes'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s' % (self.provide, self.pigeonhole_date, self.pigeonhole_transfer.name)


# ------------------------持续跟踪模型--------------------------#
class Track(models.Model):  #
    provide = models.ForeignKey(to='Provides', verbose_name="放款",
                                on_delete=models.PROTECT,
                                limit_choices_to={'provide_status': 1},
                                related_name='track_provide')
    TRACK_TYP_LIST = [(11, '日常跟踪'), (21, '分期还款'), (25, '分期付息'), (31, '提前还款'), ]
    track_typ = models.IntegerField(verbose_name='跟踪类型', choices=TRACK_TYP_LIST, default=11)
    plan_date = models.DateField(verbose_name='计划日期')
    proceed = models.CharField(verbose_name='跟踪内容', max_length=128)
    track_date = models.DateField(verbose_name='跟踪日期', null=True, blank=True)
    condition = models.TextField(verbose_name='跟踪情况', null=True, blank=True)
    TRACK_STATE_LIST = [(11, '待跟踪'), (21, '已跟踪'), ]
    track_state = models.IntegerField(verbose_name='_跟踪状态', choices=TRACK_STATE_LIST, default=11)
    trackor = models.ForeignKey(to='Employees', verbose_name="_创建者",
                                on_delete=models.PROTECT,
                                related_name='trackor_employee')
    trackordate = models.DateField(verbose_name='_创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '放款-跟踪'  # 指定显示名称
        db_table = 'dbms_track'  # 指定数据表的名称
        ordering = ['plan_date', ]

    def __str__(self):
        return '%s_%s' % (self.provide, self.track_date)
