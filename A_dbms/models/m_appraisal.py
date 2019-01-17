from django.db import models
import time, datetime


# ------------------------评审会模型--------------------------#
class Appraisals(models.Model):  # 评审会
    num = models.CharField(verbose_name='评审会编号', max_length=32, unique=True)
    review_year = models.IntegerField(verbose_name='评审年份', default=datetime.date.today().year)
    review_order = models.IntegerField(verbose_name='评审次序')
    REVIEW_MODEL_LIST = ((1, '内审'), (2, '外审'))
    review_model = models.IntegerField(verbose_name='评审类型', choices=REVIEW_MODEL_LIST)
    review_date = models.DateField(verbose_name='评审日期', default=datetime.date.today)
    article = models.ManyToManyField(to='Articles', verbose_name="参评项目",
                                     related_name='appraisal_article',
                                     limit_choices_to={'article_state': 2},
                                     null=True, blank=True)
    MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))
    meeting_state = models.IntegerField(verbose_name='会议状态', choices=MEETING_STATE_LIST, default=1)
    meeting_buildor = models.ForeignKey(to='Employees', verbose_name="创建人",
                                        on_delete=models.PROTECT, default=1,
                                        related_name='meeting_buildor_employee')
    meeting_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '评审-审保会'  # 指定显示名称
        db_table = 'dbms_appraisals'  # 指定数据表的名称

    def __str__(self):
        return self.num


# ------------------------单项额度--------------------------#
def limit_article_choices():
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'),
    (5, '已签批'), (6, '已注销'))'''
    return {'article_state__in': [4, 5]}


class SingleQuota(models.Model):  # 单项额度
    summary = models.ForeignKey(to='Articles', verbose_name="纪要",
                                on_delete=models.PROTECT,
                                limit_choices_to=limit_article_choices,
                                related_name='single_quota_summary')
    CREDIT_MODEL_LIST = [(1, '流动资金贷款担保'), (2, '银行承兑汇票担保'), (3, '保函担保'),
                         (4, '综合授信额度担保（含流贷、银承、保函）')]
    credit_model = models.IntegerField(verbose_name='授信类型', choices=CREDIT_MODEL_LIST, default=1)
    credit_amount = models.FloatField(verbose_name='授信额度（元）')
    flow_rate = models.FloatField(verbose_name='费率（%）')
    amount = models.FloatField(verbose_name='_放款金额（元）', default=0)
    single_buildor = models.ForeignKey(to='Employees', verbose_name="创建人",
                                       on_delete=models.PROTECT, default=1,
                                       related_name='single_buildor_employee')
    single_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '评审-额度'  # 指定显示名称
        db_table = 'dbms_single_quota'  # 指定数据表的名称
        unique_together = ('summary', 'credit_model')

    def __str__(self):
        return "%s_%s_%s" % (self.summary, self.credit_model, self.credit_amount)


# ------------------------放款次序--------------------------#
def limit_lending_choices():
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'),
    (5, '已签批'), (6, '已注销'))'''
    return {'article_state__in': [1, 2]}


class LendingOrder(models.Model):
    summary = models.ForeignKey(to='Articles', verbose_name="项目纪要",
                                on_delete=models.PROTECT,
                                limit_choices_to=limit_lending_choices,
                                related_name='lending_summary')
    ORDER_LIST = ((1, '第一次'), (2, '第二次'), (3, '第三次'), (4, '第四次'))
    order = models.IntegerField(verbose_name='发放次序', choices=ORDER_LIST, default=1)
    order_amount = models.FloatField(verbose_name='拟放金额')

    lending_provide_sum = models.FloatField(verbose_name='_放款金额', default=0)
    lending_repayment_sum = models.FloatField(verbose_name='_还款金额', default=0)

    lending_buildor = models.ForeignKey(to='Employees', verbose_name="创建者",
                                        on_delete=models.PROTECT, default=1,
                                        related_name='lending_employee')
    lending_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '评审-发放次序'  # 指定显示名称
        db_table = 'dbms_lending'  # 指定数据表的名称
        unique_together = ('summary', 'order')

    def __str__(self):
        return "%s_%s_%s" % (self.summary.summary_num, self.order, self.order_amount)


