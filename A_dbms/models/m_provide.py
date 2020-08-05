from django.db import models
import datetime
from _WHDB.views import (FICATION_LIST)


# ------------------------收费模型--------------------------#
class Charges(models.Model):  # 收费
    provide = models.ForeignKey(to='Provides',
                              verbose_name="放款",
                              on_delete=models.PROTECT,
                              related_name='provide_agree')
    CHARGE_TYP_LIST = (
        (11, '担保费/利息'),
        (21, '咨询费/服务费'),
        (41, '保证金'),
    )
    charge_typ = models.IntegerField(verbose_name='收费类型',
                                     choices=CHARGE_TYP_LIST,
                                     default=11)
    rate = models.FloatField(verbose_name='费率(%)', default=0)
    amount = models.FloatField(verbose_name='收费金额（元）')
    charge_buildor = models.ForeignKey(to='Employees',
                                       verbose_name="创建者",
                                       on_delete=models.PROTECT,
                                       default=1,
                                       related_name='charge_buildor_employee')
    charge_date = models.DateField(verbose_name='收费日期',
                                   default=datetime.date.today)

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
    notify_date = models.DateField(verbose_name='日期',
                                   default=datetime.date.today)
    contracts_lease = models.CharField(verbose_name='借款合同编号',
                                       max_length=32,
                                       null=True,
                                       blank=True)
    contract_guaranty = models.CharField(verbose_name='保证合同编号',
                                         max_length=32,
                                         null=True,
                                         blank=True)
    remark = models.CharField(verbose_name='备注',
                              max_length=256,
                              null=True,
                              blank=True)
    time_limit = models.IntegerField(verbose_name='期限（月）')
    weighting = models.FloatField(verbose_name='加权金额')
    notify_provide_sum = models.FloatField(verbose_name='_放款金额', default=0)
    notify_repayment_sum = models.FloatField(verbose_name='_还款金额', default=0)
    notify_balance = models.FloatField(verbose_name='_在保余额', default=0)

    notifyor = models.ForeignKey(to='Employees',
                                 verbose_name="_创建者",
                                 on_delete=models.PROTECT,
                                 default=1,
                                 related_name='notifyor_employee')

    class Meta:
        verbose_name_plural = '放款-放款通知'  # 指定显示名称
        db_table = 'dbms_notify'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s' % (self.agree.agree_num, self.notify_date,
                             self.notify_money)


# ------------------------放款模型--------------------------#
class Provides(models.Model):  # 放款
    notify = models.ForeignKey(to='Notify',
                               verbose_name="_放款通知",
                               on_delete=models.PROTECT,
                               related_name='provide_notify')
    PROVIDE_TYP_LIST = [(1, 'D-流贷'), (11, 'D-承兑'), (21, 'D-保函'), (31, 'D-委贷'),
                        (41, 'X-过桥贷'), (52, 'X-房抵贷'), (53, 'X-担保贷'),
                        (55, 'X-经营贷'), (57, 'X-票据贷'), (58, 'X-消费贷')]
    provide_typ = models.IntegerField(verbose_name='放款种类',
                                      choices=PROVIDE_TYP_LIST)
    old_amount = models.FloatField(verbose_name='续贷金额', default=0)
    new_amount = models.FloatField(verbose_name='新增金额', default=0)
    provide_money = models.FloatField(verbose_name='放款金额', default=0)
    provide_date = models.DateField(verbose_name='放款日期')
    due_date = models.DateField(verbose_name='到期日')
    agree_rate = models.FloatField(verbose_name='保费率/利率(%)', default=0)
    investigation_fee = models.FloatField(verbose_name='咨询费/服务费(%)', default=0)
    charge = models.FloatField(verbose_name='担保费（元）', default=0)
    charge_fee = models.FloatField(verbose_name='咨询费/服务费（元）', default=0)
    bond_proportion = models.FloatField(verbose_name='客户保证金比例(%)', default=0)
    bond_amount = models.FloatField(verbose_name='客户保证金金额', default=0)
    IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'),
                      (41, '已归档'), (99, '无需归档')]
    implement = models.IntegerField(verbose_name='_归档状态',
                                    choices=IMPLEMENT_LIST,
                                    default=1)
    file_num = models.CharField(verbose_name='档案编号',
                                max_length=64,
                                unique=True,
                                null=True,
                                blank=True)

    PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (15, '展期'), (21, '代偿')]
    provide_status = models.IntegerField(verbose_name='放款状态',
                                         choices=PROVIDE_STATUS_LIST,
                                         default=1)
    provide_repayment_sum = models.FloatField(verbose_name='_还款总额', default=0)
    provide_balance = models.FloatField(verbose_name='_在保余额', default=0)

    fication = models.IntegerField(verbose_name='风险分类',
                                   choices=FICATION_LIST,
                                   default=11)
    fic_date = models.DateField(verbose_name='分类日期',
                                default=datetime.date.today)

    OBJ_TYP_LIST = [
        (1, '农户贷款'),
        (11, '关联企业或个体工商户贷款'),
        (15, '个人消费贷款'),
        (21, '农村企业贷款'),
        (23, '城市-小微企业'),
        (25, '城市-其他企业'),
        (99, '其他'),
    ]
    obj_typ = models.IntegerField(verbose_name='贷款对象分类',
                                  choices=OBJ_TYP_LIST,
                                  default=99)
    CREDIT_TYP_LIST = [(1, '纯信用贷款'), (11, '抵押贷款'), (15, '质押贷款'), (21, '保证贷款'),
                       (99, '其他')]
    credit_typ = models.IntegerField(verbose_name='信用形式分类',
                                     choices=CREDIT_TYP_LIST,
                                     default=99)

    providor = models.ForeignKey(to='Employees',
                                 verbose_name="_创建者",
                                 on_delete=models.PROTECT,
                                 related_name='providor_employee')
    providordate = models.DateField(verbose_name='_创建日期',
                                    default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '放款'  # 指定显示名称
        db_table = 'dbms_provides'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.notify, self.provide_money)


