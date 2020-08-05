from django.db import models
import datetime
from _WHDB.views import (FICATION_LIST)


def limit_managementor_choices():

    return {'job__name': '项目经理'}


def limit_controler_choices():

    return {'job__name': '风控专员'}


# -----------------------客户模型-------------------------#
class Customes(models.Model):  # 客户
    name = models.CharField(verbose_name='客户名称', max_length=32)
    short_name = models.CharField(verbose_name='客户简称',
                                  max_length=16,
                                  unique=True)
    GENRE_LIST = [(1, '企业用户'), (2, '个人用户')]
    genre = models.IntegerField(verbose_name='客户类型',
                                choices=GENRE_LIST,
                                default=1)
    CUSTOM_TYP = ((1, '--'), (11, '新增'), (21, '存量'), (31, '存量新增'))
    custom_typ = models.IntegerField(verbose_name='新增标志',
                                     choices=CUSTOM_TYP,
                                     default=1)
    contact_addr = models.CharField(verbose_name='联系地址', max_length=64)
    linkman = models.CharField(verbose_name='联系人', max_length=64)
    contact_num = models.CharField(verbose_name='联系电话', max_length=32)
    idustry = models.ForeignKey(
        to='Industries',
        verbose_name="所属行业",
        on_delete=models.PROTECT,
        related_name='c_idustry',
    )
    district = models.ForeignKey(
        to='Districtes',
        verbose_name="所属区域",
        on_delete=models.PROTECT,
        related_name='c_district',
    )
    plan_date = models.DateField(verbose_name='台账日期', blank=True, null=True)
    review_plan_date = models.DateField(verbose_name='保后计划',
                                        blank=True,
                                        null=True)
    PLAN_STY_LIST = ((1, '现场检查'), (11, '电话回访'), (61, '补调替代'), (62, '尽调替代'),
                     (91, '无需保后'))
    plan_sty = models.IntegerField(verbose_name='计划方式',
                                   choices=PLAN_STY_LIST,
                                   blank=True,
                                   null=True)
    REVIEW_STATE_LIST = ((1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后'),
                         (91, '无需保后'))
    review_state = models.IntegerField(verbose_name='_保后状态',
                                       choices=REVIEW_STATE_LIST,
                                       default=21)
    review_date = models.DateField(verbose_name='保后日期', blank=True, null=True)
    review_amount = models.IntegerField(verbose_name='保后次数', default=0)
    add_amount = models.IntegerField(verbose_name='补调次数', default=0)

    book = models.TextField(verbose_name='专员台账', blank=True, null=True)
    analysis = models.TextField(verbose_name='风险分析', blank=True, null=True)
    suggestion = models.TextField(verbose_name='风控建议', blank=True, null=True)
    classification = models.IntegerField(verbose_name='五级分类',
                                         choices=FICATION_LIST,
                                         default=11)
    provide_date = models.DateField(verbose_name='最近放款', null=True, blank=True)
    # 含上会，放款，补调，保后
    lately_date = models.DateField(verbose_name='最近更新', null=True, blank=True)
    day_space = models.IntegerField(verbose_name='间隔（日）', default=0)
    CUSTOM_DUN_LIST = ((1, '正常'), (11, '被告'), (99, '注销'))
    custom_dun_state = models.IntegerField(verbose_name='_风险分类',
                                           choices=CUSTOM_DUN_LIST,
                                           default=11)

    credit_amount = models.FloatField(verbose_name='授信总额', default=0)
    custom_flow = models.FloatField(verbose_name='_流贷余额', default=0)
    custom_accept = models.FloatField(verbose_name='_承兑余额', default=0)
    custom_back = models.FloatField(verbose_name='_保函余额', default=0)
    entrusted_loan = models.FloatField(verbose_name='_委贷余额', default=0)
    petty_loan = models.FloatField(verbose_name='小贷', default=0)
    amount = models.FloatField(verbose_name='_在保总额', default=0)

    g_value = models.FloatField(verbose_name='反担保价值', default=0)
    g_radio = models.FloatField(verbose_name='授信覆盖率(%)', default=0)

    v_radio = models.FloatField(verbose_name='在保覆盖率(%)', default=0)

    CUSTOM_STATE_LIST = ((11, '正常客户'), (21, '反担保客户'), (31, '小贷客户'), (99,
                                                                     '注销客户'))
    custom_state = models.IntegerField(verbose_name='客户状态',
                                       choices=CUSTOM_STATE_LIST,
                                       default=11)
    SUBMISSION_STATUS_LIST = ((11, '未报送'), (21, '更新待报'), (31, '已报送'))
    submission_status = models.IntegerField(verbose_name='客户状态',
                                            choices=SUBMISSION_STATUS_LIST,
                                            default=11)
    managementor = models.ForeignKey(to='Employees',
                                     verbose_name="管护经理",
                                     on_delete=models.PROTECT,
                                     default=1,
                                     limit_choices_to={'job__name': '项目经理'},
                                     related_name='manage_employee')
    controler = models.ForeignKey(to='Employees',
                                  verbose_name="风控专员",
                                  on_delete=models.PROTECT,
                                  default=1,
                                  limit_choices_to={'job__name': '风控专员'},
                                  related_name='controler_employee')
    custom_buildor = models.ForeignKey(to='Employees',
                                       verbose_name="_创建者",
                                       on_delete=models.PROTECT,
                                       default=1,
                                       related_name='custom_buildor_employee')
    custom_date = models.DateField(verbose_name='创建日期',
                                   default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)

    class Meta:
        verbose_name_plural = '客户'  # 指定显示名称
        db_table = 'dbms_customes'  # 指定数据表的名称
        ordering = ['genre', 'name']

    def __str__(self):
        return self.name


# -----------------------企业客户-------------------------#
class CustomesC(models.Model):
    custome = models.OneToOneField(to='Customes',
                                   verbose_name="企业客户",
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'genre': 1},
                                   related_name='company_custome')
    DECISIONOR_LIST = ((11, '股东会'), (13, '合伙人会议'), (15, '举办者会议'), (21, '董事会'),
                       (23, '管理委员会'))
    decisionor = models.IntegerField(verbose_name='决策机构',
                                     choices=DECISIONOR_LIST,
                                     default=11)
    credit_code = models.CharField(verbose_name='统一社会信用代码',
                                   max_length=32,
                                   null=True,
                                   blank=True)
    NATURE_LIST = ((11, '国有独资'), (21, '国有控股'), (31, '国有参股'), (41, '民营'),
                   (51, '外资'), (61, '港澳台商独资'), (71, '其他'))
    custom_nature = models.IntegerField(verbose_name='企业性质',
                                        choices=NATURE_LIST,
                                        default=41)
    INDUSTRY_C_LIST = (
        (101, '农林牧渔'),
        (102, '工业'),
        (103, '建筑业'),
        (104, '批发业'),
        (106, '零售业'),
        (107, '交通运输业'),
        (108, '仓储业'),
        (109, '邮政业'),
        (110, '住宿业'),
        (111, '餐饮业'),
        (112, '信息传输业'),
        (113, '软件和信息技术服务业'),
        (114, '房地产开发经营'),
        (115, '物业管理'),
        (116, '租赁和商务服务'),
        (199, '其他未列明行业'),
    )
    industry_c = models.IntegerField(verbose_name='所属行业',
                                     choices=INDUSTRY_C_LIST,
                                     default=102)
    TYPING_LIST = ((11, '涉农小微企业'), (21, '非农小微企业'), (31, '中型企业'), (41, '大型企业'))
    typing = models.IntegerField(verbose_name='企业划型',
                                 choices=TYPING_LIST,
                                 default=21)
    capital = models.FloatField(verbose_name='注册资本', default=0)
    paid_capital = models.FloatField(verbose_name='实收资本', default=0)
    registered_addr = models.CharField(verbose_name='注册地址', max_length=64)
    representative = models.CharField(verbose_name='法人代表', max_length=16)

    class Meta:
        verbose_name_plural = '客户-企业'  # 指定显示名称
        db_table = 'dbms_customesc'  # 指定数据表的名称

    def __str__(self):
        return '%s' % (self.custome)


