from django.db import models
import datetime


# 担保物信息
# ------------------------担保物--------------------------#
class Warrants(models.Model):  # 担保物
    warrant_num = models.CharField(verbose_name='权证编码', max_length=32, unique=True)
    WARRANT_TYP_LIST = [
        (1, '房产'), (2, '土地'), (3, '应收'), (4, '股权'),
        (5, '票据'), (6, '车辆'), (7, '其他'), (9, '他权')]
    '''其他-存货、设备、合格证、'''
    warrant_typ = models.IntegerField(verbose_name='权证类型', choices=WARRANT_TYP_LIST, default=1)
    evaluate_value = models.FloatField(verbose_name='评估价值', null=True, blank=True)
    evaluate_date = models.DateField(verbose_name='评估日期', null=True, blank=True)
    WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (3, '已出库'),
        (4, '已借出'), (5, '已注销'))
    warrant_state = models.IntegerField(verbose_name='_权证状态', choices=WARRANT_STATE_LIST, default=1)

    class Meta:
        verbose_name_plural = '权证-权证'  # 指定显示名称
        db_table = 'dbms_warrants'  # 指定数据表的名称

    def __str__(self):
        return self.warrant_num


# ------------------------产权证--------------------------#
class Ownership(models.Model):  # 产权证
    ownership_num = models.CharField(verbose_name='产权证编号', max_length=32, unique=True)
    warrant = models.ForeignKey(to='Warrants',
                                verbose_name="权证",
                                on_delete=models.CASCADE,
                                related_name='ownership_warrant')
    owner = models.ForeignKey(to='Customes',
                              verbose_name="所有权人",
                              on_delete=models.PROTECT,
                              related_name='owner_custome')

    class Meta:
        verbose_name_plural = '权证-产权证'  # 指定显示名称
        db_table = 'dbms_ownership'  # 指定数据表的名称
        unique_together = [('warrant', 'owner'), ]

    def __str__(self):
        return '%s-%s-%s' % (self.ownership_num, self.owner.name, self.warrant)


# -------------------------房产---------------------------#
class Houses(models.Model):  # 房产
    warrant = models.OneToOneField(to='Warrants',
                                   verbose_name="权证",
                                   on_delete=models.CASCADE,
                                   related_name='house_warrant')
    house_locate = models.CharField(verbose_name='房产坐落', max_length=64, unique=True)
    HOUSE_APP_LIST = ((1, '住宅'), (2, '商业'), (3, '办公'), (4, '公寓'), (5, '厂房'), (6, '科研'))
    house_app = models.IntegerField(verbose_name='房产用途', choices=HOUSE_APP_LIST, default=1)
    house_area = models.FloatField(verbose_name='建筑面积')

    class Meta:
        verbose_name_plural = '权证-房产'  # 指定显示名称
        db_table = 'dbms_houses'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s-%s' % (self.warrant, self.house_locate, self.house_area, self.house_app)


# ------------------------土地--------------------------#
class Grounds(models.Model):  # 土地
    warrant = models.OneToOneField(to='Warrants',
                                   verbose_name="权证",
                                   on_delete=models.CASCADE,
                                   related_name='ground_warrant')
    ground_locate = models.CharField(verbose_name='土地坐落', max_length=64)
    GROUND_APP_LIST = ((1, '住宅'), (2, '商住'), (3, '商服'), (4, '工业'))
    ground_app = models.IntegerField(verbose_name='土地用途', choices=GROUND_APP_LIST, default=1)
    ground_area = models.FloatField(verbose_name='土地面积')

    class Meta:
        verbose_name_plural = '权证-土地'  # 指定显示名称
        db_table = 'dbms_grounds'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s-%s' % (self.warrant, self.ground_locate, self.ground_area, self.ground_app)


# ------------------------股权--------------------------#
class Stockes(models.Model):  # 股权
    warrant = models.OneToOneField(to='Warrants',
                                   verbose_name="权证",
                                   on_delete=models.CASCADE,
                                   related_name='stock_warrant')
    STOCK_TYP_LIST = ((1, '有限公司股权'), (2, '股份公司股份'), (3, '举办者权益'))
    stock_typ = models.IntegerField(verbose_name='股权性质', choices=STOCK_TYP_LIST, default=1)
    stock_owner = models.ForeignKey(to='Customes',
                                    verbose_name="所有权人",
                                    on_delete=models.PROTECT,
                                    related_name='stock_owner_custome')
    target = models.CharField(verbose_name='标的公司', max_length=64)
    share = models.FloatField(verbose_name='数量（万元/万股）')

    class Meta:
        verbose_name_plural = '权证-股权'  # 指定显示名称
        db_table = 'dbms_stockes'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s-%s' % (self.warrant, self.stock_owner, self.target, self.share)


# ------------------------应收票据--------------------------#
class Draft(models.Model):  # 应收票据
    warrant = models.OneToOneField(to='Warrants',
                                   verbose_name="权证",
                                   on_delete=models.CASCADE,
                                   related_name='draft_warrant')
    owner = models.ForeignKey(to='Customes',
                              verbose_name="所有权人",
                              on_delete=models.PROTECT,
                              related_name='draft_custome')
    DRAFT_TYP_LIST = ((1, '银行承兑汇票'), (2, '商业承兑汇票'), (2, '支票'))
    draft_typ = models.IntegerField(verbose_name='票据种类', choices=DRAFT_TYP_LIST, default=1)

    detail = models.TextField(verbose_name="汇票描述")

    class Meta:
        verbose_name_plural = '权证-应收票据'  # 指定显示名称
        db_table = 'dbms_draft'  # 指定数据表的名称

    def __str__(self):
        return self.warrant


