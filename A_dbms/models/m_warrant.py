from django.db import models
import datetime


# ------------------------担保物--------------------------#
class Warrants(models.Model):  # 担保物
    warrant_num = models.CharField(verbose_name='权证编码', max_length=128, unique=True)
    WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]
    '''其他-存货、设备、合格证、'''
    warrant_typ = models.IntegerField(verbose_name='权证类型', choices=WARRANT_TYP_LIST, default=1)

    EVALUATE_STATE_LIST = ((1, '机构评估'), (11, '机构预估'), (21, '综合询价'), (31, '购买成本'))
    evaluate_state = models.IntegerField(verbose_name='评估方式', choices=EVALUATE_STATE_LIST, null=True, blank=True)
    evaluate_value = models.FloatField(verbose_name='评估价值', null=True, blank=True)
    evaluate_date = models.DateField(verbose_name='评估日期', null=True, blank=True)
    evaluate_explain = models.CharField(verbose_name='评估说明', max_length=128, null=True, blank=True)

    WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'), (99, '已注销'))
    warrant_state = models.IntegerField(verbose_name='_权证状态', choices=WARRANT_STATE_LIST, default=1)
    storage_explain = models.CharField(verbose_name='出入库说明', max_length=128, blank=True, null=True)

    warrant_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                        on_delete=models.PROTECT,
                                        related_name='warrant_buildor_employee')
    warrant_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证'  # 指定显示名称
        db_table = 'dbms_warrants'  # 指定数据表的名称

    def __str__(self):
        return self.warrant_num


# ------------------------产权证--------------------------#
class Ownership(models.Model):  # 产权证
    ownership_num = models.CharField(verbose_name='产权证编号', max_length=32, unique=True)
    warrant = models.ForeignKey(to='Warrants', verbose_name="权证",
                                on_delete=models.PROTECT,
                                related_name='ownership_warrant')
    owner = models.ForeignKey(to='Customes', verbose_name="所有权人",
                              on_delete=models.PROTECT,
                              related_name='owner_custome')
    ownership_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                          on_delete=models.PROTECT,
                                          related_name='ownership_buildor_employee')
    ownership_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-产权证'  # 指定显示名称
        db_table = 'dbms_ownership'  # 指定数据表的名称
        unique_together = [('warrant', 'owner'), ]

    def __str__(self):
        return '%s-%s-%s' % (self.ownership_num, self.owner.name, self.warrant)


