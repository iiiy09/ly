from django.urls import path
from . import views

urlpatterns = [
    # 登录
    path("admin/login/", views.login_view, name="login"),
    path("admin/logout/", views.logout_view, name="logout"),

    # 栏目管理
    path("admin/type/", views.admin_type_list, name="admin_type_list"),
    path("admin/type/add/", views.admin_type_add, name="admin_type_add"),
    path("admin/type/<int:type_id>/edit/", views.admin_type_edit, name="admin_type_edit"),
    path("admin/type/<int:type_id>/delete/", views.admin_type_delete, name="admin_type_delete"),

    # 新闻公告管理
    path("admin/news/", views.admin_news_list, name="admin_news_list"),
    path("admin/news/add/", views.admin_news_add, name="admin_news_add"),
    path("admin/news/<int:news_id>/edit/", views.admin_news_edit, name="admin_news_edit"),
    path("admin/news/<int:news_id>/delete/", views.admin_news_delete, name="admin_news_delete"),
    path("admin/news/batch-delete/", views.admin_news_batch_delete, name="admin_news_batch_delete"),

    # 前台浏览
    path("", views.front_index, name="front_index"),
    path("detail/<int:news_id>/", views.front_detail, name="front_detail"),
    path("front/", views.front_index, name="front_index_alt"),
    path("front/detail/<int:news_id>/", views.front_detail, name="front_detail_alt"),
]
