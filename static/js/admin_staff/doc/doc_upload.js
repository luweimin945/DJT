$(function () {
    // 获取元素
    let $docTitle = $("#doc-title");
    let $docDesc = $("#doc-desc");
    let $docPathInput = $(".doc-path-input");
    let $docUpload = $("#upload-doc");
    let $saveBtn = $(".save-btn");
    console.log($docUpload);
    // 上传图片至服务器
    $docUpload.change(function () {
        // 获取文件
        let file = this.files[0];
        console.log(file);
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
                console.log(res);
                if (res["code"] === 1) {
                    // 获取后台返回的 URL 地址
                    let thumbnailUrl = res["data"]["file_url"];
                    $docPathInput.val('');
                    $docPathInput.val(thumbnailUrl);
                }
            },
            error: err => {
                logError(err);
            }
        });
    });

    // 保存按钮点击事件
    $saveBtn.click(function () {
        let docTitle = $docTitle.val();
        let docDesc = $docDesc.val();
        let docPath = $docPathInput.val();

        selfAjax('/admin/doc_upload/', 'post', {
            "title": docTitle, //文档标签
            "desc": docDesc,    //文档描述
            "file_path": docPath    //文档路径
        }, res => {
            if (res["code"] === 1) {
                ALERT.alertSuccessToast("保存成功");
                $docTitle.val('');
                $docDesc.val('');
                $docPathInput.val('');
            } else {
                ALERT.alertInfoToast(res["msg"]);
            }
        });
    });
});

/*== 封装 JQ 的 Ajax ==*/
function selfAjax(url, method, data, successCallback) {
    $.ajax({
        url,
        method,
        data,
        dataType: "json",
        success: successCallback || function (res) {
            console.log(res);
        },
        error: err => {
            logError(err);
        }
    });
}