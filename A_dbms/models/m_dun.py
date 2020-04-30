from django.db import models
import datetime


# -----------------------代偿模型-------------------------#
class Compensatories(models.Model):  #
    title = models.CharField(verbose_name='标志', max_length=128)
    provide = models.ForeignKey(to='Provides', verbose_name="放款",
                                on_delete=models.PROTECT,
                                related_name='compensatory_provide')
    compensatory_date = models.DateField(verbose_name='代偿日期', default=datetime.date.today)
    compensatory_capital = models.FloatField(verbose_name='代偿本金', default=0)
    compensatory_interest = models.FloatField(verbose_name='代偿利息', default=0)
    default_interest = models.FloatField(verbose_name='代偿罚息', default=0)
    compensatory_amount = models.FloatField(verbose_name='代偿总额')
    '''STAGE_TYPE_LIST = ((1, '证据及财产线索资料'), (11, '诉前资料'), (21, '一审资料'),
                           (31, '上诉及再审'), (41, '案外之诉'),
                           (51, '执行资料'), (99, '其他'))'''
    DUN_STATE_LIST = [(1, '已代偿'), (3, '诉前'), (11, '一审'), (21, '上诉及再审'), (31, '案外之诉'),
                      (41, '执行'), (91, '结案')]
    dun_state = models.IntegerField(verbose_name='追偿状态', choices=DUN_STATE_LIST, default=1)
    compensator = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                    related_name='compensator_employee')
    compensator_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-代偿'  # 指定显示名称
        db_table = 'dbms_compensatories'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.provide, self.compensatory_amount)


# -----------------------追偿模型-------------------------#
class Dun(models.Model):  #
    title = models.CharField(verbose_name='追偿', max_length=128, unique=True)
    compensatory = models.ManyToManyField(to='Compensatories', verbose_name="代偿",
                                          related_name='dun_compensatory', blank=True, null=True)
    dun_amount = models.FloatField(verbose_name='追偿金额', default=0)
    dun_retrieve_sun = models.FloatField(verbose_name='_回收金额', default=0)
    dun_charge_sun = models.FloatField(verbose_name='_追偿费用', default=0)
    dun_balance = models.FloatField(verbose_name='_剩余金额', default=0)
    warrant = models.ManyToManyField(to='Warrants', verbose_name="资产线索",
                                     related_name='dun_warrant',
                                     null=True, blank=True)
    custom = models.ManyToManyField(to='Customes', verbose_name="被告人",
                                    related_name='dun_custom',
                                    null=True, blank=True)
    up_date = models.DateField(verbose_name='跟新日期', default=datetime.date.today)                                
    DUN_STAGE_LIST = [(1, '已代偿'), (3, '诉前'), (11, '一审'), (21, '上诉及再审'), (31, '案外之诉'),
                      (41, '执行'), (51, '终本''),(91, '结案')]
    dun_stage = models.IntegerField(verbose_name='追偿状态', choices=DUN_STAGE_LIST, default=1)
    dunor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                              related_name='dunor_employee')
    dunor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿'  # 指定显示名称
        db_table = 'dbms_dun'  # 指定数据表的名称

    def __str__(self):
        return self.title


# -----------------------代理模型-------------------------#
class Agent(models.Model):  #
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='agent_dun')
    agent_agree = models.CharField(verbose_name='代理合同', max_length=64, unique=True)
    agent_item = models.TextField(verbose_name='代理事项', blank=True, null=True)
    fee_scale = models.TextField(verbose_name='收费标准', blank=True, null=True)
    agent_date = models.DateField(verbose_name='代理日期')
    due_date = models.DateField(verbose_name='到期日')
    AGENT_STATE_LIST = ((1, '生效'), (11, '失效'), (99, '注销'))
    agent_state = models.IntegerField(verbose_name='合同状态', choices=AGENT_STATE_LIST, default=1)
    agent_remark = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)

    agentor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                related_name='agentor_employee')
    agentor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-代理合同'  # 指定显示名称
        db_table = 'dbms_agent'  # 指定数据表的名称

    def __str__(self):
        return self.agent_agree


