import random
import requests
import re
import cv2
import numpy as np
from io import BytesIO
from bs4 import BeautifulSoup


API_PAGE = 'https://ppbc.iplant.cn/tu/{}'
API_SPID = 'https://ppbc.iplant.cn/ashx/getotherinfo.ashx?spid={}&t=photosys'

def getpic(pid):
    pid = str(pid)
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3',
               'Referer': API_PAGE.format(pid)}
    ses = requests.session()
    res = ses.get(API_PAGE.format(pid), allow_redirects=True).text
    reg = re.search('"(//img\\d\\.iplant\\.cn/image(.*?))"', res)
    if not reg: return None
    spid = re.search('var photospid = "(.*?)"', res).group().strip('var photospid = "').strip('"')
    des = ses.get(API_SPID.format(spid)).text
    if '植物界' in des or '科' not in des: return None
    link = reg.group().strip('"')
    res = ses.get('https:' + link, headers=headers).content
    soup = BeautifulSoup(des)
    for a in soup.find_all('a'):
        original = a.get_text().strip().split(' ')[0]
        if '属' not in original and '科' not in original:
            a['href'] = 'https://ppbc.iplant.cn' + a['href']
            a['target'] = '_blank'
            continue
        new_url = f"https://duocet.ibiodiversity.net/index.php?title={original}"
        a['href'] = new_url
    des = str(soup)
    return link, res, des

def randpic():
    while True:
        rand = random.randint(10000, 5000000)
        res = getpic(rand)
        if res: 
            return res
        
def replaceAll(input, toReplace, replaceWith):
    while input.find( toReplace ) > -1:
        input = input.replace(toReplace, replaceWith)
    return input

def imgCompress(content, size=199, quality=90, step=5, picType='.jpg'):
    # 读取图片bytes
    img_np = np.frombuffer(content, np.uint8)
    img_cv = cv2.imdecode(img_np, cv2.IMREAD_ANYCOLOR)
    pic_byte = content
    current_size = len(pic_byte) / 1024
    while current_size > size:
        pic_byte = cv2.imencode(picType, img_cv, [int(cv2.IMWRITE_JPEG_QUALITY), quality])[1]
        if quality - step < 0:
            break
        quality -= step
        current_size = len(pic_byte) / 1024
    return BytesIO(pic_byte).getvalue()

def addBlurSides(imageBytes, picType='.jpg', aspectRatio=4 / 3, blurWidth=None, kernelSize=(75, 75)):
    imageNp = np.frombuffer(imageBytes, np.uint8)
    image = cv2.imdecode(imageNp, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Error: Could not decode the image data.")
    height, width, _ = image.shape
    if width < height:
        newWidth = int(height * aspectRatio)
        newImage = np.zeros((height, newWidth, 3), dtype=np.uint8)
        xPosition = (newWidth - width) // 2
        newImage[:, xPosition:xPosition+width] = image
        if blurWidth is None:
            blurWidth = xPosition
        # 从原始图像的左侧开始计算模糊区域
        blurLeft = cv2.blur(image[:, :blurWidth], kernelSize)
        blurRight = cv2.blur(image[:, -blurWidth:], kernelSize)
        newImage[:, :blurWidth] = blurLeft
        newImage[:, -blurWidth:] = blurRight
        _, buffer = cv2.imencode(picType, newImage)
        return buffer.tobytes()
    else:
        _, buffer = cv2.imencode(picType, image)
        return buffer.tobytes()
