from django.db import models


# -----------------------委托合同模型-------------------------#
class Agrees(models.Model):  # 委托合同
    agree_num = models.CharField(
        verbose_name='_合同编号',
        max_length=32,
        unique=True)
    article = models.ForeignKey(
        to='Articles',
        verbose_name="纪要",
        on_delete=models.PROTECT,
        related_name='agree_article')
    branch = models.ForeignKey(
        to='Branches',
        verbose_name="放款银行",
        on_delete=models.PROTECT,
        related_name='agree_branch')
    AGREE_TYP_LIST = ((1, '单笔'),
                      (2, '最高额'))
    agree_typ = models.IntegerField(
        verbose_name='合同种类',
        choices=AGREE_TYP_LIST,
        default=1)
    agree_amount = models.FloatField(
        verbose_name='合同金额')
    AGREE_STATE_LIST = ((1, '未签订'),
                        (2, '已签订'),
                        (3, '已落实'),
                        (4, '已作废'))
    agree_state = models.IntegerField(
        verbose_name='_合同状态',
        choices=AGREE_STATE_LIST,
        default=1)
    agree_balance = models.FloatField(
        verbose_name='_放款余额',
        default=0)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '合同-委托保证'  # 指定显示名称
        db_table = 'dbms_agrees'  # 指定数据表的名称

    def __str__(self):
        return "%s-%s" % (self.article.article_num,
                          self.agree_num)


# -----------------------反担保合同模型-------------------------#
class Counters(models.Model):  # 反担保合同
    counter_num = models.CharField(
        verbose_name='_合同编号',
        max_length=32,
        unique=True)
    agree = models.ForeignKey(
        to='Agrees',
        verbose_name="委托保证合同",
        on_delete=models.PROTECT,
        related_name='counter_agree')
    COUNTER_TYP_LIST = ((1, '企业担保'),
                        (2, '个人担保'),
                        (3, '房产抵押'),
                        (4, '土地抵押'),
                        (5, '应收质押'),
                        (6, '动产抵押'),
                        (7, '车辆抵押'))
    counter_typ = models.IntegerField(
        verbose_name='合同类型',
        choices=COUNTER_TYP_LIST,
        default=1)
    COUNTER_STATE_LIST = ((1, '未签订'),
                          (2, '已签订'),
                          (3, '已注销'))
    counter_state = models.IntegerField(
        verbose_name='_签订情况',
        choices=COUNTER_STATE_LIST,
        default=1)

    class Meta:
        verbose_name_plural = '合同-反担保'  # 指定显示名称
        db_table = 'dbms_counters'  # 指定数据表的名称

    def __str__(self):
        return self.counter_num


# ---------------------保证反担保合同模型-----------------------#
class CountersAssure(models.Model):  # 保证反担保合同
    counter = models.OneToOneField(
        to='Counters',
        verbose_name="反担保合同",
        on_delete=models.PROTECT,
        related_name='assure_counter')
    custome = models.ManyToManyField(
        to='Customes',
        verbose_name="反担保人",
        related_name='assure_custome')

    class Meta:
        verbose_name_plural = '合同-保证反担保'  # 指定显示名称
        db_table = 'dbms_countersassure'  # 指定数据表的名称

    def __str__(self):
        return self.counter.counter_num


# -------------------房产抵押反担保合同模型--------------------#
class CountersHouse(models.Model):  # 房产抵押反担保合同
    counter = models.OneToOneField(
        to='Counters',
        verbose_name="反担保合同",
        on_delete=models.PROTECT,
        related_name='house_counter')
    house = models.ManyToManyField(
        to='Houses',
        verbose_name="抵押物",
        related_name='house_house')

    class Meta:
        verbose_name_plural = '合同-房产抵押'  # 指定显示名称
        db_table = 'dbms_countershouse'  # 指定数据表的名称

    def __str__(self):
        return self.counter.counter_num
