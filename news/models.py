from django.db import models
from django.utils import timezone


class Admin(models.Model):
    """管理员表"""
    username = models.CharField(max_length=50, unique=True, verbose_name="登录账号")
    password = models.CharField(max_length=128, verbose_name="登录密码")

    class Meta:
        db_table = "admin"
        verbose_name = "管理员"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class NewsType(models.Model):
    """新闻栏目表"""
    type_name = models.CharField(max_length=50, unique=True, verbose_name="栏目名称")

    class Meta:
        db_table = "news_type"
        verbose_name = "新闻栏目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.type_name


class News(models.Model):
    """新闻公告表"""
    title = models.CharField(max_length=200, verbose_name="公告标题")
    content = models.TextField(blank=True, default="", verbose_name="公告内容")
    author = models.CharField(max_length=50, blank=True, default="", verbose_name="发布人")
    publish_time = models.DateTimeField(default=timezone.now, verbose_name="发布时间")
    news_type = models.ForeignKey(
        NewsType,
        on_delete=models.RESTRICT,
        db_column="type_id",
        verbose_name="所属栏目",
        related_name="news_list",
    )

    class Meta:
        db_table = "news"
        verbose_name = "新闻公告"
        verbose_name_plural = verbose_name
        ordering = ["-publish_time"]

    def __str__(self):
        return self.title
