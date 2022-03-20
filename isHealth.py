'''
Descripttion: 
version: 
Author: A1ertx5s
Date: 2022-01-24 17:47:08
LastEditors: sA1ertx5s
LastEditTime: 2022-03-20 11:10:12
'''

from gc import collect
from glob import escape
import requests
import json
import io
import random
import time
import re
import pyDes
import base64
import uuid
import sys
import os
import hashlib
from Crypto.Cipher import AES
from tools import CpdailyTools

class DailyCP:
    """
    今日校园打卡，学习的项目链接是：
    https://gitee.com/Finch1/FKDailyCP/blob/master/DailyCP.py
    """
    def __init__(self, schoolName="华侨大学", user=None) -> None:
        self.key = "b3L26XNL"
        self.session = requests.session()
        self.userInfo = user
        self.host = ""
        self.loginUrl = ""
        self.isIAPLogin = True
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37",
            # "X-Requested-With": "XMLHttpRequest",
            "Pragma": "no-cache",
            "Accept": "application/json, text/plain, */*",
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            # "User-Agent": "okhttp/3.12.4"
        })
        extension = {"deviceId": str(uuid.uuid4()), "systemName": "未来操作系统", "userId": "5201314",
                     "appVersion": "8.1.13", "model": "红星一号量子计算机", "lon": 0.0, "systemVersion": "初号机", "lat": 0.0}
        self.session.headers.update(
            {"Cpdaily-Extension": self.encrypt(json.dumps(extension))})
        self.setHostBySchoolName(schoolName)

    def setHostBySchoolName(self, schoolName):
        """
        获取院校的登录地址
        """
        # 获取院校简称hqdx
        ret = self.request(
            "https://static.campushoy.com/apicache/tenantListSort")
        school = [j for i in ret["data"]
                    for j in i["datas"] if j["name"] == schoolName] 
        if len(school) == 0:
            print("该院校不支持")
            exit()
        
        # 通过简称获取院校的登录地址
        ret = self.request("https://mobile.campushoy.com/v6/config/guest/tenant/info?ids={ids}".format(ids=school[0]["id"]))
        self.loginUrl = ret["data"][0]["ampUrl"]
        if ret == "":
            print("学校没有使用今日校园")
            exit()

        print("+"*25 + "成功获取登录地址" + "+"*25)
        print("{name}的登录地址是{url}".format(name=schoolName, url=self.loginUrl))
        
        # 获取host
        self.host = re.findall(r"//(.*?)/", ret["data"][0]["ampUrl2"])[0]

    def login(self, username, password, captcha=""):
        """
        登录，有两种登录方式，hqu使用的是第二种
        """
        if "campusphere" in self.loginUrl:
            return self.loginIAP(username, password, captcha)
        else:
            return self.loginAuthserver(username, password, captcha)

    def loginAuthserver(self, username, password, captcha=""):
        """
        登录
        """
        ret = self.request(self.loginUrl, parseJson=False)
        body = dict(re.findall(
            r'''<input type="hidden" name="(.*?)" value="(.*?)"''', ret.text))
        salt = dict(re.findall(
            r'''<input type="hidden" id="(.*?)" value="(.*?)"''', ret.text))
        body["username"] = username
        body["dllt"] = "userNamePasswordLogin"
        if "pwdDefaultEncryptSalt" in salt.keys():
            body["password"] = self.passwordEncrypt(
                password, salt["pwdDefaultEncryptSalt"])
        else:
            body["password"] = password
        ret = self.request(ret.url, body, False, False, Referer=self.loginUrl).text
        print("+"*25 + "成功获取Session" + "+"*25)
        print(self.session.cookies)
        return True

    def getCollectorList(self):
        """
        获取打卡列表
        """
        body = {
            "pageSize": 10,
            "pageNumber": 1
        }
        # ret = self.request(
        #     "https://hqu.campusphere.net/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList", body)
        self.session.headers["Content-Type"] = "application/json"
        url = "https://{host}/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList".format(host=self.host)
        ret = self.session.post(url, data=json.dumps(body))
        ret = self.session.post(url, data=json.dumps(body))
        print(ret.text)
        ret = json.loads(ret.text)
        return ret["datas"]["rows"]

    def getCollectorDetail(self, collectorWid):
        body = {
            "collectorWid": collectorWid
        }
        url = "https://{host}/wec-counselor-collector-apps/stu/collector/detailCollector".format(host=self.host)
        ret = self.session.post(url, data=json.dumps(body))
        ret = self.session.post(url, data=json.dumps(body))
        ret = json.loads(ret.text)
        return ret

    def getCollectorFormFiled(self, formWid, collectorWid):
        body = {
            "pageSize": 50,
            "pageNumber": 1,
            "formWid": formWid,
            "collectorWid": collectorWid
        }
        url = "https://{host}/wec-counselor-collector-apps/stu/collector/getFormFields".format(host=self.host)
        # ret = self.session.post(url, data=json.dumps(body))
        ret = self.session.post(url, data=json.dumps(body))
        ret = json.loads(ret.text)
        return ret["datas"]["rows"]

    def fillForm(self, form):
        for formItem in form:
            if formItem["isRequired"] == True and formItem["fieldType"] == "2":
                for fieldItem in formItem["fieldItems"].copy():
                    print(type(fieldItem["isSelected"]))
                    if fieldItem["isSelected"] == 1:
                        formItem["value"] = fieldItem["itemWid"]
                    elif fieldItem["isSelected"] == None:
                        formItem['fieldItems'].remove(fieldItem)
                        print("remove")
            elif formItem["isRequired"] == False:
                form.remove(formItem)
        
    def submitCollectorForm(self, formWid, collectWid, schoolTaskWid, rows, address, instanceWid):
        body = {
            "formWid": formWid,
            "collectWid": collectWid,
            "schoolTaskWid": schoolTaskWid,
            "form": rows,
            "address": address,
            "uaIsCpadaily":True,
            "latitude": self.userInfo["lat"],
            "longitude": self.userInfo["lon"],
            "instanceWid": instanceWid
        }

        bodyString = CpdailyTools.encrypt_BodyString(json.dumps(body))

        extension = {
            "model": "OPPO R11 Plus",
            "appVersion": "9.0.14",
            "systemVersion": "9.1.0",
            "userId": self.userInfo['username'],
            "systemName": "android",
            "lon": self.userInfo['lon'],
            "lat": self.userInfo['lat'],
            "deviceId": str(uuid.uuid1())
        }

        cpdailyExtension = CpdailyTools.encrypt_CpdailyExtension(
            json.dumps(extension)
        )

        submitData = {
            "lon": self.userInfo['lon'],
            "version": self.userInfo['signVersion'],
            "calVersion": self.userInfo['calVersion'],
            "deviceId": extension['deviceId'],
            "userId": self.userInfo['username'],
            "systemName": extension['systemName'],
            "bodyString": bodyString,
            "lat": self.userInfo['lat'],
            "systemVersion": extension['systemVersion'],
            "appVersion": extension['appVersion'],
            "model": extension['model'],
        }

        submitData['sign'] = CpdailyTools.signAbstract(submitData)

        headers = {
            'User-Agent': self.session.headers['User-Agent'],
            'CpdailyStandAlone': '0',
            'extension': '1',
            'Cpdaily-Extension': cpdailyExtension,
            'Content-Type': 'application/json; charset=utf-8',
            # 请注意这个应该和配置文件中的host保持一致
            'Host': self.host,
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        url = "https://{host}/wec-counselor-collector-apps/stu/collector/submitForm".format(host=self.host)
        ret = self.session.post(url, headers=headers, data=json.dumps(submitData))
        ret = self.session.post(url, headers=headers, data=json.dumps(submitData))
        ret = json.loads(ret.text)
        print(ret["message"])
        return ret["message"] == "SUCCESS"

    def autoComplete(self, address, dbpath):
        # 获取收集列表
        collectList = self.getCollectorList()
        print("+"*25 + "成功抓取打卡项目" + "+"*25)
        for r in collectList:
            print("wid: ", r["wid"])
            print("标题：", r["subject"])
            print("创建人：", r["senderUserName"])
            print("-"*66)
            print(r)
            print(self.getCollectorDetail("62057"))
        for item in collectList:
            # 获取表单
            form = self.getCollectorFormFiled(item["formWid"], item["wid"])
            # 表单存储地址
            # formpath = "{dbpath}/test.json".format(dbpath=dbpath)
            self.fillForm(form)
            # if not os.path.exists(formpath):
            #     with open(formpath, "wb") as file:
            #         file.write(json.dumps(
            #             form, ensure_ascii=False).encode("utf-8"))
            try:
                flag = self.submitCollectorForm(item["formWid"], item["wid"], "", form, address, item["instanceWid"])
            except:
                flag = False
            if flag == True:
                print("+"*30 + "打卡成功!!" + "+"*30)
        return flag

    def encrypt(self, text):
        k = pyDes.des(self.key, pyDes.CBC, b"\x01\x02\x03\x04\x05\x06\x07\x08",
                      pad=None, padmode=pyDes.PAD_PKCS5)
        ret = k.encrypt(text)
        return base64.b64encode(ret).decode()

    def passwordEncrypt(self, text: str, key: str):
        def pad(s): return s + (len(key) - len(s) %
                                len(key)) * chr(len(key) - len(s) % len(key))

        def unpad(s): return s[:-ord(s[len(s) - 1:])]
        text = pad(
            "TdEEGazAXQMBzEAisrYaxRRax5kmnMJnpbKxcE6jxQfWRwP2J78adKYm8WzSkfXJ"+text).encode("utf-8")
        aes = AES.new(str.encode(key), AES.MODE_CBC,
                      str.encode("ya8C45aRrBEn8sZH"))
        return base64.b64encode(aes.encrypt(text))
    
    def request(self, url: str, body=None, parseJson=True, JsonBody=True, Referer=None):
        url = url.format(host=self.host)
        if Referer != None:
            self.session.headers.update({"Referer": Referer})
        if body == None:
            ret = self.session.get(url)
        else:
            self.session.headers.update(
                {"Content-Type": ("application/json" if JsonBody else "application/x-www-form-urlencoded")})
            ret = self.session.post(url, data=(
                json.dumps(body) if JsonBody else body))
        if parseJson:
            return json.loads(ret.text)
        else:
            return ret        

if __name__ == "__main__":
    users = [
    {
        "username": "19251040xx",
        "lon": "118.899015",
        "lat": "25.136278",
        "signVersion": "first_v3",
        "calVersion": "firstv",
        "schoolName": "华侨大学",
        "password": "xxxxxxxx",
        "address": "你的地址"
    },
    ]
    for user in users:
        app = DailyCP(user["schoolName"], user)
        app.login(user["username"], user["password"])
        app.autoComplete(user["address"], "formdb")