# ------------------------应收帐款--------------------------#
class Receivable(models.Model):  # 应收帐款
    warrant = models.OneToOneField(to='Warrants',
                                   verbose_name="权证",
                                   on_delete=models.CASCADE,
                                   related_name='receive_warrant')
    owner = models.ForeignKey(to='Customes',
                              verbose_name="所有权人",
                              on_delete=models.PROTECT,
                              related_name='receive_custome')
    detail = models.TextField(verbose_name="应收账款描述")

    class Meta:
        verbose_name_plural = '权证-应收账款'  # 指定显示名称
        db_table = 'dbms_receivable'  # 指定数据表的名称

    def __str__(self):
        return self.warrant


class ReceiveExtend(models.Model):  # 应收列表
    receivable = models.ForeignKey(to='Receivable',
                                   verbose_name="应收账款",
                                   on_delete=models.CASCADE,
                                   related_name='extend_receiveable')
    receive_unit = models.CharField(verbose_name="应收单位名称", max_length=64)


# ------------------------动产--------------------------#
class Chattel(models.Model):  # 动产
    warrant = models.OneToOneField(to='Warrants',
                                   verbose_name="权证",
                                   on_delete=models.CASCADE,
                                   related_name='chattel_warrant')
    owner = models.ForeignKey(to='Customes',
                              verbose_name="所有权人",
                              on_delete=models.PROTECT,
                              related_name='chattel_custome')
    CHATTEL_TYP_LIST = ((1, '存货'), (2, '设备'))
    chattel_typ = models.IntegerField(verbose_name='动产种类', choices=CHATTEL_TYP_LIST, default=1)
    detail = models.TextField(verbose_name="动产具体描述")

    class Meta:
        verbose_name_plural = '权证-动产'  # 指定显示名称
        db_table = 'dbms_rchattel'  # 指定数据表的名称

    def __str__(self):
        return self.warrant


# ------------------------车辆--------------------------#

class Vehicle(models.Model):  # 车辆
    warrant = models.OneToOneField(to='Warrants',
                                   verbose_name="权证",
                                   on_delete=models.CASCADE,
                                   related_name='vehicle_warrant')
    owner = models.ForeignKey(to='Customes',
                              verbose_name="所有权人",
                              on_delete=models.PROTECT,
                              related_name='vehicle_custome')
    frame_num = models.CharField(verbose_name="车架号", max_length=64, unique=True)
    plate_num = models.CharField(verbose_name="车牌号", max_length=64, unique=True)

    class Meta:
        verbose_name_plural = '权证-车辆'  # 指定显示名称
        db_table = 'dbms_vehicle'  # 指定数据表的名称

    def __str__(self):
        return self.warrant


# ------------------------他权模型--------------------------#
class Hypothecs(models.Model):  # 他权
    warrant = models.OneToOneField(to='Warrants',
                                   verbose_name="他权证",
                                   on_delete=models.CASCADE,
                                   related_name='ypothec_warrant')
    agree = models.ForeignKey(to='Agrees',
                              verbose_name="委托合同",
                              on_delete=models.PROTECT,
                              related_name='ypothec_agree')
    warrant_m = models.ManyToManyField(to='Warrants', verbose_name="权证", related_name='ypothec_m_agree')

    class Meta:
        verbose_name_plural = '权证-他权'  # 指定显示名称
        db_table = 'dbms_hypothecs'  # 指定数据表的名称

    def __str__(self):
        return self.warrant


# ------------------------出入库模型---------------------------#
class Storages(models.Model):  # 出入库
    warrant = models.ForeignKey(to='Warrants',
                                verbose_name="权证",
                                on_delete=models.PROTECT,
                                related_name='storage_warrant')
    STORAGE_TYP_LIST = ((1, '入库'), (2, '出库'), (3, '借出'), (4, '归还'), (5, '解保'))
    storage_typ = models.IntegerField(verbose_name='出入库', choices=STORAGE_TYP_LIST, default=1)
    storage_date = models.DateField(verbose_name='日期', default=datetime.date.today)
    transfer = models.ForeignKey(to='Employees',
                                 verbose_name="移交/接收者",
                                 on_delete=models.PROTECT,
                                 related_name='transfer_employee')
    conservator = models.ForeignKey(to='Employees',
                                    verbose_name="权证管理岗",
                                    on_delete=models.PROTECT,
                                    related_name='conservator_employee')

    class Meta:
        verbose_name_plural = '权证-出入库'  # 指定显示名称
        db_table = 'dbms_storages'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s' % (self.warrant, self.storage_date, self.storage_typ)


# ------------------------评估模型---------------------------#
class Evaluate(models.Model):  # 评估
    warrant = models.ForeignKey(to='Warrants',
                                verbose_name="权证",
                                on_delete=models.PROTECT,
                                related_name='evaluate_warrant')
    evaluate_value = models.FloatField(verbose_name='评估价值')
    evaluate_date = models.DateField(verbose_name='评估日期', default=datetime.date.today)
    evaluator = models.ForeignKey(to='Employees',
                                  verbose_name="创建者",
                                  on_delete=models.PROTECT,
                                  related_name='evaluator_employee')

    class Meta:
        verbose_name_plural = '权证-评估'  # 指定显示名称
        db_table = 'dbms_evaluate'  # 指定数据表的名称

    def __str__(self):
        return self.warrant
