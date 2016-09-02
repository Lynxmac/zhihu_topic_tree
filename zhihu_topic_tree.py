#-*-encoding:utf8-*-
import os, platform, time, random
import json,sys
import requests
import cookielib
import re
import Logging
import PIL

if platform.system()=='Windows':
    reload(sys)
    sys.setdefaultencoding('utf-8')
else:
    pass

Header = { 'Host':'www.zhihu.com',
          'Referer': 'http://www.zhihu.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36'
                        ' (KHTML, like Gecko) Chrome/52.0.2743.82 '
                        'Safari/537.36 OPR/39.0.2256.48',
            'X-Requested-With': 'XMLHttpRequest'}



BASE_URL = 'https://www.zhihu.com/'

CAPTURE_URL = BASE_URL+'captcha.gif?r=1466595391805&type=login'

PHONE_LOGIN = BASE_URL + 'login/phone_num'#邮箱登陆需在这里修改登陆接口

requests = requests.session()
requests.headers.update(Header)
requests.cookies = cookielib.LWPCookieJar('cookies')




def search_xsrf():
    url = "http://www.zhihu.com/"
    r = requests.get(url)
    if int(r.status_code) != 200:
        raise NetworkError(u"验证码请求失败")
    results = re.compile(r"\<input\stype=\"hidden\"\sname=\"_xsrf\"\svalue=\"(\S+)\"", re.DOTALL).findall(r.text)
    if len(results) < 1:
        Logging.info(u"提取XSRF 代码失败" )
        return None
    return results[0]

def login():
    phoneNum = '在这里输入手机号码'
    password = '在这里输入密码'
    with open('./cap.gif','wb') as f:
        f.write(requests.get(CAPTURE_URL).content)
    #Img = Image.open('./cap.gif')
    #Img.show()
    captcha = raw_input('capture:')
    data = {"phone_num":phoneNum,"password":password,"captcha":captcha}
    requests.post(PHONE_LOGIN, data)
    #print r.cookies
    #return r

def expand_list(nested_list):
    for item in nested_list:
        if isinstance(item, (list, tuple)):
            for sub_item in expand_list(item):
                yield sub_item
        else:
            yield item

def load(children,parent):
    global xrsf
    url = 'https://www.zhihu.com/topic/19776749/organize/entire?child='+children+'&parent='+parent
    payload = {
        '_xsrf':xrsf
    }
    params = {'child':children,'parent':parent}
    req= requests.post(url, data=payload,params = params,timeout=60*4)
    result = json.loads(req.text)['msg']
    tmp =  list(expand_list(result))
    return [x for x in tmp if x !='']

def loadmore(expand,sub_list):
    time.sleep(random.randrange(1,3))
    children = expand[-2]
    parent = expand[-1]
    expand = load(children,parent)#[3:]
    if expand[-3]== u"加载更多":
        return expand,sub_list+expand[3:-4]
    return expand,sub_list+expand[3:]

def weiguilei():
    children = ''
    parent = '19776751'
    expand = load(children,parent)
    sub_list = expand[1:-4]
    while expand[-3] == u"加载更多":
        expand,sub_list = loadmore(expand,sub_list)
    for i in range(len(sub_list)):
        print sub_list[i]
        if sub_list[i] == 'topic':
            try:
                path = sub_list[1]+'_'+sub_list[0].decode('utf-8')\
                            +'/'+sub_list[i+2]+'_'+sub_list[i+1].decode('utf-8')
                os.makedirs(path)
            except:
                pass
    return

def get_index(parent,path):
    children = ''
    expand = load(children,parent)
    if expand[-3]==u'加载更多':
        sub_list = expand[1:-4]
    else:
        sub_list =expand[1:]
    while expand[-3] == u"加载更多":
        expand,sub_list = loadmore(expand,sub_list)
    for i in range(len(sub_list)):
        if sub_list[i] == 'topic':
            try:
                tmppath = path +'/'+sub_list[i+2]+'_'+sub_list[i+1].decode('utf-8')
                os.makedirs(tmppath)
                if sub_list[i+3]=='load':
                    print tmppath
                    get_index(sub_list[i+5],tmppath)
            except:
                pass


def generate_txt():
    if platform.system() == 'Windows':
        print 'yes'
        os.system('tree /f>zhihu_topic_tree.txt')
    else:
        os.system('tree ./>zhihu_topic_tree.txt')




if __name__=="__main__":
    login()
    xrsf  = search_xsrf()
    children = ''
    parents =['19778287','19560891','19618774','19778298']
    for rootdir in parents:
        expand = load(children,rootdir)
        path = expand[1]
        get_index(rootdir,path)
    weiguilei()