# ------------------------展期模型--------------------------#
class Extension(models.Model):  # 放款
    provide = models.ForeignKey(to='Provides',
                                verbose_name="_放款",
                                on_delete=models.PROTECT,
                                related_name='extension_provide')
    extension_amount = models.FloatField(verbose_name='展期金额', default=0)
    extension_date = models.DateField(verbose_name='展期日')
    extension_due_date = models.DateField(verbose_name='展期到期日')
    extensionor = models.ForeignKey(to='Employees',
                                    verbose_name="_创建者",
                                    on_delete=models.PROTECT,
                                    related_name='extensionor_employee')
    extensiondate = models.DateField(verbose_name='_创建日期',
                                     default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '放款-展期'  # 指定显示名称
        db_table = 'dbms_extension'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.provide, self.extension_amount)


# ------------------------还款模型--------------------------#
class Repayments(models.Model):  # 还款
    provide = models.ForeignKey(
        to='Provides',
        verbose_name="放款",
        on_delete=models.PROTECT,
        # limit_choices_to={'provide_status': 1},
        related_name='repayment_provide')
    repayment_money = models.FloatField(verbose_name='当期还款本金额', default=0)
    repayment_int = models.FloatField(verbose_name='当期还款利息额', default=0)
    repayment_pen = models.FloatField(verbose_name='当期还款违约金额', default=0)
    repayment_amt = models.FloatField(verbose_name='当期还款总额额', default=0)

    repayment_date = models.DateField(verbose_name='还款日期',
                                      default=datetime.date.today)
    repaymentor = models.ForeignKey(to='Employees',
                                    verbose_name="_创建者",
                                    on_delete=models.PROTECT,
                                    related_name='repaymentor_employee')
    repaymentdate = models.DateField(verbose_name='_创建日期',
                                     default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目-还款'  # 指定显示名称
        db_table = 'dbms_repayments'  # 指定数据表的名称
        ordering = [
            '-repayment_date',
        ]

    def __str__(self):
        return '%s_%s' % (self.provide, self.repayment_money)


# ------------------------归档模型--------------------------#
class Pigeonholes(models.Model):  # 归档
    provide = models.ForeignKey(to='Provides',
                                verbose_name="放款",
                                on_delete=models.PROTECT,
                                related_name='pigeonhole_provide')
    IMPLEMENT_LIST = Provides.IMPLEMENT_LIST
    implement = models.IntegerField(verbose_name='归档状态',
                                    choices=IMPLEMENT_LIST,
                                    default=1)
    pigeonhole_date = models.DateField(verbose_name='归档日期',
                                       default=datetime.date.today)
    pigeonhole_explain = models.CharField(verbose_name='归档说明',
                                          max_length=128,
                                          null=True,
                                          blank=True)
    pigeonhole_transfer = models.ForeignKey(
        to='Employees',
        verbose_name="移交人",
        on_delete=models.PROTECT,
        limit_choices_to={'employee_status': 1},
        related_name='pigeonhole_transfer_employee')
    pigeonholor = models.ForeignKey(to='Employees',
                                    verbose_name="_创建者",
                                    on_delete=models.PROTECT,
                                    related_name='pigeonholor_employee')

    class Meta:
        verbose_name_plural = '放款-归档'  # 指定显示名称
        db_table = 'dbms_pigeonholes'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s' % (self.provide, self.pigeonhole_date,
                             self.pigeonhole_transfer.name)


