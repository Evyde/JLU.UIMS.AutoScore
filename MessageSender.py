import json
from email.header import Header
from email.mime.text import MIMEText
from urllib import parse
import smtplib
import requests


class MessageSender(object):
    __method = "ServerChan"
    __sender = None
    __obj = None
    initFlag = False

    def __new__(cls, *args, **kwargs):
        if cls.__obj is None:
            cls.__obj = super().__new__(cls)
        return cls.__obj

    def __init__(self, method):
        self.__methods = {
            "server_chan": ServerChanSender,
            "bark": BarkSender,
            "smtp": SMTPSender,
            "console": ConsoleSender,
            "mirai": MiraiHTTPApiSender
        }
        if self.initFlag is False:
            self.__method = str(method)
            self.__method = self.__method.lower()
        self.initFlag = True

    def config(self, config):
        if self.__method in self.__methods:
            self.__sender = self.__methods[self.__method](config)
        else:
            raise Exception("Configure Exception")

    def send(self, msg):
        try:
            return self.__sender.send(msg)
        except:
            raise Exception("Sender Exception")

    def getMethod(self):
        return self.__method

    def setMethod(self, method):
        if method.lower() == self.__method:
            return
        self.__method = str(method).lower()


class ServerChanSender(object):
    __sckey = ""
    __url = "https://sc.ftqq.com/"
    __header = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    def __init__(self, SCKEY):
        self.__sckey = SCKEY['SCKEY']

    def send(self, msg):
        url = self.__url + self.__sckey + ".send"
        postData = {
            'text': msg['title'],
            'desp': msg['content']
        }
        return "发送状态：" + str(requests.post(url, postData, headers=self.__header))


class SMTPSender(object):
    __configList = {}
    __smtpObj = None

    def __init__(self, list):
        self.__configList = list
        self.__smtpObj = smtplib.SMTP_SSL(self.__configList['host'], self.__configList['port'])

    def send(self, msg):
        message = MIMEText(msg['content'], 'plain', 'utf-8')
        message['From'] = self.__configList['fromName']
        message['To'] = self.__configList['toName']
        message['Subject'] = Header(msg['title'], 'utf-8')
        self.__smtpObj.connect(self.__configList['host'])
        self.__smtpObj.ehlo(self.__configList['host'])
        self.__smtpObj.login(self.__configList['user'], self.__configList['pwd'])
        self.__smtpObj.sendmail(self.__configList['fromAddr'], self.__configList['toAddr'], message.as_string())
        return "已向%s发送邮件，请查收！" % self.__configList['toAddr']


class ConsoleSender(object):
    def __init__(self, config):
        pass

    def send(self, msg):
        print("《%s》" % msg['title'])

        print(msg['content'])
        return "控制台输出成功！"


class BarkSender(object):
    __apiKey = ""
    __url = "https://api.day.app/"

    def __init__(self, config):
        self.__apiKey = config['apikey']

    def send(self, msg):
        url = self.__url + self.__apiKey + "/" + parse.quote(
            msg['title']) + "/" + parse.quote(msg['content'])
        return "发送状态：" + str(requests.get(url))


class MiraiHTTPApiSender(object):
    _mah_friend_webhook = "localhost:9999/send"
    _mah_group_webhook = "localhost:9999/send"

    def __init__(self, config: dict):
        if config.get("friend_webhook") is not None:
            self._mah_friend_webhook = config["friend_webhook"]
        if config.get("group_webhook") is not None:
            self._mah_group_webhook = config["group_webhook"]

    def send(self, msg: dict):
        if msg.get("send_to") == "friend":
            return self.__send_to_friend(json.dumps(msg))
        elif msg.get("send_to") == "group":
            return self.__send_to_group(json.dumps(msg))
        return None

    def __send_to_group(self, msg: str):
        return requests.post(self._mah_group_webhook, data=msg).text

    def __send_to_friend(self, msg: str):
        return requests.post(self._mah_friend_webhook, data=msg).text
