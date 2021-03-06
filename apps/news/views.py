from django.db.models import Q
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, Http404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.decorators.http import require_GET
from utils import json_status
import os
from DJT import settings
from .forms import NewsPubForm, AddNewsCommentForm, NewsBannerForm
from ..admin_staff.models import NewsTag
from .models import News
from qiniu import Auth
from .models import NewsComment, NewsHot, NewsBanner
from .serializers import NewsCommentSerializers, NewsSerializers, NesTagSerializers, NewsHotSerializer, \
    NewsBannerSerializer
from utils.Mydecorators import ajax_login_reruired
from utils.Mydecorators import user_permission_required


# 发布新闻页面
@method_decorator([csrf_exempt, staff_member_required(login_url='/account/loading/')], name='dispatch')
class NewsPUbView(View):
    def get(self, request):
        tags = NewsTag.objects.filter(is_delete=0).all()
        return render(request, 'news/newspub.html', context={'tags': tags})

    def post(self, request):
        form = NewsPubForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            desc = form.cleaned_data.get('desc')
            tag_id = form.cleaned_data.get('tag_id')
            photo_url = form.cleaned_data.get('photo_url')
            content = form.cleaned_data.get('content')
            tag = NewsTag.objects.filter(id=tag_id).first()
            if tag:
                News.objects.create(title=title, desc=desc, tag=tag, photo_url=photo_url, content=content,
                                    author=request.user)
                return json_status.result()
        else:
            return json_status.params_error(message=form.get_error())


# 上传文件
@csrf_exempt
@user_permission_required(NewsBanner)
def UploadFile(request):
    file = request.FILES.get('upload_file')
    file_name = file.name
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    print(file)
    with open(file_path, 'wb') as data:
        # chunks 返回一个生成器
        for chunk in file.chunks():
            data.write(chunk)
    # 返回当前视图的绝对路径http://127.0.0.1:8000/admin/upload-file/
    # http: // 127.0.0.1: 8000 / Users / luweimin / PycharmProjects / DJT / mediacode.md
    file_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)
    return json_status.result(data={'file_url': file_url})


# 上传图片到七牛

def up_token(request):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = settings.QINIU_AK
    secret_key = settings.QINIU_SK
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'luweimin'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name)
    return JsonResponse({'uptoken': token})


# 新闻详情页面
def news_detail(request, news_id):
    # news = News.objects.filter(id=news_id, is_delete=0).first()
    # return render(request, 'news/news_detail.html', context={'news': news, })
    try:
        news = News.objects.get(id=news_id, is_delete=0)
        return render(request, 'news/news_detail.html', context={'news': news, })
    except News.DoesNotExist:
        # 页面不存在或者说找不到新闻，http404错误,只能debug=false才能用
        raise Http404


# 添加新闻评论
@method_decorator([csrf_exempt, ajax_login_reruired], name='dispatch')
class AddNewsCommentView(View):
    def post(self, request):
        form = AddNewsCommentForm(request.POST)
        if form.is_valid():
            news_id = form.cleaned_data.get('news_id')
            content = form.cleaned_data.get('content')
            news = News.objects.filter(id=news_id, ).first()
            if news:
                comment = NewsComment.objects.create(content=content, author=request.user, news=news)
                serializers = NewsCommentSerializers(comment)
                return json_status.result(data=serializers.data)
            else:
                return json_status.params_error('新闻不存在或已删除')
        else:
            return json_status.params_error(message='评论失败')


# 新闻评论列表
def comment_new(request):
    news_id = request.GET.get('news_id')
    news = News.objects.filter(id=news_id).first()
    if news:
        # news.newscomment_set反向查询
        news_comment = news.comment.all()
        # comments = list(news_comment.values())
        # 序列化查询结果，自动序列化关联的表
        serializers = NewsCommentSerializers(news_comment, many=True)
        # print(type(serializers))<class 'rest_framework.serializers.ListSerializer'>  ListSerializer
        # print(type(serializers.data))<class 'rest_framework.utils.serializer_helpers.ReturnList'>   JsonSerializer
        return json_status.result(data=serializers.data)
    else:
        return json_status.params_error(message='新闻不存在')