# -----------------------人员模型-------------------------#
class Staff(models.Model):  #
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='staff_dun')
    staff_name = models.CharField(verbose_name='姓名', max_length=64, unique=True)
    STAFF_TYPE_LIST = ((1, '代理律师'), (11, '审判法官'), (21, '执行法官'), (31, '评估人员'),
                       (41, '代理员工'), (51, '助拍人员'), (51, '竞拍人员'), (99, '其他人员'))
    staff_type = models.IntegerField(verbose_name='人员类型', choices=STAFF_TYPE_LIST)
    contact_number = models.CharField(verbose_name='联系电话', max_length=32)

    staff_remark = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)
    staffor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                related_name='staffor_employee')
    staffor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-人员'  # 指定显示名称
        db_table = 'dbms_staff'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s_%s' % (self.staff_name, self.staff_type, self.contact_number, self.staff_remark)


# -----------------------追偿费用模型-------------------------#
class Charge(models.Model):  #
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='charge_dun')

    CHARGE_TYPE_LIST = ((1, '律师代理费'), (11, '案件受理费'), (21, '财产保全费'), (25, '评估费'), (31, '执行费'),
                        (41, '公告费'), (99, '其他费用'))
    charge_type = models.IntegerField(verbose_name='费用类型', choices=CHARGE_TYPE_LIST)
    charge_amount = models.FloatField(verbose_name='金额')
    charge_date = models.DateField(verbose_name='支付日期')

    charge_remark = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)
    chargor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                related_name='chargor_employee')
    chargor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-追偿费用'  # 指定显示名称
        db_table = 'dbms_charge'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s_%s' % (self.dun.title, self.charge_type, self.charge_amount, self.charge_date)


# -----------------------案款回收模型-------------------------#
class Retrieve(models.Model):
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='retrieve_dun')

    RETRIEVE_TYPE_LIST = ((1, '诉讼前清收'), (11, '履行判决'), (21, '强制执行'), (31, '执行资产抵债'),
                          (99, '其他回收方式'))
    retrieve_type = models.IntegerField(verbose_name='回收类型', choices=RETRIEVE_TYPE_LIST)
    retrieve_amount = models.FloatField(verbose_name='金额')
    retrieve_date = models.DateField(verbose_name='回收日期')
    retrieve_remark = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)

    retrievor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                  related_name='retrievor_employee')
    retrievor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-案款回收'  # 指定显示名称
        db_table = 'dbms_retrieve'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s' % (self.retrieve_type, self.retrieve_amount, self.retrieve_date)


# -----------------------资料目录-------------------------#
class Stage(models.Model):
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='stage_dun')

    STAGE_TYPE_LIST = ((1, '证据及财产线索资料'), (11, '诉前资料'), (21, '一审资料'),
                       (31, '上诉及再审'), (41, '案外之诉'),
                       (51, '执行资料'), (99, '其他'))
    stage_type = models.IntegerField(verbose_name='资料类型', choices=STAGE_TYPE_LIST)
    STAGE_STATE_LIST = ((1, '原件'), (11, '复印件'))
    stage_state = models.IntegerField(verbose_name='原件或复印件', choices=STAGE_STATE_LIST)

    stage_file = models.CharField(verbose_name='文件', max_length=64)
    stage_date = models.DateField(verbose_name='文件日期')

    page_amout = models.IntegerField(verbose_name='页数')

    stage_remark = models.CharField(verbose_name='索引号', max_length=64, blank=True, null=True)
    stagor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                               related_name='stagor_employee')
    stagor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-追偿阶段'  # 指定显示名称
        db_table = 'dbms_stage'  # 指定数据表的名称
        ordering = ['stage_type', 'id']

    def __str__(self):
        return '%s_%s_%s' % (self.stage_type, self.stage_file, self.stage_date)


# -----------------------判决与裁定-------------------------#
class Judgment(models.Model):
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='judgment_dun')

    judgment_file = models.CharField(verbose_name='文件编号', max_length=64, unique=True)
    judgment_detail = models.TextField(verbose_name='判决内容')
    judgment_unit = models.CharField(verbose_name='单位', max_length=64)
    judgment_date = models.DateField(verbose_name='判决日期')
    # judgment_remark = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)

    judgmentor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                   related_name='judgmentor_employee')
    judgmentor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-判决'  # 指定显示名称
        db_table = 'dbms_judgment'  # 指定数据表的名称

    def __str__(self):
        return self.judgment_file


