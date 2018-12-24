from django.db import models
import time, datetime


# ------------------------评审会模型--------------------------#
class Appraisals(models.Model):  # 评审会
    num = models.CharField(
        verbose_name='评审会编号', max_length=32, unique=True)
    review_year = models.IntegerField(
        verbose_name='评审年份', default=datetime.date.today().year)
    review_order = models.IntegerField(verbose_name='评审次序')
    REVIEW_MODEL_LIST = ((1, '内审'), (2, '外审'))
    review_model = models.IntegerField(
        verbose_name='评审类型', choices=REVIEW_MODEL_LIST)
    review_date = models.DateField(
        verbose_name='评审日期', default=datetime.date.today)
    article = models.ManyToManyField(to='Articles',
                                     verbose_name="参评项目",
                                     related_name='appraisal_article',
                                     null=True, blank=True)
    meeting_buildor = models.ForeignKey(to='Employees',
                                        verbose_name="创建人",
                                        on_delete=models.PROTECT,
                                        related_name='meeting_buildor_employee')
    MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))
    meeting_state = models.IntegerField(
        verbose_name='会议状态', choices=MEETING_STATE_LIST, default=1)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '评审-审保会'  # 指定显示名称
        db_table = 'dbms_appraisals'  # 指定数据表的名称

    def __str__(self):
        return self.num


# ------------------------单项额度--------------------------#
class SingleQuota(models.Model):  # 单项额度
    summary = models.ForeignKey(to='Articles',
                                verbose_name="纪要",
                                on_delete=models.PROTECT,
                                related_name='single_quota_summary')
    CREDIT_MODEL_LIST = ((1, '流贷'), (2, '承兑'),
                         (3, '保函'), (4, '综合'))
    credit_model = models.IntegerField(
        verbose_name='授信类型', choices=CREDIT_MODEL_LIST, default=1)
    credit_amount = models.FloatField(verbose_name='授信额度（元）')
    flow_rate = models.FloatField(verbose_name='费率（%）')
    amount = models.FloatField(verbose_name='_放款金额（元）', default=0)
    single_buildor = models.ForeignKey(to='Employees',
                                       verbose_name="创建人",
                                       on_delete=models.PROTECT,
                                       related_name='single_buildor_employee')

    class Meta:
        verbose_name_plural = '评审-额度'  # 指定显示名称
        db_table = 'dbms_single_quota'  # 指定数据表的名称
        unique_together = ('summary', 'credit_model')

    def __str__(self):
        return "%s-%s-%s" % (self.summary,
                             self.credit_model,
                             self.credit_amount)


# ------------------------放款次序--------------------------#
def limit_lending_choices():
    return {'article_state__in': [1, 2, 3, 4]}


class LendingOrder(models.Model):
    summary = models.ForeignKey(to='Articles',
                                verbose_name="项目纪要",
                                on_delete=models.PROTECT,
                                limit_choices_to=limit_lending_choices,
                                related_name='lending_summary')
    ORDER_LIST = ((1, '第一次'), (2, '第二次'),
                  (3, '第三次'), (4, '第四次'))
    order = models.IntegerField(
        verbose_name='发放次序', choices=ORDER_LIST, default=1)
    order_amount = models.FloatField(verbose_name='拟放金额')
    amount = models.FloatField(verbose_name='已放金额', default=0)

    class Meta:
        verbose_name_plural = '评审-发放次序'  # 指定显示名称
        db_table = 'dbms_lending'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s-%s" % (self.summary, self.order, self.order_amount)


class LendingSures(models.Model):
    lending = models.ForeignKey(to='LendingOrder',
                                verbose_name="放款次序",
                                on_delete=models.PROTECT,
                                related_name='sure_lending')
    SURE_TYP_LIST = (
        (0, '--------'),
        (1, '个人保证'), (2, '企业保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'),
        (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))
    sure_typ = models.IntegerField(verbose_name='担保类型', choices=SURE_TYP_LIST)

    class Meta:
        verbose_name_plural = '反担保-反担保措施'  # 指定显示名称
        db_table = 'dbms_lendingsure'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s" % (self.lending, self.sure_typ)


class LendingCustoms(models.Model):
    sure = models.OneToOneField(to='LendingSures',
                                verbose_name="反担保措施",
                                on_delete=models.PROTECT,
                                related_name='custome_sure')
    custome = models.ManyToManyField(to='Customes',
                                     verbose_name="反担保人",
                                     related_name='lending_custome')

    class Meta:
        verbose_name_plural = '反担保-保证反担保'  # 指定显示名称
        db_table = 'dbms_lendingcustom'  # 指定数据表的名称

    def __str__(self):
        return '%s' % self.sure


class LendingWarrants(models.Model):
    sure = models.OneToOneField(
        to='LendingSures',
        verbose_name="反担保措施",
        on_delete=models.PROTECT,
        related_name='warrant_sure')
    warrant = models.ManyToManyField(
        to='Warrants',
        verbose_name="抵质押物",
        related_name='lending_warrant')

    class Meta:
        verbose_name_plural = '反担保-抵质押'  # 指定显示名称
        db_table = 'dbms_lendingwarrant'  # 指定数据表的名称

    def __str__(self):
        return '%s' % self.sure


# ------------------------评审意见--------------------------#
class Comments(models.Model):  # 评委意见
    summary = models.ForeignKey(
        to='Articles',
        verbose_name="纪要",
        on_delete=models.PROTECT,
        related_name='comment_summary')
    expert = models.ForeignKey(
        to='Experts',
        verbose_name="评委",
        on_delete=models.PROTECT,
        related_name='comment_expert')
    COMMENT_TYPE_LIST = ((0, '------'), (1, '同意'),
                         (2, '复议'), (3, '不同意'))
    comment_type = models.IntegerField(
        verbose_name='评委意见',
        choices=COMMENT_TYPE_LIST,
        default=1)
    concrete = models.TextField(
        verbose_name='意见详情',
        null=True, blank=True)
    comment_buildor = models.ForeignKey(
        to='Employees',
        verbose_name="创建人",
        on_delete=models.PROTECT,
        related_name='comment_buildor_employee')

    class Meta:
        verbose_name_plural = '评审-意见'  # 指定显示名称
        db_table = 'dbms_comments'  # 指定数据表的名称
        unique_together = ('summary', 'expert')

    def __str__(self):
        return "%s-%s-%s" % (self.summary,
                             self.expert,
                             self.comment_type)

# class Proposes(models.Model):  # 评审结论
