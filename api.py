from flask import *
import base64
import dependencies
import json

app = Flask(__name__)

@app.route('/query-image', methods=['GET'])
def queryImage():
    link, content, des = dependencies.randpic()
    fname = link.split('/')[-1]
    com = dependencies.imgCompress(content, size=50, quality=90, picType='.'+fname.split('.')[-1])
    com = dependencies.addBlurSides(com, picType='.'+fname.split('.')[-1])
    img = base64.b64encode(com).decode()
    return 'requestSuccess(' + json.dumps({'img':img, 'link':link, 'des':des}) + ')'


if __name__ == '__main__':
    app.run('0.0.0.0', 9000)