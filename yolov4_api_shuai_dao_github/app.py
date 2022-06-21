from flask import Flask, Response, request, render_template
from werkzeug.utils import secure_filename
import os
from PIL import Image
from predict_api import predict,predict_down
app = Flask(__name__)
# 设置图片保存文件夹
UPLOAD_FOLDER = 'static/photo'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 设置允许上传的文件格式
ALLOW_EXTENSIONS = [ 'jpg', 'jpeg','avi','mp4']

# 判断文件后缀是否在列表中
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in ALLOW_EXTENSIONS

# 上传图片
@app.route("/photo/upload", methods=['POST', "GET"])

def uploads():
    path ='./static/result/'
    filelist = os.listdir(path)
    for item in filelist:
        os.remove(os.path.join(path, item))
    if request.method == 'POST':
        # 获取post过来的文件名称，从name=file参数中获取
        file = request.files['file']
        if file and allowed_file(file.filename):
            print(file.filename)
            # secure_filename方法会去掉文件名中的中文
            file_name = secure_filename(file.filename)

            # # 保存图片
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            # image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            # state=predict(image,file_name)

            # 保存视频
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            if file.filename.rsplit('.', 1)[-1] =="avi" or file.filename.rsplit('.', 1)[-1] =="mp4":
                state = predict_down(video_path,file_name)
            else:
                image = Image.open(video_path)
                state = predict(image,file_name)

            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            s=""
            if state==0:
                s="摔倒事件未发生"
            elif state==1:
                s="摔倒事件发生"
            pppp='\\static\\result'+"\\" + file_name
            return render_template('success.html',sc=pppp,st=s)
        else:
            return "格式错误，请上传jpg格式文件"
    return render_template('index.html')
@app.route('/')
def init():
    return render_template('index.html')
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

