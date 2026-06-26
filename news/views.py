import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Admin, NewsType, News


# ============================================================
# 登录认证装饰器
# ============================================================

def admin_required(view_func):
    """要求管理员登录的装饰器"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get("admin_id"):
            return redirect("/admin/login/")
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================
# 登录模块
# ============================================================

def login_view(request):
    """管理员登录"""
    if request.method == "GET":
        return render(request, "login.html")
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "").strip()
    if not username or not password:
        return render(request, "login.html", {"error": "账号和密码不能为空"})
    try:
        admin = Admin.objects.get(username=username, password=password)
        request.session["admin_id"] = admin.id
        request.session["admin_name"] = admin.username
        return redirect("/admin/type/")
    except Admin.DoesNotExist:
        return render(request, "login.html", {"error": "账号或密码错误"})


def logout_view(request):
    """退出登录"""
    request.session.flush()
    return redirect("/")


# ============================================================
# 后台 — 栏目分类管理
# ============================================================

@admin_required
def admin_type_list(request):
    """栏目列表页"""
    types = NewsType.objects.all()
    return render(request, "admin_type.html", {"types": types})


@admin_required
@require_http_methods(["POST"])
def admin_type_add(request):
    """新增栏目（JSON 接口）"""
    name = request.POST.get("type_name", "").strip()
    if not name:
        return JsonResponse({"ok": False, "msg": "栏目名称不能为空"})
    if NewsType.objects.filter(type_name=name).exists():
        return JsonResponse({"ok": False, "msg": "栏目名称已存在"})
    NewsType.objects.create(type_name=name)
    return JsonResponse({"ok": True})


@admin_required
@require_http_methods(["POST"])
def admin_type_edit(request, type_id):
    """修改栏目名称（JSON 接口）"""
    news_type = get_object_or_404(NewsType, id=type_id)
    name = request.POST.get("type_name", "").strip()
    if not name:
        return JsonResponse({"ok": False, "msg": "栏目名称不能为空"})
    if NewsType.objects.filter(type_name=name).exclude(id=type_id).exists():
        return JsonResponse({"ok": False, "msg": "栏目名称已存在"})
    news_type.type_name = name
    news_type.save()
    return JsonResponse({"ok": True})


@admin_required
@require_http_methods(["POST"])
def admin_type_delete(request, type_id):
    """删除栏目 — 有关联新闻时拒绝"""
    news_type = get_object_or_404(NewsType, id=type_id)
    if News.objects.filter(news_type=news_type).exists():
        return JsonResponse({"ok": False, "msg": "该栏目下存在新闻公告，无法删除"})
    news_type.delete()
    return JsonResponse({"ok": True})


# ============================================================
# 后台 — 新闻公告管理
# ============================================================

@admin_required
def admin_news_list(request):
    """新闻公告列表页（带搜索 + 筛选 + 分页）"""
    qs = News.objects.select_related("news_type").all()

    # 搜索 — 标题模糊匹配
    keyword = request.GET.get("q", "").strip()
    if keyword:
        qs = qs.filter(title__icontains=keyword)

    # 按栏目筛选
    type_id = request.GET.get("type_id", "").strip()
    if type_id:
        qs = qs.filter(news_type_id=int(type_id))

    # 按发布时间筛选
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    if date_from:
        qs = qs.filter(publish_time__gte=date_from)
    if date_to:
        qs = qs.filter(publish_time__lte=date_to + " 23:59:59")

    # 分页
    paginator = Paginator(qs, 10)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)

    types = NewsType.objects.all()
    return render(request, "admin_news.html", {
        "page_obj": page_obj,
        "types": types,
        "q": keyword,
        "type_id": type_id,
        "date_from": date_from,
        "date_to": date_to,
    })


@admin_required
@require_http_methods(["POST"])
def admin_news_add(request):
    """新增公告（JSON 接口）"""
    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"ok": False, "msg": "标题不能为空"})
    content = request.POST.get("content", "").strip()
    author = request.POST.get("author", "").strip()
    type_id = request.POST.get("type_id", "")
    if not type_id:
        return JsonResponse({"ok": False, "msg": "请选择所属栏目"})
    news_type = get_object_or_404(NewsType, id=int(type_id))
    News.objects.create(
        title=title,
        content=content,
        author=author,
        news_type=news_type,
        publish_time=timezone.now(),
    )
    return JsonResponse({"ok": True})


@admin_required
@require_http_methods(["POST"])
def admin_news_edit(request, news_id):
    """修改公告（JSON 接口）"""
    news = get_object_or_404(News, id=news_id)
    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"ok": False, "msg": "标题不能为空"})
    type_id = request.POST.get("type_id", "")
    if not type_id:
        return JsonResponse({"ok": False, "msg": "请选择所属栏目"})
    news.title = title
    news.content = request.POST.get("content", "").strip()
    news.author = request.POST.get("author", "").strip()
    news.news_type = get_object_or_404(NewsType, id=int(type_id))
    news.save()
    return JsonResponse({"ok": True})


@admin_required
@require_http_methods(["POST"])
def admin_news_delete(request, news_id):
    """单条删除公告"""
    news = get_object_or_404(News, id=news_id)
    news.delete()
    return JsonResponse({"ok": True})


@admin_required
@require_http_methods(["POST"])
def admin_news_batch_delete(request):
    """批量删除公告"""
    ids = request.POST.getlist("ids[]")
    if not ids:
        return JsonResponse({"ok": False, "msg": "请选择要删除的公告"})
    News.objects.filter(id__in=ids).delete()
    return JsonResponse({"ok": True, "count": len(ids)})


# ============================================================
# 前台 — 游客浏览模块
# ============================================================

def front_index(request):
    """前台首页 — 公告列表"""
    qs = News.objects.select_related("news_type").all()

    type_id = request.GET.get("type_id", "").strip()
    if type_id:
        qs = qs.filter(news_type_id=int(type_id))

    paginator = Paginator(qs, 10)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)

    types = NewsType.objects.all()
    return render(request, "front_index.html", {
        "page_obj": page_obj,
        "types": types,
        "current_type_id": int(type_id) if type_id else 0,
    })


def front_detail(request, news_id):
    """公告详情页"""
    news = get_object_or_404(News.objects.select_related("news_type"), id=news_id)
    return render(request, "front_detail.html", {"news": news})