# -------------------------房产1---------------------------#
class Houses(models.Model):  # 房产
    ''' WARRANT_TYP_LIST = [
            (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
            (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    warrant = models.OneToOneField(to='Warrants', verbose_name="权证",
                                   on_delete=models.PROTECT,
                                   limit_choices_to={'warrant_typ': 1},
                                   related_name='house_warrant')
    house_locate = models.CharField(verbose_name='房产坐落', max_length=64, unique=True)
    HOUSE_APP_LIST = ((1, '住宅'), (11, '商业'), (21, '办公'), (31, '公寓'), (41, '生产性工业用房'), (51, '科研')
                      , (61, '车库'), (71, '仓储'), (99, '期房'))
    house_app = models.IntegerField(verbose_name='房产用途', choices=HOUSE_APP_LIST, default=1)
    house_area = models.FloatField(verbose_name='建筑面积')
    house_name = models.CharField(verbose_name='楼盘名称', max_length=64, null=True, blank=True)
    house_buildor = models.ForeignKey(to='Employees', verbose_name="创建者",
                                      on_delete=models.PROTECT,
                                      related_name='house_buildor_employee')
    house_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-房产'  # 指定显示名称
        db_table = 'dbms_houses'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s-%s' % (self.warrant, self.house_locate, self.house_area, self.house_app)


# ------------------------产权证--------------------------#
class HouseBag(models.Model):  # 产权证
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    warrant = models.ForeignKey(to='Warrants', verbose_name="权证",
                                on_delete=models.PROTECT,
                                limit_choices_to={'warrant_typ': 1},
                                related_name='housebag_warrant')
    housebag_locate = models.CharField(verbose_name='房产坐落', max_length=64, unique=True)
    HOUSEBAG_APP_LIST = ((1, '住宅'), (11, '商业'), (21, '办公'), (31, '公寓'), (41, '厂房'), (51, '科研'))
    housebag_app = models.IntegerField(verbose_name='房产用途', choices=HOUSEBAG_APP_LIST, default=1)
    housebag_area = models.FloatField(verbose_name='建筑面积')
    housebag_buildor = models.ForeignKey(to='Employees', verbose_name="创建者",
                                         on_delete=models.PROTECT,
                                         related_name='housebag_buildor_employee')
    housebag_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-房产包'  # 指定显示名称
        db_table = 'dbms_housebag'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s' % (self.warrant, self.housebag_locate)


# ------------------------土地2--------------------------#
class Grounds(models.Model):  # 土地
    ''' WARRANT_TYP_LIST = [
                (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
                (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    warrant = models.OneToOneField(to='Warrants', verbose_name="权证",
                                   on_delete=models.PROTECT,
                                   limit_choices_to={'warrant_typ': 5},
                                   related_name='ground_warrant')
    ground_locate = models.CharField(verbose_name='土地坐落', max_length=64)
    GROUND_APP_LIST = ((1, '住宅'), (5, '城镇混合住宅'), (11, '商住'), (21, '商服'), (31, '工业'))
    ground_app = models.IntegerField(verbose_name='土地用途', choices=GROUND_APP_LIST, default=1)
    ground_area = models.FloatField(verbose_name='土地面积')
    ground_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                       on_delete=models.PROTECT,
                                       related_name='ground_buildor_employee')
    ground_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-土地'  # 指定显示名称
        db_table = 'dbms_grounds'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s-%s' % (self.warrant, self.ground_locate, self.ground_area, self.ground_app)


# ------------------------应收帐款11--------------------------#
class Receivable(models.Model):  # 应收帐款
    warrant = models.OneToOneField(to='Warrants', verbose_name="权证",
                                   on_delete=models.PROTECT,
                                   limit_choices_to={'warrant_typ': 11},
                                   related_name='receive_warrant')
    receive_owner = models.ForeignKey(to='Customes', verbose_name="所有权人",
                                      on_delete=models.PROTECT,
                                      related_name='receive_custome')
    receivable_detail = models.TextField(verbose_name="应收账款描述")
    receivable_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                           on_delete=models.PROTECT,
                                           related_name='receivable_buildor_employee')
    receivable_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-应收账款'  # 指定显示名称
        db_table = 'dbms_receivable'  # 指定数据表的名称

    def __str__(self):
        return '%s' % (self.warrant)


class ReceiveExtend(models.Model):  # 应收列表
    receivable = models.ForeignKey(to='Receivable', verbose_name="应收账款",
                                   on_delete=models.PROTECT,
                                   related_name='extend_receiveable')
    receive_unit = models.CharField(verbose_name="应收单位名称", max_length=64)
    receiv_e_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                         on_delete=models.PROTECT,
                                         related_name='receiv_e_buildor_employee')
    receiv_e_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-应收明细'  # 指定显示名称
        db_table = 'dbms_receiveextend'  # 指定数据表的名称

    def __str__(self):
        return '%s' % self.receivable


# ------------------------股权21--------------------------#
class Stockes(models.Model):  # 股权
    warrant = models.OneToOneField(to='Warrants', verbose_name="权证",
                                   on_delete=models.PROTECT,
                                   limit_choices_to={'warrant_typ': 21},
                                   related_name='stock_warrant')
    STOCK_TYP_LIST = ((1, '有限公司股权'), (11, '股份公司股份'), (21, '举办者权益'))
    stock_typ = models.IntegerField(verbose_name='股权性质', choices=STOCK_TYP_LIST, default=1)
    stock_owner = models.ForeignKey(to='Customes', verbose_name="所有权人",
                                    on_delete=models.PROTECT,
                                    related_name='stock_owner_custome')
    target = models.CharField(verbose_name='标的公司', max_length=64)
    share = models.FloatField(verbose_name='数量（万元/万股）')
    stock_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                      on_delete=models.PROTECT,
                                      related_name='stock_buildor_employee')
    stock_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-股权'  # 指定显示名称
        db_table = 'dbms_stockes'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s-%s' % (self.warrant, self.stock_owner, self.target, self.share)