# -----------------------股东信息-------------------------#
class Shareholders(models.Model):
    custom = models.ForeignKey(to='CustomesC',
                               verbose_name="企业客户",
                               on_delete=models.CASCADE,
                               related_name='shareholder_custom_c')
    shareholder_name = models.CharField(verbose_name='股东名称', max_length=32)
    invested_amount = models.FloatField(verbose_name='投资额')
    shareholding_ratio = models.FloatField(verbose_name='持股比例（%）')
    shareholderor = models.ForeignKey(to='Employees',
                                      verbose_name="创建者",
                                      on_delete=models.PROTECT,
                                      default=1,
                                      related_name='shareholderor_employee')
    shareholder_date = models.DateField(verbose_name='创建时间',
                                        default=datetime.date.today)

    class Meta:
        verbose_name_plural = '客户-股东信息'  # 指定显示名称
        db_table = 'dbms_shareholders'  # 指定数据表的名称
        unique_together = ['custom', 'shareholder_name']
        ordering = [
            '-shareholding_ratio',
        ]

    def __str__(self):
        return '%s-%s' % (self.custom, self.shareholder_name)


# -----------------------董事信息-------------------------#
class Trustee(models.Model):
    custom = models.ForeignKey(to='CustomesC',
                               verbose_name="企业客户",
                               on_delete=models.CASCADE,
                               related_name='trustee_custom_c')
    trustee_name = models.CharField(verbose_name='董事姓名',
                                    unique=True,
                                    max_length=32)
    trusteeor = models.ForeignKey(to='Employees',
                                  verbose_name="创建者",
                                  on_delete=models.PROTECT,
                                  related_name='trusteeor_employee')
    trusteeor_date = models.DateField(verbose_name='创建时间',
                                      default=datetime.date.today)

    class Meta:
        verbose_name_plural = '客户-董事信息'  # 指定显示名称
        db_table = 'dbms_trustee'  # 指定数据表的名称
        unique_together = ['custom', 'trustee_name']

    def __str__(self):
        return '%s-%s' % (self.custom, self.trustee_name)


