'''
predict1.py有几个注意点
1、无法进行批量预测，如果想要批量预测，可以利用os.listdir()遍历文件夹，利用Image.open打开图片文件进行预测。
2、如果想要保存，利用r_image.save("img.jpg")即可保存。
3、如果想要获得框的坐标，可以进入detect_image函数，读取top,left,bottom,right这四个值。
4、如果想要截取下目标，可以利用获取到的top,left,bottom,right这四个值在原图上利用矩阵的方式进行截取。
'''
import urllib #发送请求
import hashlib #加密
import time
from PIL import Image
import os
import numpy as np
import cv2
import logging.config
from yolo import YOLO
logging.config.fileConfig('./loggers.conf')
logger = logging.getLogger('applog')
import datetime
yolo = YOLO()

def predict(image,name):
    try:
        situation = 0
    except:
        print('Open Error! Try again!')
    else:
        r_image,list1 = yolo.detect_image(image)
        r_image.save("./static/result/" +name)

        for p in range(len(list1)):
            if list1[p]=="Down":
                situation=1
                print('摔倒事件发生')

    return situation

def predict_down(video_path,save_name):
    video_fps = 25.0
    capture = cv2.VideoCapture(video_path)

    if save_name != "":
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        out = cv2.VideoWriter("./static/result/" +save_name, fourcc, video_fps, size)

    ref, frame = capture.read()
    if not ref:
        raise ValueError("未能正确读取摄像头（视频），请注意是否正确安装摄像头（是否正确填写视频路径）。")

    fps = 0.0
    is_first_down = False
    is_send = False
    count_down = 0
    count_sum = 0
    percentage =0
    final_situation = 0

    i=0
    while (True):

        i=i+1
        print(i)

        situation = 0
        t1 = time.time()
        # 读取某一帧
        ref, frame = capture.read()
        if not ref:
            break
        # 格式转变，BGRtoRGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 转变成Image
        frame = Image.fromarray(np.uint8(frame))
        # 进行检测
        f1, l1 = yolo.detect_image(frame)
        for p in range(len(l1)):
            if l1[p]=="Down":
                situation=1
                if not is_first_down:
                    is_first_down = True
                # print('摔倒事件发生')

        if is_first_down:
            # print(i,count_sum,count_down,percentage,final_situation)
            count_sum = count_sum + 1
            if situation==1:
                count_down=count_down + 1
            if count_sum<91 and count_sum%30 ==0:
                percentage = float(count_down/count_sum)

            if percentage>0 and percentage<0.84:
                is_first_down = False
                count_sum = 0
                count_down = 0
            if count_sum==90 and percentage>=0.84:
                print("摔倒事件成立")
                final_situation = 1
                is_send = True
                is_first_down = False
                count_sum = 0
                count_down = 0

        if final_situation==1 and is_send ==True:
            phone = 18305167550
            t1 = datetime.datetime.now()
            duanx = smsbao(phone, '【智慧家居】您绑定的家庭摄像头于'+' '+str(t1)+' '+'检测到摔倒事件发生，请及时查看，如非本人操作请勿理会。')
            final_situation = 0
            is_send = False

        frame = np.array(f1)
        # RGBtoBGR满足opencv显示格式
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        fps = (fps + (1. / (time.time() - t1))) / 2
        print("fps= %.2f" % (fps))
        frame = cv2.putText(frame, "fps= %.2f" % (fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # cv2.imshow("video", frame)
        c = cv2.waitKey(1) & 0xff
        if save_name != "":
            out.write(frame)

        if c == 27:
            capture.release()
            break

    print("Video Detection Done!")
    capture.release()
    if save_name != "":
        print("Save processed video to the path :" + save_name)
        out.release()
    cv2.destroyAllWindows()
    return final_situation

def md5s(strs):
   m = hashlib.md5()
   m.update(strs.encode("utf8")) #进行加密
   return m.hexdigest()

def smsbao(phone, text):  # 短信宝接口对接
    statusStr = {
        '0': '短信发送成功',
        '-1': '参数不全',
         '-2': '服务器不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间',
        '30': '密码错误',
        '40': '账号不存在',
        '41': '余额不足',
        '42': '账户已过期',
        '43': 'IP地址限制',
        '50': '内容含有敏感词',
        '51': '手机号码不正确'
    }
    smsapi = "http://api.smsbao.com/"
    # 短信平台账号
    user = 'yrf132336'
    # 短信平台密码
    password = md5s('yrf132336@')
    # 要发送的短信内容
    content = str(text)
    # 要发送短信的手机号码
    phone = str(phone)

    data = urllib.parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
    send_url = smsapi + 'sms?' + data
    response = urllib.request.urlopen(send_url)
    the_page = response.read().decode('utf-8')
    try:
        print(statusStr[the_page])
        return (statusStr[the_page])
    except:
        print('短信发送出现未知错误')
        return '未知错误'

if __name__ == '__main__':
    image_path = "img/1.jpg"
    image_name = "1.jpg"

    # image = Image.open(image_path)
    # situation = predict(image,image_name)
    # print(situation)

    video_path = "D:\\zhuan_ye_shi_jian\\yolov4_api_shuai_dao\\待检测视频资料\\Coffee_room\\video (47).avi"
    save_name  = "video (47).avi"
    final_situation = predict_down(video_path,save_name)
    print(final_situation)


