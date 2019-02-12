import datetime
from django.db import models


# -----------------------委托合同模型-------------------------#
def limit_agree_choices():
    ''''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    return {'summary__article_state__in': [5, 61]}


class Agrees(models.Model):  # 委托合同
    agree_num = models.CharField(verbose_name='_合同编号', max_length=32, unique=True)
    num_prefix = models.CharField(verbose_name='_编号前缀', max_length=32)
    lending = models.ForeignKey(to='LendingOrder', verbose_name="放款纪要",
                                on_delete=models.PROTECT,
                                limit_choices_to=limit_agree_choices,
                                related_name='agree_lending')
    # limit_choices_to = limit_agree_choices,

    branch = models.ForeignKey(to='Branches', verbose_name="放款银行",
                               on_delete=models.PROTECT,
                               # limit_choices_to={'branch_state': 1},
                               related_name='agree_branch')
    agree_term = models.IntegerField(verbose_name='合同期限（月）')
    AGREE_TYP_LIST = ((1, '单笔'), (2, '最高额'), (3, '保函'))
    agree_typ = models.IntegerField(verbose_name='合同种类', choices=AGREE_TYP_LIST)
    GUARANTEE_TYP_LIST = (('②', '②'), ('③', '③'), ('④', '④'),
                          ('⑤', '⑤'), ('⑥', '⑥'), ('⑦', '⑦'),)
    guarantee_typ = models.CharField(verbose_name='反担保种类数', max_length=6, choices=GUARANTEE_TYP_LIST)
    agree_copies = models.IntegerField(verbose_name='合同份数')
    agree_amount = models.FloatField(verbose_name='合同金额')
    agree_sign_date = models.DateField(verbose_name='签批日期', null=True, blank=True)
    charge = models.FloatField(verbose_name='应收保费（元）', default=0)

    ascertain_date = models.DateField(verbose_name='落实日期', null=True, blank=True)
    agree_remark = models.TextField(verbose_name='落实情况', null=True, blank=True)

    AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))
    agree_state = models.IntegerField(verbose_name='合同状态', choices=AGREE_STATE_LIST, default=11)
    agree_notify_sum = models.FloatField(verbose_name='_通知金额', default=0)
    agree_provide_sum = models.FloatField(verbose_name='_放款金额', default=0)
    agree_repayment_sum = models.FloatField(verbose_name='_还款金额', default=0)

    agree_buildor = models.ForeignKey(to='Employees', verbose_name="创建人",
                                      on_delete=models.PROTECT, related_name='agree_buildor_employee')
    agree_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '合同'  # 指定显示名称
        db_table = 'dbms_agrees'  # 指定数据表的名称

    def __str__(self):
        return "%s_%s_(%s)" % (self.agree_num, self.agree_amount, self.lending)


# 合同变更-----********


class AgreeesExtend(models.Model):
    agree = models.OneToOneField(to='Agrees', verbose_name="委托合同",
                                 limit_choices_to={'counter_only': 0},
                                 on_delete=models.PROTECT,
                                 related_name='extend_agree')
    contact_addr = models.CharField(verbose_name='联系地址', max_length=64)
    linkman = models.CharField(verbose_name='联系人', max_length=16)
    contact_num = models.CharField(verbose_name='联系电话', max_length=13)
    registered_addr = models.CharField(verbose_name='注册地址', max_length=64, null=True, blank=True)
    representative = models.CharField(verbose_name='法人代表', max_length=16, null=True, blank=True)
    license_num = models.CharField(verbose_name='身份证号码', max_length=18, null=True, blank=True)

    class Meta:
        verbose_name_plural = '合同-委托合同扩展信息'  # 指定显示名称
        db_table = 'dbms_greeeExtend'  # 指定数据表的名称

    def __str__(self):
        return "%s_%s" % (self.agree.agree_num, 'extend')


# -----------------------反担保合同模型-------------------------#
class Counters(models.Model):  # 反担保合同
    counter_num = models.CharField(verbose_name='_合同编号', max_length=32, unique=True)
    agree = models.ForeignKey(to='Agrees', verbose_name="委托保证合同",
                              on_delete=models.PROTECT, related_name='counter_agree')
    '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'),  (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))
    counter_typ = models.IntegerField(verbose_name='合同类型', choices=COUNTER_TYP_LIST)
    counter_copies = models.IntegerField(verbose_name='合同份数')
    COUNTER_STATE_LIST = ((11, '未签订'), (21, '已签订'), (31, '作废'))

    counter_state = models.IntegerField(verbose_name='签订状态', choices=COUNTER_STATE_LIST, default=11)
    counter_sign_date = models.DateField(verbose_name='签订日期', null=True, blank=True)
    counter_remark = models.TextField(verbose_name='签订备注', null=True, blank=True)

    counter_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                        on_delete=models.PROTECT,
                                        related_name='counteror_employee')
    counter_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '合同-反担保'  # 指定显示名称
        db_table = 'dbms_counters'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.counter_num, self.agree.agree_num)


# ---------------------保证反担保合同模型-----------------------#
def limit_lending_choices():
    return {'article_state__in': [1, 2, 3, 4]}


class CountersAssure(models.Model):  # 保证反担保合同
    counter = models.OneToOneField(to='Counters',
                                   verbose_name="反担保合同",
                                   on_delete=models.PROTECT,
                                   related_name='assure_counter')
    custome = models.ManyToManyField(to='Customes',
                                     verbose_name="反担保人",
                                     related_name='counter_custome')
    counter_assure_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                               on_delete=models.PROTECT,
                                               related_name='counter_assureor_employee')
    counter_assure_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '合同-保证反担保'  # 指定显示名称
        db_table = 'dbms_countersassure'  # 指定数据表的名称

    def __str__(self):
        return "%s_%s" % (self.counter, self.counter.counter_typ)


# -------------------抵质押反担保合同模型--------------------#
class CountersWarrants(models.Model):  # 房产抵押反担保合同
    counter = models.OneToOneField(to='Counters', verbose_name="反担保合同",
                                   on_delete=models.PROTECT,
                                   related_name='warrant_counter')
    warrant = models.ManyToManyField(to='Warrants', verbose_name="抵质押物",
                                     related_name='counter_warrant')
    counter_warrant_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                                on_delete=models.PROTECT,
                                                related_name='counter_warrantor_employee')
    counter_warrant_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '合同-抵质押合同'  # 指定显示名称
        db_table = 'dbms_counterwarrants'  # 指定数据表的名称

    def __str__(self):
        return "%s_%s" % (self.counter, self.counter.counter_typ)
