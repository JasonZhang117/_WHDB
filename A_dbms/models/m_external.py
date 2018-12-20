from django.db import models
import datetime


# -----------------------授信银行-------------------------#
class Cooperators(models.Model):  # 授信银行
    name = models.CharField(
        verbose_name='授信银行',
        max_length=32, unique=True)
    short_name = models.CharField(
        verbose_name='银行简称',
        max_length=32, unique=True)
    flow_credit = models.FloatField(
        verbose_name='流贷&承兑额度',
        default=100000000)
    flow_limit = models.FloatField(
        verbose_name='流贷&承兑单笔限额',
        default=10000000)
    back_credit = models.FloatField(
        verbose_name='保函额度',
        default=0)
    back_limit = models.FloatField(
        verbose_name='保函单笔限额',
        default=0)
    credit_date = models.DateField(
        verbose_name='授信日期',
        default=datetime.date.today)
    flow_used = models.FloatField(
        verbose_name='流贷&承兑占用额度',
        default=0)
    flow_loan = models.FloatField(
        verbose_name='流贷&承兑放款额度',
        default=0)
    back_used = models.FloatField(
        verbose_name='保函占用额度',
        default=0)
    back_loan = models.FloatField(
        verbose_name='保函放款额度',
        default=0)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '外部-授信银行'  # 指定显示名称
        db_table = 'dbms_cooperators'  # 指定数据表的名称

    def __str__(self):
        return self.name


# -----------------------放款银行-------------------------#
class Branches(models.Model):  # 放款银行
    cooperator = models.ForeignKey(
        to='Cooperators',
        verbose_name="授信银行",
        on_delete=models.CASCADE,
        related_name='branch_cooperator')
    name = models.CharField(
        verbose_name='放款银行', max_length=32)
    institution_code = models.CharField(
        verbose_name='金融机构代码',
        max_length=32,
        unique=True)
    BRANCH_STATE_LIST = ((1, '正常'), (2, '注销'))
    branch_state = models.IntegerField(
        verbose_name='银行状态',
        choices=BRANCH_STATE_LIST,
        default=1)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '外部-放款银行'  # 指定显示名称
        db_table = 'dbms_branchess'  # 指定数据表的名称
        unique_together = (('name', 'cooperator'),)

    def __str__(self):
        return self.name


# -----------------------评审专家-------------------------#
class Experts(models.Model):  # 评审专家
    name = models.CharField(
        verbose_name='评审姓名',
        max_length=16)
    organization = models.CharField(
        verbose_name='工作单位',
        max_length=32)
    job = models.CharField(
        verbose_name='职务',
        max_length=16, null=True)
    LEVEL_LIST = ((1, '内部'), (2, '顾问'), (3, '一级'), (4, '二级'))
    level = models.IntegerField(
        verbose_name='级别',
        choices=LEVEL_LIST,
        default=1)
    contact_numb = models.CharField(
        verbose_name='联系电话',
        max_length=16, unique=True)
    email = models.CharField(
        verbose_name='邮箱',
        max_length=32, unique=True)
    ordery = models.IntegerField(
        verbose_name='优先级')
    EXPERT_STATE_LIST = ((1, '正常'), (2, '注销'))
    expert_state = models.IntegerField(
        verbose_name='评审状态',
        choices=EXPERT_STATE_LIST,
        default=1)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '外部-评审专家'  # 指定显示名称
        db_table = 'dbms_experts'  # 指定数据表的名称

    def __str__(self):
        return self.name