# -----------------------周报-------------------------#
class Standing(models.Model):
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='standing_dun')

    standing_detail = models.TextField(verbose_name='追偿情况')

    standingor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                   related_name='standingor_employee')
    standingor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-跟进台账'  # 指定显示名称
        db_table = 'dbms_standing'  # 指定数据表的名称
        ordering = ['-standingor_date',]

    def __str__(self):
        return '%s_%s' % (self.dun.title, self.standingor_date)


# ------------------------财产线索--------------------------#
class Seal(models.Model):
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目",
                            on_delete=models.PROTECT,
                            related_name='seal_dun')
    warrant = models.ForeignKey(to='Warrants', verbose_name="财产",
                                on_delete=models.PROTECT,
                                related_name='seal_warrant')
    SEAL_STATE_LIST = [(1, '查询跟踪'), (3, '诉前保全'), (5, '首次首封'), (11, '首次轮封'), (21, '续查封'),
                       (51, '解除查封'), (99, '注销')]
    seal_state = models.IntegerField(verbose_name='查封状态', choices=SEAL_STATE_LIST, default=1)
    seal_date = models.DateField(verbose_name='_最近查封日', blank=True, null=True)
    due_date = models.DateField(verbose_name='_查封到期日', blank=True, null=True)
    inquiry_date = models.DateField(verbose_name='_最近查询日', blank=True, null=True)
    seal_remark = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)

    sealor = models.ForeignKey(to='Employees', verbose_name="创建人",
                               on_delete=models.PROTECT,
                               related_name='sealor_employee')
    sealor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-查封现状'  # 指定显示名称
        db_table = 'dbms_seal'  # 指定数据表的名称
        unique_together = ('dun', 'warrant')
        ordering = ['-seal_date']

    def __str__(self):
        return "%s_%s_%s" % (self.dun.title, self.warrant.warrant_num, self.seal_state)


# ------------------------查封情况--------------------------#
class Sealup(models.Model):
    seal = models.ForeignKey(to='Seal', verbose_name="财产线索", on_delete=models.PROTECT,
                             related_name='sealup_seal')
    SEALUP_TYPE_LIST = Seal.SEAL_STATE_LIST
    sealup_type = models.IntegerField(verbose_name='查封类型', choices=SEALUP_TYPE_LIST, default=1)
    sealup_date = models.DateField(verbose_name='查封日期', blank=True, null=True)
    due_date = models.DateField(verbose_name='到期日', blank=True, null=True)
    sealup_remark = models.CharField(verbose_name='备注', max_length=64, null=True, blank=True)

    sealupor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                 related_name='sealup_employee')
    sealupor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-查封明细'  # 指定显示名称
        ordering = ['-sealupor_date']
        db_table = 'dbms_sealup'  # 指定数据表的名称


    def __str__(self):
        return '%s_%s_%s_%s' % (self.seal.dun.title, self.seal.warrant.warrant_num, self.sealup_type, self.sealup_date)


# ------------------------查询情况--------------------------#
class Inquiry(models.Model):
    seal = models.ForeignKey(to='Seal', verbose_name="财产线索", on_delete=models.PROTECT,
                             related_name='inquiry_seal')
    INQUIRY_TYPE_LIST = (
        (1, '日常跟踪'), (3, '拍卖评估'), (5, '拍卖挂网'), (11, '拍卖成交'), (21, '拍卖流拍'),
        (31, '执行回转'), (99, '注销'))
    inquiry_type = models.IntegerField(verbose_name='查询类型', choices=INQUIRY_TYPE_LIST, default=1)
    evaluate_date = models.DateField(verbose_name='评估日期', null=True, blank=True)
    evaluate_value = models.FloatField(verbose_name='评估价值', null=True, blank=True)
    auction_date = models.DateField(verbose_name='拍卖日期', blank=True, null=True)
    listing_price = models.FloatField(verbose_name='挂网价格', blank=True, null=True)
    transaction_date = models.DateField(verbose_name='成交日期', blank=True, null=True)
    auction_amount = models.FloatField(verbose_name='成交金额', blank=True, null=True)

    inquiry_detail = models.TextField(verbose_name='查询情况', null=True, blank=True)
    inquiryor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                  related_name='inquiryor_employee')
    inquiryor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-查询情况'  # 指定显示名称
        db_table = 'dbms_inquiry'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s' % (self.seal.dun.title, self.seal.warrant.warrant_num, self.inquiryor_date)
