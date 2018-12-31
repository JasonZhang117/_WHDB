from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)


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
        error_messages={
            'unique': ("email already exists.")}, )
    num = models.CharField(max_length=64, verbose_name="代码")
    name = models.CharField(max_length=64, verbose_name="姓名")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)
    job = models.ManyToManyField("Jobs", blank=True, null=True)
    department = models.ForeignKey(to="Departments",
                                   verbose_name="部门",
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
        return '%s(%s)' % (self.name, self.email)

    class Meta:
        verbose_name_plural = '内部-员工'  # 指定显示名称
        db_table = 'dbms_employees'  # 指定数据表的名称
        permissions = (
            ('dbms_article_list',
             '访问项目列表'),
            ('dbms_article_list_all',
             '访问所有项目列表'),
            ('dbms_article_add_view',
             '访问项目添加页'),
            ('dbms_article_add_change',
             '添加项目'),
            ('crm_table_list',
             '可以查看kingadmin每张表里所有的数据'),
            ('crm_table_list_view',
             '可以访问kingadmin表里每条数据的修改页'),
            ('crm_table_list_change',
             '可以对kingadmin表里的每条数据进行修改'),
            ('crm_table_obj_add_view',
             '可以访问kingadmin每张表的数据增加页'),
            ('crm_table_obj_add',
             '可以对kingadmin每张表进行数据添加'),)


# -----------------------------岗位模型------------------------------#
class Jobs(models.Model):  # 岗位（角色）
    name = models.CharField(verbose_name='岗位名称', max_length=16, unique=True)
    menu = models.ManyToManyField(to="Menus",
                                  verbose_name="菜单",
                                  blank=True)

    class Meta:
        verbose_name_plural = '内部-岗位'  # 指定显示名称
        db_table = 'dbms_jobs'  # 指定数据表的名称

    def __str__(self):
        return self.name


# -----------------------------菜单模型------------------------------#
class Menus(models.Model):
    """动态菜单"""
    name = models.CharField(max_length=64)
    url_name = models.CharField(max_length=128)
    ordery = models.IntegerField()

    class Meta:
        verbose_name_plural = '内部-动态菜单'
        db_table = 'dbms_menus'
        unique_together = ('name', 'url_name')

    def __str__(self):
        return self.name
