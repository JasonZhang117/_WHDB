from django.db import models


# 客户、企业客户、个人客户区域、行业
# -----------------------客户模型-------------------------#
class Customes(models.Model):  # 客户
    name = models.CharField(
        verbose_name='名称',
        max_length=32, unique=True)
    GENRE_LIST = ((1, '企业'), (2, '个人'))
    genre = models.IntegerField(
        verbose_name='客户类型',
        choices=GENRE_LIST,
        default=1)
    contact_addr = models.CharField(
        verbose_name='联系地址',
        max_length=64)
    linkman = models.CharField(
        verbose_name='联系人',
        max_length=16)
    contact_num = models.CharField(
        verbose_name='联系电话',
        max_length=13)
    credit_amount = models.FloatField(
        verbose_name='授信总额（元）',
        default=0)
    flow_loan = models.FloatField(
        verbose_name='流贷余额（元）',
        default=0)
    accept_loan = models.FloatField(
        verbose_name='承兑余额（元）',
        default=0)
    back_loan = models.FloatField(
        verbose_name='保函余额（元）',
        default=0)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '客户'  # 指定显示名称
        db_table = 'dbms_customes'  # 指定数据表的名称

    def __str__(self):
        return self.name


# -----------------------企业客户-------------------------#
class CustomesC(models.Model):
    custome = models.OneToOneField(
        to='Customes',
        verbose_name="企业客户",
        on_delete=models.PROTECT,
        related_name='company_custome')
    short_name = models.CharField(
        verbose_name='简称',
        max_length=8, unique=True)
    capital = models.FloatField(
        verbose_name='注册资本（股本）')
    registered_addr = models.CharField(
        verbose_name='注册地址',
        max_length=64)
    representative = models.CharField(
        verbose_name='法人代表',
        max_length=16)
    idustry = models.ForeignKey(
        to='Industries',
        verbose_name="所属行业",
        on_delete=models.PROTECT,
        related_name='custome_idustry')
    district = models.ForeignKey(
        to='Districtes',
        verbose_name="所属区域",
        on_delete=models.CASCADE,
        related_name='custome_district')

    class Meta:
        verbose_name_plural = '客户-企业'  # 指定显示名称
        db_table = 'dbms_customesc'  # 指定数据表的名称

    def __str__(self):
        return self.custome.name


# -----------------------个人客户-------------------------#
class CustomesP(models.Model):  # 个人客户
    custome = models.OneToOneField(
        to='Customes',
        verbose_name="个人客户",
        on_delete=models.PROTECT,
        related_name='person_custome')
    license_num = models.CharField(
        verbose_name='身份证号码',
        max_length=18,
        unique=True)
    registered_addr = models.CharField(
        verbose_name='身份证地址',
        max_length=64)

    class Meta:
        verbose_name_plural = '客户-个人'  # 指定显示名称
        db_table = 'dbms_customesp'  # 指定数据表的名称

    def __str__(self):
        return self.custome.name


# -------------------区域（街道）----------------------#
class Districtes(models.Model):  # 区域（街道）
    name = models.CharField(
        verbose_name='街道名称',
        max_length=16, unique=True)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '客户-区域'  # 指定显示名称
        db_table = 'dbms_districtes'  # 指定数据表的名称

    def __str__(self):
        return self.name


# -----------------------行业模型-------------------------#
class Industries(models.Model):  # 行业
    code = models.CharField(
        verbose_name='行业编码',
        max_length=16, unique=True)
    name = models.CharField(
        verbose_name='行业名称',
        max_length=32, unique=True)

    # Cancellation = models.BooleanField('注销', default=False)
    class Meta:
        verbose_name_plural = '客户-行业'  # 指定显示名称
        db_table = 'dbms_industriess'  # 指定数据表的名称

    def __str__(self):
        return self.name
