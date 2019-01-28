from django.db import models
import datetime


# -----------------------客户模型-------------------------#
class Customes(models.Model):  # 客户
    name = models.CharField(verbose_name='客户名称', max_length=32, unique=True)
    short_name = models.CharField(verbose_name='客户简称', max_length=16, unique=True)
    GENRE_LIST = ((1, '企业'), (2, '个人'))
    genre = models.IntegerField(verbose_name='客户类型', choices=GENRE_LIST, default=1)
    contact_addr = models.CharField(verbose_name='联系地址', max_length=64)
    linkman = models.CharField(verbose_name='联系人', max_length=16)
    contact_num = models.CharField(verbose_name='联系电话', max_length=13)
    counter_only = models.BooleanField(verbose_name='仅反担保', default=1)

    lately_date = models.DateField(verbose_name='最近调查', null=True, blank=True)

    credit_amount = models.FloatField(verbose_name='_授信总额', default=0)
    custom_flow = models.FloatField(verbose_name='_流贷余额', default=0)
    custom_accept = models.FloatField(verbose_name='_承兑余额', default=0)
    custom_back = models.FloatField(verbose_name='_保函余额', default=0)
    custom_buildor = models.ForeignKey(to='Employees', verbose_name="_创建者",
                                       on_delete=models.PROTECT, default=1,
                                       related_name='custom_buildor_employee')
    custom_date = models.DateField(verbose_name='创建日期', default=datetime.date.today)

    # Cancellation = models.BooleanField('注销', default=False)

    class Meta:
        verbose_name_plural = '客户'  # 指定显示名称
        db_table = 'dbms_customes'  # 指定数据表的名称

    def __str__(self):
        return self.name


# -----------------------企业客户-------------------------#
class CustomesC(models.Model):
    custome = models.OneToOneField(to='Customes', verbose_name="企业客户",
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'genre': 1},
                                   related_name='company_custome')
    idustry = models.ForeignKey(to='Industries', verbose_name="所属行业",
                                on_delete=models.PROTECT,
                                related_name='custome_idustry')
    district = models.ForeignKey(to='Districtes', verbose_name="所属区域",
                                 on_delete=models.PROTECT,
                                 related_name='custome_district')
    capital = models.FloatField(verbose_name='注册资本')
    registered_addr = models.CharField(verbose_name='注册地址', max_length=64)
    representative = models.CharField(verbose_name='法人代表', max_length=16)

    class Meta:
        verbose_name_plural = '客户-企业'  # 指定显示名称
        db_table = 'dbms_customesc'  # 指定数据表的名称

    def __str__(self):
        return '%s' % (self.custome)


# -----------------------股东信息-------------------------#
class Shareholders(models.Model):
    custom = models.ForeignKey(to='CustomesC', verbose_name="企业客户",
                               on_delete=models.CASCADE,
                               related_name='shareholder_custom_c')
    shareholder_name = models.CharField(verbose_name='简称', max_length=32)
    invested_amount = models.FloatField(verbose_name='投资额')
    shareholding_ratio = models.FloatField(verbose_name='持股比例（%）')
    shareholderor = models.ForeignKey(to='Employees', verbose_name="创建者",
                                      on_delete=models.PROTECT, default=1,
                                      related_name='shareholderor_employee')
    shareholder_date = models.DateField(verbose_name='创建时间', default=datetime.date.today)

    class Meta:
        verbose_name_plural = '客户-股东信息'  # 指定显示名称
        db_table = 'dbms_shareholders'  # 指定数据表的名称
        unique_together = ['custom', 'shareholder_name']

    def __str__(self):
        return '%s-%s' % (self.custom, self.shareholder_name)


# -----------------------个人客户-------------------------#
class CustomesP(models.Model):  # 个人客户
    custome = models.OneToOneField(to='Customes', verbose_name="个人客户",
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'genre': 2},
                                   related_name='person_custome')
    spouse = models.OneToOneField(to='self', verbose_name='配偶',
                                  on_delete=models.CASCADE,
                                  null=True, blank=True)
    license_num = models.CharField(verbose_name='身份证号码', max_length=18, unique=True)
    license_addr = models.CharField(verbose_name='身份证地址', max_length=64)

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

    def __str__(self):
        return self.name


# -----------------------行业模型-------------------------#
class Industries(models.Model):  # 行业
    code = models.CharField(verbose_name='行业编码', max_length=16, unique=True)
    name = models.CharField(verbose_name='行业名称', max_length=32, unique=True)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '客户-行业'  # 指定显示名称
        db_table = 'dbms_industriess'  # 指定数据表的名称

    def __str__(self):
        return self.name
