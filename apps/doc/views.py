from django.shortcuts import render
from .models import Doc
from django.http import FileResponse
import requests
from utils import json_status
# Create your views here.
def search(request):
    return render(request, 'news/search.html')

def docDownload(request):
    docs = Doc.objects.filter(is_delete=False)
    return render(request, 'doc/docDownload.html', context={'docs': docs})

# 下载文件
def download_doc(request):
    # 获取前端传过来的id
    doc_id = request.GET.get("doc_id")
    # 根据id 查出来文档
    doc = Doc.objects.filter(id=doc_id).first()
    if doc:
        # http://192.168.31.200:8000/media/avatar.jpeg
        file_path = doc.file_path
        # requests 返回文件对象,先用requests.get获取文件，然后创建fileresponse对象
        res = FileResponse(requests.get(file_path))
        # 切出文件后缀
        file_type = file_path.split('.')[-1]
        # 设置文件类型 https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
        if file_type == 'jpg':
            res["Content-type"] = "image/jpeg"
        elif file_type == 'doc':
            res["Content-type"] = "application/msword"
        elif file_type == 'txt':
            res["Content-type"] = "text/plain"
        else:
            res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        # 设置附件下载格式
        res["Content-Disposition"] = "attachment; filename={}".format(file_path.split('/')[-1])
        return res
    return json_status.params_error(message="文档不存在")


