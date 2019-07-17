import requests
import urllib
import base64
import time
import re
import json
import logging
import rsa
import binascii
import random
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# logging.getLogger("requests").setLevel(logging.WARNING)
# from requests.packages.urllib3.connectionpoll import InsecuerRequestWarning
# requests.packages.urllib3.display_warnings(InsecureRequestWarning)


header={
    
    'User-Agent':	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
    'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding':	'gzip, deflate, br',
    'Accept-Language'	:'zh-CN,zh;q=0.9',
    'Referer':'https://webo.com/?sudaref=www.baidu.com&display=0&retcode=6102',
    'Connection':'keep-alive'
}

class Login(object):
    user_name=""
    pass_word=""
    def get_name(self):
        self.user_name=input(u"请输入用户名")
    def get_pass(self):
        self.pass_word=input(u"请输入密码")

    session =requests.session()

    def get_username(self):
        # print(base64.b64encode(urllib.parse.quote(self.user_name).encode("utf-8")).decode("utf-8"))
        return base64.b64encode(urllib.parse.quote(self.user_name).encode("utf-8")).decode("utf-8")

    def get_pre_login(self):
        int(time.time()*1000)
        params={
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallback",
            "su": self.get_username(),
            "rsakt":"mod",
            "checkpin":"1",
            "client":"ssologin.js(v1.4.19)",
            "_": int(time.time()*1000)
        }
        try:
            response= self.session.post("https://login.sina.com.cn/sso/prelogin.php",params=params,headers=header,verify=False)
            # print(response.text)
            # print(json.loads(re.search(r"\((?P<data>.*)\)",response.text).group("data")))
            return (json.loads(re.search(r"\((?P<data>.*)\)",response.text).group("data")))
        except:
            print("获取公钥失败")
            return 0
        
    def get_password(self):
        # print(self.get_pre_login()["servertime"])
        publib_key=rsa.PublicKey(int(self.get_pre_login()["pubkey"],16),int("10001",16))
        # print (publib_key)
        password_string=str(self.get_pre_login()["servertime"])+'\t'+str(self.get_pre_login()["nonce"])+'\n'+self.pass_word
        # print(password_string)
        password =binascii.b2a_hex(rsa.encrypt(password_string.encode("utf-8"),publib_key)).decode("utf-8")
        # print(password)
        return password
    
    def login(self):
        pcid = self.get_pre_login()["pcid"]
        self.get_cha(pcid)
        door = input(u"请输入验证码")
        # print(self.get_pre_login()["servertime"])
        post_data={
            "entry"	:"weibo",
            "gateway"	:"1",
            "from"	:"",
            'savestate'	:'7',
            "qrcode_flag"	:"false",
            "useticket"	:"1",
            # pagerefer	
            "pcid"	: pcid,
            "door":	door,
            "vsnf":	"1",
            "su"	:self.get_username(),
            "service"	:"miniblog",
            "servertime":	self.get_pre_login()["servertime"],
            "nonce":	self.get_pre_login()["nonce"],
            "pwencode"	:"rsa2",
            "rsakv":	self.get_pre_login()["rsakv"],
            "sp":	self.get_password(),
            "sr":	"1920*1080" ,
            "encoding":	"UTF-8",
            "prelt":	"442",
            "url"	:"https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype":	"TEXT"

        }

    
        login_data = self.session.post("https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)",data=post_data,headers=header,verify=False)
        # print(login_data.text)

        params={
            "ticket":login_data.json()['ticket'],
            "ssosavestate":int(time.time()),
            "callback":"sinaSSOController.doCrossDomainCallBack",
            "scripId":"ssoscript0",
            "client":"ssologin.js(v1.4.19)",
            "_":int(time.time()*1000)
        }
        session=self.session.post("https://passport.weibo.com/wbsso/login",headers=header,verify=False,params=params)
        # urlnew = re.findall('location.replace\(\'(.*?)\'',session.content,re.S)[0]
        # print(urlnew)
        return self.session
    
    def get_cha(self,pcid):
        session = requests.session()
        cha_url = "http://login.sina.com.cn/cgi/pin.php?r="
        cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
        cha_url = cha_url + pcid
        print(cha_url)
        cha_page = session.get(cha_url, headers=header)
        with open("cha.jpg", 'wb') as f:
            f.write(cha_page.content)
            f.close()
        # try:
        #     # im = Image.open("cha.jpg")
        #     # im.show()
        #     # im.close()
        # except:
        #     print(u"请到当前目录下，找到验证码后输入")




# login = Login()
# login.get_name()
# login.get_pass()
# session=login.login()
# login.get_pre_login()

# with open("cookie.json","w") as f:
#             # f.write(str(session.cookies.get_dict()))
#             json.dump(session.cookies.get_dict(), f)
#             f.close()

# print(session.cookies.get_dict())

# response=session.post("https://weibo.com",headers=header,verify=False)

# c = requests.cookies.RequestsCookieJar()
#     for i in cookie:    #添加cookie到CookieJar
#         c.set(i["name"], i["value"])
#     s.cookies.update(c)     #更新session里的cookie

with open("cookie.json","r") as f:
            cookies=json.load(f)
            f.close()
# # print(cookie)

# response=session.get("https://weibo.com",headers=header,verify=False)
response=requests.session().get("https://weibo.com",headers=header,verify=False,cookies=cookies)
soup = BeautifulSoup(response.text,"html.parser")
print(soup.find("title"))