def news_list(request):
    tag_id = request.GET.get('tag_id')
    page = int(request.GET.get('page', 1))
    start_page = settings.ONE_PAGE_COUNT * (page - 1)
    end_page = start_page + settings.ONE_PAGE_COUNT
    newses = News.objects.defer('content').select_related('tag', 'author').filter(is_delete=0, tag_id=tag_id).all()[
             start_page: end_page]
    if tag_id:
        return json_status.result(data={'newses': NewsSerializers(newses, many=True).data})
    else:
        return json_status.params_error(message='新闻不存在')


# 返回api接口  /news/tag/list/
def news_tag_list(request):
    news_tags = NewsTag.objects.filter(is_delete=False).all()
    serizlizer = NesTagSerializers(news_tags, many=True)
    return json_status.result(data={'tags': serizlizer.data})


# 返回新闻和标签
def news_with_tag(request):
    tag_id = int(request.GET.get('tag_id', 0))
    if tag_id:
        newses = News.objects.filter(is_delete=False, tag=tag_id)
    else:
        newses = News.objects.filter(is_delete=False)
    serizlizer = NewsSerializers(newses, many=True)
    return json_status.result(data={'newses': serizlizer.data})


# 返回热门新闻列表
def hot_news_list(request):
    hot_news = NewsHot.objects.filter(is_delete=False)
    serializers = NewsHotSerializer(hot_news, many=True)
    return json_status.result(data=serializers.data)


# 轮播图的增删改
@method_decorator([csrf_exempt, ], name='dispatch')
class NewsBannerView(View):
    def get(self, request):
        return render(request, 'admin_staff/news/news_banner.html')

    def post(self, request):
        form = NewsBannerForm(request.POST)
        if form.is_valid():
            link_to = form.cleaned_data.get("link_to")
            image_url = form.cleaned_data.get('image_url')
            priority = form.cleaned_data.get('priority')
            print('link_to:{},image_url:{},priority:{} '.format(link_to, image_url, priority))
            banner = NewsBanner.objects.create(image_url=image_url, priority=priority, link_to=link_to)
            return json_status.result(data={"banner_id": banner.id})
        return json_status.params_error(message=form.get_error())

    def put(self, request):
        p = QueryDict(request.body)
        banner_id = p.get("banner_id")
        image_url = p.get("image_url")
        priority = p.get("priority")
        link_to = p.get("link_to")
        if banner_id:
            banner = NewsBanner.objects.filter(id=banner_id)
            if banner:
                banner.update(image_url=image_url, priority=priority, link_to=link_to)
                return json_status.result()
            return json_status.result().params_error(message='轮播图找不到')
        return json_status.result().params_error(message="bannerId不存在")

    def delete(self, request):
        d = QueryDict(request.body)
        banner_id = d.get("banner_id")
        if banner_id:
            banner = NewsBanner.objects.filter(id=banner_id)
            if banner:
                banner.update(is_delete=True)
                return json_status.result()
            return json_status.params_error(message="轮播图不存在")
        return json_status.params_error(message="轮播图id不存在")


@require_GET  # /news/banner/list/
def news_banner_list(request):
    """返回banner的列表 """
    banners = NewsBanner.objects.filter(is_delete=False)
    serializer = NewsBannerSerializer(banners, many=True)
    return json_status.result(data={"banners": serializer.data})

# 搜索视图
def searchView(request):
    q = request.GET.get('q', '')
    if q:
        ret_newses = News.objects.filter(
            Q(title__contains=q) | Q(content__icontains=q) | Q(author__username__icontains=q))
        context = {'ret_newses': ret_newses,
                   'q': q}
    else:
        hot_newses = NewsHot.objects.filter(is_delete=False).all()
        context = {'hot_newses': hot_newses}

    return render(request, 'news/search.html', context=context)