# ------------------------应收票据31--------------------------#
class Draft(models.Model):  # 应收票据
    warrant = models.OneToOneField(to='Warrants', verbose_name="权证",
                                   on_delete=models.PROTECT,
                                   limit_choices_to={'warrant_typ': 31},
                                   related_name='draft_warrant')
    draft_owner = models.ForeignKey(to='Customes', verbose_name="所有权人",
                                    on_delete=models.PROTECT,
                                    related_name='draft_custome')

    draft_detail = models.TextField(verbose_name="票据描述")
    draft_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                      on_delete=models.PROTECT,
                                      related_name='draft_buildor_employee')
    draft_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-应收票据'  # 指定显示名称
        db_table = 'dbms_draft'  # 指定数据表的名称

    def __str__(self):
        return '%s' % self.warrant,


class DraftExtend(models.Model):  # 票据列表
    draft = models.ForeignKey(to='Draft', verbose_name="票据",
                              on_delete=models.PROTECT,
                              related_name='extend_draft')
    DRAFT_TYP_LIST = ((1, '电子银行承兑汇票'), (2, '普通银行承兑汇票'), (11, '电子商业承兑汇票'),
                      (12, '普通商业承兑汇票'), (21, '支票'))
    draft_typ = models.IntegerField(verbose_name='票据种类', choices=DRAFT_TYP_LIST, default=1)
    draft_num = models.CharField(verbose_name="票据编号", max_length=64)
    draft_acceptor = models.CharField(verbose_name="承兑人", max_length=64)
    draft_amount = models.FloatField(verbose_name="票面金额")
    issue_date = models.DateField(verbose_name="出票日期")
    due_date = models.DateField(verbose_name="到期日")
    draft_e_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                        on_delete=models.PROTECT,
                                        related_name='draft_e_buildor_employee')
    draft_e_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-票据明细'  # 指定显示名称
        db_table = 'dbms_draftextend'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s' % (self.draft, self.draft_typ, self.draft_num)


# ------------------------车辆41--------------------------#
class Vehicle(models.Model):  # 车辆
    warrant = models.OneToOneField(to='Warrants', verbose_name="权证",
                                   on_delete=models.PROTECT,
                                   limit_choices_to={'warrant_typ': 41},
                                   related_name='vehicle_warrant')
    vehicle_owner = models.ForeignKey(to='Customes', verbose_name="所有权人",
                                      on_delete=models.PROTECT,
                                      related_name='vehicle_custome')
    frame_num = models.CharField(verbose_name="车架号", max_length=64, unique=True)
    plate_num = models.CharField(verbose_name="车牌号", max_length=64, unique=True)
    vehicle_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                        on_delete=models.PROTECT,
                                        related_name='vehicle_buildor_employee')
    vehicle_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-车辆'  # 指定显示名称
        db_table = 'dbms_vehicle'  # 指定数据表的名称

    def __str__(self):
        return '%s' % self.warrant


# ------------------------动产51--------------------------#
class Chattel(models.Model):  # 动产
    warrant = models.OneToOneField(to='Warrants', verbose_name="权证",
                                   on_delete=models.PROTECT,
                                   limit_choices_to={'warrant_typ': 51},
                                   related_name='chattel_warrant')
    chattel_owner = models.ForeignKey(to='Customes', verbose_name="所有权人",
                                      on_delete=models.PROTECT,
                                      related_name='chattel_custome')
    CHATTEL_TYP_LIST = ((1, '存货'), (11, '设备'))
    chattel_typ = models.IntegerField(verbose_name='动产种类', choices=CHATTEL_TYP_LIST, default=1)
    chattel_detail = models.TextField(verbose_name="动产具体描述")
    chattel_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                        on_delete=models.PROTECT,
                                        related_name='chattel_buildor_employee')
    chattel_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-动产'  # 指定显示名称
        db_table = 'dbms_rchattel'  # 指定数据表的名称

    def __str__(self):
        return '%s' % self.warrant


