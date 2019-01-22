from django.db import models
import datetime


# -----------------------------项目模型------------------------------#
class Articles(models.Model):  # 项目、纪要
    article_num = models.CharField(verbose_name='_项目编号', max_length=32, unique=True)
    custom = models.ForeignKey(to='Customes', verbose_name="客户",
                               on_delete=models.PROTECT,
                               limit_choices_to={'counter_only': 0},
                               related_name='article_custom')
    renewal = models.FloatField(verbose_name='续贷金额（元）', default=0)
    augment = models.FloatField(verbose_name='新增金额（元）', default=0)
    amount = models.FloatField(verbose_name='_总额度（元）', default=0)
    credit_term = models.IntegerField(verbose_name='授信期限（月）', default=12)
    director = models.ForeignKey(to='Employees', verbose_name="项目经理",
                                 on_delete=models.PROTECT,
                                 related_name='director_employee')
    assistant = models.ForeignKey(to='Employees', verbose_name="项目助理",
                                  on_delete=models.PROTECT,
                                  related_name='assistant_employee')
    control = models.ForeignKey(to='Employees', verbose_name="风控专员",
                                on_delete=models.PROTECT,
                                related_name='control_employee')
    article_date = models.DateField(verbose_name='反馈日期', default=datetime.date.today)

    # 自动创建第三张表
    expert = models.ManyToManyField(to='Experts', verbose_name="评审委员",
                                    related_name='article_expert')
    review_date = models.DateField(verbose_name='上会日期', null=True, blank=True)
    summary_num = models.CharField(verbose_name='_纪要编号', max_length=32, unique=True, null=True, blank=True)
    SIGN_TYPE_LIST = ((1, '同意'), (2, '不同意'))
    sign_type = models.IntegerField(verbose_name='签批结论', choices=SIGN_TYPE_LIST, null=True, blank=True)
    rcd_opinion = models.TextField(verbose_name='风控部意见', null=True, blank=True)
    convenor_opinion = models.TextField(verbose_name='招集人意见', null=True, blank=True)
    sign_detail = models.TextField(verbose_name='签批人意见', null=True, blank=True)
    sign_date = models.DateField(verbose_name='签批日期', null=True, blank=True)

    ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))
    article_state = models.IntegerField(verbose_name='_项目状态', choices=ARTICLE_STATE_LIST, default=1)
    CLASSIFICATION_LIST = ((1, '正常'), (11, '关注'), (21, '次级'), (31, '可疑'), (41, '损失'))
    classification = models.IntegerField(verbose_name='_风险分类', choices=CLASSIFICATION_LIST, default=1)
    article_provide_sum = models.FloatField(verbose_name='_放款金额', default=0)
    article_repayment_sum = models.FloatField(verbose_name='_还款金额', default=0)
    article_buildor = models.ForeignKey(to='Employees', verbose_name="_创建者",
                                        on_delete=models.PROTECT, default=1,
                                        related_name='article_buildor_employee')
    build_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目'  # 指定显示名称
        db_table = 'dbms_articles'  # 指定数据表的名称

    def __str__(self):
        return '%s' % (self.article_num)


# -----------------------------风控反馈------------------------------#
class Feedback(models.Model):
    article = models.ForeignKey(to='Articles', verbose_name="项目",
                                on_delete=models.PROTECT,
                                related_name='feedback_article')
    PROPOSE_LIST = ((1, '符合上会条件'), (11, '暂不符合上会条件'), (21, '建议终止项目'))
    propose = models.IntegerField(verbose_name='上会建议', choices=PROPOSE_LIST)
    analysis = models.TextField(verbose_name='风险分析')
    suggestion = models.TextField(verbose_name='风控意见')
    feedback_buildor = models.ForeignKey(to='Employees', verbose_name="创建者",
                                         on_delete=models.PROTECT,
                                         related_name='feedback_buildor_employee')
    feedback_date = models.DateField(verbose_name='提交日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目-反馈'  # 指定显示名称
        db_table = 'dbms_feedback'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.article, self.propose)


# -----------------------------项目变更------------------------------#
class ArticleChange(models.Model):
    article = models.ForeignKey(to='Articles', verbose_name="项目",
                                on_delete=models.PROTECT,
                                related_name='change_article')
    CHANGE_VIEW_LIST = ((1, '变更申请'), (11, '同意变更'), (21, '否决变更'))
    change_view = models.IntegerField(verbose_name='变更意见', choices=CHANGE_VIEW_LIST, default=1)
    change_detail = models.TextField(verbose_name='签批详情')
    change_date = models.DateField(verbose_name='变更日期')
    change_buildor = models.ForeignKey(to='Employees', verbose_name="创建者",
                                       on_delete=models.PROTECT,
                                       related_name='change_buildor_employee')
    build_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '项目-变更'  # 指定显示名称
        db_table = 'dbms_articlechange'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s' % (self.article, self.change_view)


'''
 手动创建第三张表并关联
    expert = models.ManyToManyField(
        to='Expert',
        through='ArticlesToExpert',
        through_fields=['article', 'expert'],
        verbose_name="评审",
        related_name='article_expert')
    add,set的方法不能用了。


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
