from django.db import models
import time, datetime


# ------------------------评审会模型--------------------------#
class Appraisals(models.Model):  # 评审会
    num = models.CharField(
        verbose_name='评审会编号',
        max_length=32,
        unique=True)
    review_year = models.IntegerField(
        verbose_name='评审年份',
        default=datetime.date.today().year)
    review_order = models.IntegerField(
        verbose_name='评审次序')
    REVIEW_MODEL_LIST = ((1, '内审'), (2, '外审'))
    review_model = models.IntegerField(
        verbose_name='评审类型',
        choices=REVIEW_MODEL_LIST)
    review_date = models.DateField(
        verbose_name='评审日期',
        default=datetime.date.today)
    article = models.ManyToManyField(
        to='Articles',
        verbose_name="参评项目",
        related_name='appraisal_article',
        null=True, blank=True)
    meeting_buildor = models.ForeignKey(
        to='Employees',
        verbose_name="创建人",
        on_delete=models.PROTECT,
        related_name='meeting_buildor_employee')
    MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))
    meeting_state = models.IntegerField(
        verbose_name='项目状态',
        choices=MEETING_STATE_LIST,
        default=1)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '评审-审保会'  # 指定显示名称
        db_table = 'dbms_appraisals'  # 指定数据表的名称

    def __str__(self):
        return self.num


# ------------------------单项额度--------------------------#
class SingleQuota(models.Model):  # 单项额度
    summary = models.ForeignKey(
        to='Articles',
        verbose_name="纪要",
        on_delete=models.PROTECT,
        related_name='single_quota_summary')
    CREDIT_MODEL_LIST = ((1, '流贷'), (2, '承兑'),
                         (3, '保函'), (4, '综合'))
    credit_model = models.IntegerField(
        verbose_name='授信类型',
        choices=CREDIT_MODEL_LIST,
        default=1)
    credit_amount = models.FloatField(
        verbose_name='授信额度（元）')
    flow_rate = models.FloatField(
        verbose_name='费率（%）')
    amount = models.FloatField(
        verbose_name='_放款金额（元）',
        default=0)
    single_buildor = models.ForeignKey(
        to='Employees',
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
