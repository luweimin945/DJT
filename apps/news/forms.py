from django import forms
from apps.forms import FormMixin


# 提交新闻form验证表单
class NewsPubForm(forms.Form, FormMixin):
    title = forms.CharField(max_length=100, min_length=2,
                            error_messages={'required': '新闻标题不能为空', 'max_length': '新闻标题字数不能大于100'})
    desc = forms.CharField(max_length=200, min_length=2,
                           error_messages={'required': '新闻标题不能为空', 'max_length': '新闻标题字数不能大于200'})
    tag_id = forms.IntegerField(error_messages={'required': 'ID不能为空'})
    photo_url = forms.CharField(error_messages={'required': '图片不能为空'})
    content = forms.CharField(max_length=10000, min_length=2,
                              error_messages={'required': '新闻内容不能为空', 'max_length': '内容不能超过10000'})


class AddNewsCommentForm(forms.Form, FormMixin):
    news_id = forms.IntegerField(error_messages={'required': '新闻id不能为空'})
    content = forms.CharField(error_messages={'required': '评论不能为空'})


class NewsHotAddForm(forms.Form, FormMixin):
    news_id = forms.IntegerField(error_messages={'required': '参数错误'})
    priority = forms.IntegerField(error_messages={'required': '优先级不能为空'})


class NewsEditForm(NewsPubForm):
    news_id = forms.IntegerField(error_messages={'required': '新闻ID错误'})


class NewsBannerForm(forms.Form, FormMixin):
    image_url = forms.URLField(error_messages={'required': '图片地址不能为空', 'invalid': '请输入合法网址'})
    priority = forms.IntegerField(error_messages={'required': '优先级不能为空'})
    link_to = forms.URLField(error_messages={'required': '跳转地址不能为空', 'invalid': '请输入合法网址'})