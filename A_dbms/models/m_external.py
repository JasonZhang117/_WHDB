from django.db import models
import datetime


# -----------------------授信银行-------------------------#
class Cooperators(models.Model):  # 授信银行
    name = models.CharField(verbose_name='合作机构', max_length=32, unique=True)
    short_name = models.CharField(verbose_name='机构简称', max_length=32, unique=True)
    COOPERATOR_TYPE_LIST = ((1, '金融机构'), (11, '律师事务所'), (21, '评估事务所'), (91, '其他机构'))
    cooperator_type = models.IntegerField(verbose_name='机构类型', choices=COOPERATOR_TYPE_LIST, default=1)
    flow_credit = models.FloatField(verbose_name='综合额度', blank=True, null=True)
    flow_limit = models.FloatField(verbose_name='单笔限额（综合）', blank=True, null=True)
    back_credit = models.FloatField(verbose_name='保函额度', blank=True, null=True)
    back_limit = models.FloatField(verbose_name='单笔限额（保函）', blank=True, null=True)
    credit_date = models.DateField(verbose_name='合作日期', blank=True, null=True)
    due_date = models.DateField(verbose_name='到期日', blank=True, null=True)
    up_scale = models.FloatField(verbose_name='最高额上浮比例', default=0)
    cooperator_flow = models.FloatField(verbose_name='_流贷余额', default=0)
    cooperator_accept = models.FloatField(verbose_name='_承兑余额', default=0)
    cooperator_back = models.FloatField(verbose_name='_保函余额', default=0)
    entrusted_loan = models.FloatField(verbose_name='_委贷余额', default=0)
    petty_loan = models.FloatField(verbose_name='_过桥贷余额', default=0)
    amount = models.FloatField(verbose_name='_在保总额', default=0)
    COOPERATOR_STATE_LIST = ((1, '正常'), (11, '注销'))
    cooperator_state = models.IntegerField(verbose_name='状态', choices=COOPERATOR_STATE_LIST, default=1)
    cooperat = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                 related_name='cooperat_employee')
    cooperat_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '外部-合作机构'  # 指定显示名称
        db_table = 'dbms_cooperators'  # 指定数据表的名称

    def __str__(self):
        return self.name


# -----------------------合作协议-------------------------#
class Agreements(models.Model):  #
    cooperator = models.ForeignKey(to='Cooperators', verbose_name="合作机构",
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'cooperator_state': 1},
                                   related_name='agreement_cooperator')
    flow_credit = models.FloatField(verbose_name='综合额度', default=100000000)
    flow_limit = models.FloatField(verbose_name='单笔（综合）', default=10000000)
    back_credit = models.FloatField(verbose_name='保函额度', default=0)
    back_limit = models.FloatField(verbose_name='单笔（保函）', default=0)
    credit_date = models.DateField(verbose_name='合作日期', default=datetime.date.today)
    due_date = models.DateField(verbose_name='到期日', default=datetime.date.today)
    agreementor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                    related_name='agreementor_employee')
    agreementor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '外部-合作协议'  # 指定显示名称
        db_table = 'dbms_agreements'  # 指定数据表的名称

    def __str__(self):
        return self.cooperator.name


# -----------------------放款银行-------------------------#
class Branches(models.Model):  # 放款银行
    cooperator = models.ForeignKey(to='Cooperators', verbose_name="授信银行",
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'cooperator_state': 1},
                                   related_name='branch_cooperator')
    name = models.CharField(verbose_name='放款银行', max_length=32, unique=True)
    short_name = models.CharField(verbose_name='银行简称', max_length=32, unique=True)
    BRANCH_STATE_LIST = ((1, '正常'), (2, '注销'))
    branch_state = models.IntegerField(verbose_name='银行状态', choices=BRANCH_STATE_LIST, default=1)
    branch_flow = models.FloatField(verbose_name='_流贷余额', default=0)
    branch_accept = models.FloatField(verbose_name='_承兑余额', default=0)
    branch_back = models.FloatField(verbose_name='_保函余额', default=0)
    entrusted_loan = models.FloatField(verbose_name='_委贷余额', default=0)
    petty_loan = models.FloatField(verbose_name='_过桥贷余额', default=0)
    amount = models.FloatField(verbose_name='_在保总额', default=0)
    branchor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                 related_name='branchor_employee')
    branchor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '外部-放款银行'  # 指定显示名称
        db_table = 'dbms_branchess'  # 指定数据表的名称
        unique_together = (('name', 'cooperator'),)
        ordering = ['name', ]

    def __str__(self):
        return self.name


# -----------------------评审专家-------------------------#
class Experts(models.Model):  # 评审专家
    name = models.CharField(verbose_name='评审姓名', max_length=16)
    organization = models.CharField(verbose_name='工作单位', max_length=32)
    job = models.CharField(verbose_name='职务', max_length=16, null=True)
    LEVEL_LIST = ((1, '内部'), (2, '顾问'), (3, '一级'), (4, '二级'))
    level = models.IntegerField(verbose_name='级别', choices=LEVEL_LIST, default=1)
    contact_numb = models.CharField(verbose_name='联系电话', max_length=16, unique=True)
    email = models.CharField(verbose_name='邮箱', max_length=32)
    ordery = models.IntegerField(verbose_name='优先级')
    EXPERT_STATE_LIST = ((1, '正常'), (2, '注销'))
    expert_state = models.IntegerField(verbose_name='评审状态', choices=EXPERT_STATE_LIST, default=1)
    expertor = models.ForeignKey(to='Employees', verbose_name="创建人", on_delete=models.PROTECT,
                                 related_name='expertor_employee')
    expertor_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '外部-评审专家'  # 指定显示名称
        db_table = 'dbms_experts'  # 指定数据表的名称
        ordering = ['ordery']

    def __str__(self):
        return self.name