# ------------------------他权模型99--------------------------#
def limit_agree_choices():
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    return {'agree_state__in': [21, 31, 51]}


class Hypothecs(models.Model):  # 他权
    warrant = models.OneToOneField(to='Warrants', verbose_name="他权证",
                                   on_delete=models.PROTECT,
                                   limit_choices_to={'warrant_typ': 99},
                                   related_name='ypothec_warrant')
    agree = models.ForeignKey(to='Agrees', verbose_name="委托合同",
                              on_delete=models.PROTECT,
                              limit_choices_to=limit_agree_choices,
                              related_name='ypothec_agree')
    warrant_m = models.ManyToManyField(to='Warrants', verbose_name="权证", related_name='ypothec_m_agree')
    hypothec_buildor = models.ForeignKey(to='Employees', verbose_name="创建者", default=1,
                                         on_delete=models.PROTECT,
                                         related_name='hypothec_buildor_employee')
    hypothec_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-他权'  # 指定显示名称
        db_table = 'dbms_hypothecs'  # 指定数据表的名称

    def __str__(self):
        return '%s' % self.warrant


# ------------------------出入库模型---------------------------#
class Storages(models.Model):  # 出入库
    warrant = models.ForeignKey(to='Warrants', verbose_name="权证",
                                on_delete=models.PROTECT,
                                related_name='storage_warrant')
    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), 
        (31, '解保出库'), (99, '已注销'))'''
    STORAGE_TYP_LIST = ((1, '入库'), (2, '续抵出库'), (11, '借出'), (12, '归还'), (31, '解保出库'))
    storage_typ = models.IntegerField(verbose_name='出入库', choices=STORAGE_TYP_LIST, default=1)
    storage_explain = models.CharField(verbose_name='出入库说明', max_length=128, blank=True, null=True)

    transfer = models.ForeignKey(to='Employees', verbose_name="移交/接收者",
                                 on_delete=models.PROTECT,
                                 related_name='transfer_employee')
    conservator = models.ForeignKey(to='Employees', verbose_name="权证管理岗",
                                    on_delete=models.PROTECT,
                                    related_name='conservator_employee')
    storage_date = models.DateField(verbose_name='出入库日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-出入库'  # 指定显示名称
        db_table = 'dbms_storages'  # 指定数据表的名称

    def __str__(self):
        return '%s-%s-%s' % (self.warrant, self.storage_date, self.storage_typ)


# ------------------------评估模型---------------------------#
class Evaluate(models.Model):  # 评估
    warrant = models.ForeignKey(to='Warrants', verbose_name="权证",
                                on_delete=models.PROTECT,
                                related_name='evaluate_warrant')
    EVALUATE_STATE_LIST = ((1, '机构评估'), (11, '机构预估'), (21, '综合询价'), (31, '购买成本'))
    evaluate_state = models.IntegerField(verbose_name='评估方式', choices=EVALUATE_STATE_LIST, default=1)
    evaluate_value = models.FloatField(verbose_name='评估价值')
    evaluate_date = models.DateField(verbose_name='评估日期')
    evaluate_explain = models.CharField(verbose_name='评估说明', max_length=128, blank=True, null=True)
    evaluator = models.ForeignKey(to='Employees', verbose_name="创建者",
                                  on_delete=models.PROTECT,
                                  related_name='evaluator_employee')
    evaluator_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '权证-评估'  # 指定显示名称
        db_table = 'dbms_evaluate'  # 指定数据表的名称

    def __str__(self):
        return '%s_%s_%s' % (self.warrant, self.evaluate_state, self.evaluate_value)