# ------------------------反担保措施--------------------------#
class LendingSures(models.Model):
    lending = models.ForeignKey(to='LendingOrder', verbose_name="放款次序",
                                on_delete=models.PROTECT,
                                related_name='sure_lending')
    SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))
    sure_typ = models.IntegerField(verbose_name='担保类型', choices=SURE_TYP_LIST)
    sure_buildor = models.ForeignKey(to='Employees', verbose_name="创建人",
                                     on_delete=models.PROTECT, default=1,
                                     related_name='sure_buildor_employee')
    sure_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '反担保-反担保措施'  # 指定显示名称
        db_table = 'dbms_lendingsure'  # 指定数据表的名称

    def __str__(self):
        return "%s_%s" % (self.lending, self.sure_typ)


# ------------------------反担保-保证--------------------------#
class LendingCustoms(models.Model):
    sure = models.OneToOneField(to='LendingSures', verbose_name="反担保措施",
                                on_delete=models.PROTECT,
                                related_name='custom_sure')
    custome = models.ManyToManyField(to='Customes', verbose_name="反担保人",
                                     related_name='lending_custom',
                                     db_constraint=True)
    lending_c_buildor = models.ForeignKey(to='Employees', verbose_name="创建人",
                                          on_delete=models.PROTECT, default=1,
                                          related_name='lending_c_buildor_employee')
    lending_c_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '反担保-保证反担保'  # 指定显示名称
        db_table = 'dbms_lendingcustom'  # 指定数据表的名称
        # unique_together = ('sure', 'custome')

    def __str__(self):
        return "%s_%s" % (self.sure, self.custome)


# ------------------------反担保-抵质押--------------------------#
class LendingWarrants(models.Model):
    sure = models.OneToOneField(to='LendingSures', verbose_name="反担保措施",
                                on_delete=models.PROTECT,
                                related_name='warrant_sure')
    warrant = models.ManyToManyField(to='Warrants', verbose_name="抵质押物",
                                     related_name='lending_warrant',
                                     db_constraint=True)
    lending_w_buildor = models.ForeignKey(to='Employees', verbose_name="创建人",
                                          on_delete=models.PROTECT, default=1,
                                          related_name='lending_w_buildor_employee')
    lending_w_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '反担保-抵质押'  # 指定显示名称
        db_table = 'dbms_lendingwarrant'  # 指定数据表的名称

    def __str__(self):
        return "%s_%s" % (self.sure, self.warrant)


# ------------------------评审意见--------------------------#
class Comments(models.Model):  # 评委意见
    summary = models.ForeignKey(to='Articles', verbose_name="纪要",
                                on_delete=models.PROTECT,
                                related_name='comment_summary')
    expert = models.ForeignKey(to='Experts', verbose_name="评委",
                               on_delete=models.PROTECT,
                               related_name='comment_expert')
    COMMENT_TYPE_LIST = ((1, '同意'), (2, '复议'), (3, '不同意'))
    comment_type = models.IntegerField(verbose_name='评委意见', choices=COMMENT_TYPE_LIST, default=1)
    concrete = models.TextField(verbose_name='意见详情')
    comment_buildor = models.ForeignKey(to='Employees', verbose_name="创建人",
                                        on_delete=models.PROTECT, default=1,
                                        related_name='comment_buildor_employee')
    comment_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '评审-意见'  # 指定显示名称
        db_table = 'dbms_comments'  # 指定数据表的名称
        unique_together = ('summary', 'expert')

    def __str__(self):
        return "%s_%s_%s" % (self.summary.summary_num, self.expert, self.comment_type)
