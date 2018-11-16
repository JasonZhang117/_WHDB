from django.db import models


# Create your models here.
class Text(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name_plural = '测试表'  # 指定显示名称
        db_table = 'web_text' #指定数据表的名称

    def __str__(self):
        return self.name
