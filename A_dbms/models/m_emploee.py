from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin, Group)


# -----------------------------岗位模型------------------------------#
class EmployeesManager(BaseUserManager):
    def create_user(self, email, name, num, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('用户必须是email地址')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            num=num, )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, num, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            name=name,
            num=num,
            password=password, )
        user.is_superuser = True
        user.save(using=self._db)
        return user


# -----------------------------员工模型------------------------------#
class Employees(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=150, verbose_name='电子邮箱', unique=True,
        error_messages={'unique': "E-mail已经存在！"}, )
    num = models.CharField(max_length=64, verbose_name="代码")
    name = models.CharField(max_length=64, verbose_name="姓名")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)
    EMPLOYEE_STATUS_LIST = [(1, '在职'), (11, '离职')]
    employee_status = models.IntegerField(verbose_name='_员工状态', choices=EMPLOYEE_STATUS_LIST, default=1)
    job = models.ManyToManyField("Jobs", blank=True, null=True)
    department = models.ForeignKey(to="Departments", verbose_name="部门",
                                   on_delete=models.PROTECT,
                                   related_name='employee_department',
                                   blank=True, null=True)
    objects = EmployeesManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'num']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return '%s' % self.name

    class Meta:
        verbose_name_plural = '内部-员工'  # 指定显示名称
        db_table = 'dbms_employees'  # 指定数据表的名称
        ordering = ['name', ]
        permissions = [
            ('dbms_article_all', '访问项目列表'),
            ('dbms_article', '访问所有项目列表'),
            ('article_scan_all', '访问项目添加页'),
            ('article_scan_agree', '添加项目'), ]


# -----------------------------岗位（角色）模型------------------------------#
class Jobs(models.Model):  # 岗位（角色）
    name = models.CharField(verbose_name='岗位名称', max_length=16, unique=True)
    authority = models.ManyToManyField(to="Authorities", verbose_name="权限", null=True, blank=True)

    class Meta:
        verbose_name_plural = '内部-岗位'  # 指定显示名称
        db_table = 'dbms_jobs'  # 指定数据表的名称
        ordering = ['name', ]

    def __str__(self):
        return self.name


# -----------------------------菜单模型------------------------------#
class Cartes(models.Model):
    """动态菜单"""
    caption = models.CharField(verbose_name="菜单名称", max_length=64, unique=True)
    # url_name = models.CharField(verbose_name="URL", max_length=128, null=True, blank=True)
    parent = models.ForeignKey(to="self", verbose_name="母菜单",
                               on_delete=models.PROTECT,
                               related_name='carte_parent',
                               blank=True, null=True)
    ordery = models.IntegerField(verbose_name="优先级")

    class Meta:
        verbose_name_plural = '内部-菜单'
        db_table = 'dbms_cartes'
        # unique_together = ('name', 'url_name')
        ordering = ['ordery', ]

    def __str__(self):
        return '%s-%s' % (self.caption, self.ordery)


# -----------------------------权限模型------------------------------#
class Authorities(models.Model):
    """权限"""
    name = models.CharField(verbose_name="权限名称", max_length=64)
    url = models.CharField(verbose_name="URL", max_length=128, blank=True, null=True)
    url_name = models.CharField(verbose_name="URL_NAME", max_length=128, unique=True)
    carte = models.ForeignKey(to="Cartes", verbose_name="菜单",
                              on_delete=models.PROTECT,
                              related_name='authority_carte',
                              blank=True, null=True)
    ordery = models.IntegerField(verbose_name="优先级", blank=True, null=True)

    class Meta:
        verbose_name_plural = '内部-权限'
        db_table = 'dbms_authorities'
        unique_together = ('name', 'url_name')
        ordering = ['name', ]

    def __str__(self):
        return '%s-%s' % (self.name, self.url_name)
