from django.db import models
import datetime


# 项目、纪要
# -----------------------------项目模型------------------------------#
class Articles(models.Model):  # 项目、纪要
    article_num = models.CharField(
        verbose_name='_项目编号',
        max_length=32,
        unique=True)
    custom = models.ForeignKey(
        to='Customes',
        verbose_name="客户",
        on_delete=models.PROTECT,
        related_name='article_custom')
    renewal = models.FloatField(
        verbose_name='续贷金额（元）',
        null=True, blank=True)
    augment = models.FloatField(
        verbose_name='新增金额（元）',
        null=True, blank=True)
    amount = models.FloatField(
        verbose_name='_总额度（元）',
        null=True, blank=True)
    credit_term = models.IntegerField(
        verbose_name='授信期限（月）',
        default=12)
    director = models.ForeignKey(
        to='Employees',
        verbose_name="项目经理",
        on_delete=models.PROTECT,
        related_name='director_employee')
    assistant = models.ForeignKey(
        to='Employees',
        verbose_name="项目助理",
        on_delete=models.PROTECT,
        related_name='assistant_employee')
    control = models.ForeignKey(
        to='Employees',
        verbose_name="风控专员",
        on_delete=models.PROTECT,
        related_name='control_employee')
    article_date = models.DateField(
        verbose_name='提交日期',
        default=datetime.date.today)
    ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '已上会'),
                          (4, '无补调'), (5, '需补调'),
                          (6, '已补调'), (7, '已签批'))
    article_state = models.IntegerField(
        verbose_name='项目状态',
        choices=ARTICLE_STATE_LIST,
        default=1)
    # 自动创建第三张表
    expert = models.ManyToManyField(
        to='Experts',
        verbose_name="评审委员",
        related_name='article_expert')
    # 手动创建第三张表并关联
    # expert = models.ManyToManyField(
    #     to='Expert',
    #     through='ArticlesToExpert',
    #     through_fields=['article', 'expert'],
    #     verbose_name="评审",
    #     related_name='article_expert')
    # add,set的方法不能用了。
    summary_num = models.CharField(
        verbose_name='_纪要编号',
        max_length=32,
        unique=True,
        null=True, blank=True)
    sign_date = models.DateField(
        verbose_name='签批日期',
        null=True, blank=True)
    buildor = models.ForeignKey(
        to='Employees',
        verbose_name="创建人",
        on_delete=models.PROTECT,
        related_name='buildor_employee')

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '项目-项目'  # 指定显示名称
        db_table = 'dbms_articles'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s' % (self.article_num, self.summary_num)


'''
class Articles2Expert(models.Model):  # 手动创建第三张表
    article = models.ForeignKey(
        to='Articles',
        verbose_name="项目ID",
        on_delete=models.CASCADE,
        null=True)
    expert = models.ForeignKey(
        to='Experts',
        verbose_name="评审ID",
        on_delete=models.CASCADE,
        null=True)
    ctime = models.DateField(
        verbose_name="时间",
        null=True,
        default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目-项目'  # 指定显示名称
        db_table = 'dbms_articles2expert'  # 指定数据表的名称
        unique_together = [('article', 'expert'), ]

    def __str__(self):
        return "%s-%s" % (self.article.article_num,
                          self.expert.name)
'''