# -----------------------个人客户-------------------------#
class CustomesP(models.Model):  # 个人客户
    custome = models.OneToOneField(to='Customes',
                                   verbose_name="个人客户",
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'genre': 2},
                                   related_name='person_custome')
    spouses = models.OneToOneField(to='Customes',
                                   verbose_name='配偶',
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'genre': 2},
                                   related_name='spouses_custom',
                                   null=True,
                                   blank=True)
    license_num = models.CharField(verbose_name='身份证号码',
                                   max_length=18,
                                   unique=True)
    license_addr = models.CharField(verbose_name='身份证地址', max_length=64)
    MARITAL_STATUS = (
        (1, '未婚'),
        (11, '已婚'),
        (21, '离异'),
        (41, '丧偶'),
        (99, '------'),
    )
    marital_status = models.IntegerField(verbose_name='婚姻状况',
                                         choices=MARITAL_STATUS,
                                         default=1)
    HOUSEHOLD_LIST = (
        (1, '城镇居民（含个体工商户）'),
        (11, '农村居民（含个体工商户）'),
    )
    household_nature = models.IntegerField(verbose_name='户籍性质',
                                           choices=HOUSEHOLD_LIST,
                                           default=1)

    class Meta:
        verbose_name_plural = '客户-个人'  # 指定显示名称
        db_table = 'dbms_customesp'  # 指定数据表的名称

    def __str__(self):
        return '%s(%s)' % (self.custome, self.license_num)


# -------------------区域（街道）-------------------------#
class Districtes(models.Model):  # 区域（街道）
    name = models.CharField(verbose_name='街道名称', max_length=16, unique=True)

    class Meta:
        verbose_name_plural = '客户-区域'  # 指定显示名称
        db_table = 'dbms_districtes'  # 指定数据表的名称
        ordering = [
            'name',
        ]

    def __str__(self):
        return self.name


# -----------------------行业模型-------------------------#
class Industries(models.Model):  # 行业
    code = models.CharField(verbose_name='行业编码', max_length=16, unique=True)
    name = models.CharField(verbose_name='行业名称', max_length=32, unique=True)
    IND_TYP_LIST = (
        (1, '未分产业'),
        (11, '第一产业'),
        (21, '第二产业'),
        (31, '第三产业'),
    )
    ind_typ = models.IntegerField(verbose_name='产业分类',
                                  choices=IND_TYP_LIST,
                                  default=1)
    cod_nam = models.CharField(verbose_name='代码名称', max_length=48)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '客户-行业'  # 指定显示名称
        db_table = 'dbms_industriess'  # 指定数据表的名称
        ordering = [
            'code',
        ]

    def __str__(self):
        return self.name
