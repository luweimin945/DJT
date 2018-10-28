$(function () {

    // 生成富文本编辑器  https://www.kancloud.cn/wangfupeng/wangeditor3/332599
    let E = window.wangEditor;
    let editor = new E('#news-content');
    editor.create();

// ================== 上传至服务器 ================
    let $uploadThumbnail = $("#upload-news-thumbnail");
    let $thumbnailUrl = $("#news-thumbnail-url");
    $uploadThumbnail.change(function () {
        // 获取文件
        let file = this.files[0];
        // 创建一个 FormData
        let formData = new FormData();
        // 把文件添加进去
        formData.append("upload_file", file);
        // 发送请求
        $.ajax({
            url: "/admin/upload-file/",
            method: "post",
            data: formData,
            // 定义文件的传输
            processData: false,
            contentType: false,
            success: res => {
                if (res["code"] === 1) {
                    // 获取后台返回的 URL 地址
                    let thumbnailUrl = res["data"]["file_url"];
                    $thumbnailUrl.val('');
                    $thumbnailUrl.val(thumbnailUrl);
                }
            },
            error: err => {
                logError(err);
            }
        });
    });


    // ========= 发表新闻 ==========
    let $newsBtn = $("#btn-pub-news");
    $newsBtn.click(function () {
        let titleVal = $("#news-title").val();
        let descVal = $("#news-desc").val();
        let tagId = $("#news-category").val();
        let thumbnailVal = $thumbnailUrl.val();
        let contentHtml = editor.txt.html();
        let contentText = editor.txt.text();
        if (tagId === '0') {
            ALERT.alertInfoToast('请选择新闻标签')
        }
        // console.log(`
        //   新闻标题: ${titleVal},
        //   新闻描述: ${descVal},
        //   新闻分类id: ${tagId},
        //   新闻缩略图地址: ${thumbnailVal}
        //   新闻内容html版: ${contentHtml},
        //   新闻内容纯文字版：${contentText}
        // `);

        $.ajax({
            url: "/admin/newspub/",
            method: "post",
            data: {
                "title": titleVal,
                "desc": descVal,
                "tag_id": tagId,
                "photo_url": thumbnailVal,
                "content": contentHtml,
            },
            dataType: "json",
            success: res => {
                if (res["code"] === 1) {
                    ALERT.alertNewsSuccessCallback("新闻发表成功", '跳到首页', () => {
                        window.location.href = '/admin/staff/';
                    });
                } else {
                    ALERT.alertErrorToast(res["msg"]);
                }
            },
            error: err => {
                logError(err)
            }
        })
    })
});