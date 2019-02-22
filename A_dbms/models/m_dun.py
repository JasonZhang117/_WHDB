from django.db import models
import datetime


# -----------------------代偿模型-------------------------#
class Compensatories(models.Model):  #
    provide = models.ForeignKey(to='Provides', verbose_name="放款",
                                on_delete=models.PROTECT,
                                related_name='compensatory_provide')
    compensatory_date = models.DateField(verbose_name='代偿日期', default=datetime.date.today)
    compensatory_capital = models.FloatField(verbose_name='代偿本金', default=0)
    compensatory_interest = models.FloatField(verbose_name='代偿利息', default=0)
    default_interest = models.FloatField(verbose_name='代偿罚息', default=0)
    compensatory_amount = models.FloatField(verbose_name='代偿总额')
    DUN_STATE_LIST = ((1, '已代偿'), (11, '已起诉'), (21, '已判决'), (31, '已和解'), (41, '执行中'), (91, '结案'))
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
                                          related_name='dun_compensatory')
    dun_amount = models.FloatField(verbose_name='追偿金额', default=0)
    recovered_amount = models.FloatField(verbose_name='回收金额', default=0)
    DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'))
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
    agent_term = models.IntegerField(verbose_name='代理期限(年)', blank=True, null=True)
    agent_date = models.DateField(verbose_name='代理日期')
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
                       (41, '代理员工'), (51, '助拍人员'), (99, '其他人员'))
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
        return '%s-%s-%s-%s' % (self.staff_name, self.staff_type, self.contact_number, self.staff_remark)


# -----------------------追偿费用模型-------------------------#
class Charge(models.Model):  #
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='charge_dun')

    CHARGE_TYPE_LIST = ((1, '律师代理费'), (11, '案件受理费'), (21, '财产保全费'), (31, '执行费'),
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
        return '%s-%s-%s-%s' % (self.dun.title, self.charge_type, self.charge_amount, self.charge_date)


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
        return '%s-%s-%s' % (self.retrieve_type, self.retrieve_amount, self.retrieve_date)


# -----------------------追偿流程-------------------------#
class Stage(models.Model):
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='stage_dun')

    STAGE_TYPE_LIST = ((1, '还款承诺'), (5, '起诉'), (11, '受理'), (15, '财产保全'), (21, '和解'), (25, '调解'),
                       (31, '判决'), (32, '上诉'), (41, '执行'), (43, '执行异议'), (51, '资料递交'),
                       (91, '公告'), (99, '其他'))
    stage_type = models.IntegerField(verbose_name='阶段', choices=STAGE_TYPE_LIST)

    stage_file = models.CharField(verbose_name='文件', max_length=64)
    stage_date = models.DateField(verbose_name='文件日期')

    stage_remark = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)
    stagor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                               related_name='stagor_employee')
    stagor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-追偿阶段'  # 指定显示名称
        db_table = 'dbms_stage'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s' % (self.stage_type, self.stage_file, self.stage_date)


# -----------------------判决-------------------------#
class Judgment(models.Model):
    dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
                            related_name='judgment_dun')

    judgment_file = models.CharField(verbose_name='文件编号', max_length=64)
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

    standing_detail = models.TextField(verbose_name='判决内容')
    standing_date = models.DateField(verbose_name='判决日期')

    standingor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                   related_name='standingor_employee')
    standingor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '追偿-跟进台账'  # 指定显示名称
        db_table = 'dbms_standing'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s' % (self.dun.title, self.standing_date)


# -----------------------财产线索-------------------------#
# class Clue(models.Model):  #
#     dun = models.ForeignKey(to='Dun', verbose_name="追偿项目", on_delete=models.PROTECT,
#                             related_name='clue_dun')
#     warrant = models.ManyToManyField(to='Warrants', verbose_name="财产",
#                                      related_name='clue_warrant')
#
#     dun_amount = models.FloatField(verbose_name='追偿金额', default=0)
#     recovered_amount = models.FloatField(verbose_name='回收金额', default=0)
#
#     DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'))
#     dun_stage = models.IntegerField(verbose_name='追偿状态', choices=DUN_STAGE_LIST, default=1)
#     sealing_date = models.DateField(verbose_name='查封日期')
#     sealing_term = models.IntegerField(verbose_name='查封期限(月）')
#
#     cluor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
#                               related_name='cluor_employee')
#     cluor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)
#
#     class Meta:
#         verbose_name_plural = '追偿-财产线索'  # 指定显示名称
#         db_table = 'dbms_clue'  # 指定数据表的名称
#
#     def __str__(self):
#         return self.warrant


# -----------------------查封财产财产-------------------------#
'''查封日期，续查封日期、评估情况、拍卖情况……'''