# ------------------------持续跟踪模型--------------------------#
class Track(models.Model):  #
    provide = models.ForeignKey(
        to='Provides',
        verbose_name="放款",
        on_delete=models.PROTECT,
        # limit_choices_to={'provide_status': 1},
        related_name='track_provide')
    TRACK_TYP_LIST = [
        (11, '日常计划'),
        (21, '分期还本'),
        (25, '等额本息'),
        (31, '按月付息'),
    ]
    track_typ = models.IntegerField(verbose_name='计划类型',
                                    choices=TRACK_TYP_LIST,
                                    default=11)
    plan_date = models.DateField(verbose_name='计划日期')
    proceed = models.CharField(verbose_name='跟踪内容', max_length=128)

    term_pri = models.FloatField(verbose_name='应收当期本金', default=0)  #应收当期本金
    term_int = models.FloatField(verbose_name='应收当期利息', default=0)  #应收当期利息
    term_pen = models.FloatField(verbose_name='应收当期违约金', default=0)  #应收当期违约金
    term_amt = models.FloatField(verbose_name='应收当期总额', default=0)  #应收当期总额

    ddd_pro = models.DateField(verbose_name='起始日期', null=True, blank=True)
    pro_aft_dif = models.IntegerField(verbose_name='计息天数', default=0)  #计息天数
    total_int = models.FloatField(verbose_name='利息累计', default=0)  #利息累计
    prin = models.FloatField(verbose_name='剩余本金', default=0)  #剩余本金
    term_int_j = models.FloatField(verbose_name='计息本金', default=0)  #

    term_pried = models.FloatField(verbose_name='已收当期本金', default=0)  #已收当期本金
    term_inted = models.FloatField(verbose_name='已收当期利息', default=0)  #已收当期利息
    term_pened = models.FloatField(verbose_name='已收当期违约金', default=0)  #已收当期违约金
    term_amted = models.FloatField(verbose_name='已收当期总额', default=0)  #已收当期总额

    track_date = models.DateField(verbose_name='跟踪日期', null=True, blank=True)
    condition = models.TextField(verbose_name='跟踪情况', null=True, blank=True)
    TRACK_STATE_LIST = [
        (11, '未结清'),
        (21, '已结清'),
    ]
    track_state = models.IntegerField(verbose_name='计划状态',
                                      choices=TRACK_STATE_LIST,
                                      default=11)
    trackor = models.ForeignKey(to='Employees',
                                verbose_name="_创建者",
                                on_delete=models.PROTECT,
                                related_name='trackor_employee')
    trackordate = models.DateField(verbose_name='_创建日期',
                                   default=datetime.date.today)

    class Meta:
        verbose_name_plural = '放款-跟踪'  # 指定显示名称
        db_table = 'dbms_track'  # 指定数据表的名称
        ordering = [
            'plan_date',
        ]

    def __str__(self):
        return '%s_%s' % (self.provide, self.term_pri)


# ------------------------持续跟踪模型--------------------------#
class TrackEX(models.Model):  #
    track = models.ForeignKey(
        to='Track',
        verbose_name="跟踪",
        on_delete=models.PROTECT,
        # limit_choices_to={'provide_status': 1},
        related_name='ex_track')

    ex_pried = models.FloatField(verbose_name='已收当期本金', default=0)  #已收当期本金
    ex_inted = models.FloatField(verbose_name='已收当期利息', default=0)  #已收当期利息
    ex_pened = models.FloatField(verbose_name='已收当期违约金', default=0)  #已收当期违约金
    ex_tamted = models.FloatField(verbose_name='已收当期总额', default=0)  #已收当期总额

    ex_track_date = models.DateField(verbose_name='回款日期')
    ex_condition = models.TextField(verbose_name='备注', null=True, blank=True)
    ex_trackor = models.ForeignKey(to='Employees',
                                   verbose_name="_创建者",
                                   on_delete=models.PROTECT,
                                   related_name='ex_employee')
    ex_date = models.DateField(verbose_name='_创建日期',
                               default=datetime.date.today)

    class Meta:
        verbose_name_plural = '放款-跟踪-EX'  # 指定显示名称
        db_table = 'dbms_trackex'  # 指定数据表的名称
        ordering = [
            '-ex_track_date',
        ]

    def __str__(self):
        return '%s_%s' % (self.track, self.ex_track_date)