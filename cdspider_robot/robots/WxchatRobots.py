#-*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"),
# see LICENSE for more details: http://www.apache.org/licenses/LICENSE-2.0.

"""
:author:  Zhang Yi <loeyae@gmail.com>
:date:    2018-8-29 20:23:59
"""
import json
import logging
import os
import queue
import tempfile
import time
import traceback

import itchat
from cdspider import Component
from cdspider.libs import utils
from itchat.content import *


class WxchatRobots(Component):
    """
    WEB微信机器人
    """
    def __init__(self, context, uuid):
        self.ctx = context
        g = context.obj
        self.g = g
        data_dir=g.get("runtime_dir", None)
        debug=g.get("debug", False)
        self.db = g.get('db')
        self.queue = g.get('queue')
        qname = 'wechat2reply4%s' % uuid
        self.message_queue = self.queue[qname]
        self.debug_mode = debug
        log_level = logging.WARN
        if debug:
            log_level = logging.DEBUG
        self.log_level = log_level
        self.qrfile = None
        logger = logging.getLogger('robots')
        super(WxchatRobots, self).__init__(logger, log_level)
        self.__uid = uuid
        self.uin = None
        self.temp_dir = data_dir or tempfile.gettempdir()
        self.info("temp dir: %s" % self.temp_dir)
        self.auto_reply = lambda x, y: None
        self.prepare_reply = set()
        self.prepared_session = set()
        self.login_post_fn = {
            'all': set(),
            'myself': set(),
            'contact': set(),
            'friends': set(),
            'chatrooms': set(),
            'mps': set(),
        }

    def get_message(self, message, uuin):
        try:
            s = self.auto_reply(message, uuin)
            data = json.loads(s)
            if data['status'] == 200:
                return data['data']
        except:
            self.error(traceback.format_exc())
        return "忙碌中..."

    def set_reply(self, fn):
        if not callable(fn):
            raise TypeError('reply fn expects a callable')
        self.auto_reply = fn

    def add_login_post(self, fn, t = None):
        if callable(fn):
            if not t:
                t = 'all'
            if t in self.login_post_fn:
                self.login_post_fn[t].add(fn)
    def add_prepare_reply(self, fn):
        if callable(fn):
            self.prepare_reply.add(fn)

    def run(self):

        itchat.set_logging(showOnCmd=self.debug_mode, loggingLevel = self.log_level)
        robot = itchat.new_instance()

        def login():
            self.info("The Wechat was login @ Process of No.%s " % (self.__uid))
            if self.qrfile and os.path.isfile(self.qrfile):
                os.remove(self.qrfile)
                self.qrfile = None
            myself = robot.search_friends()
            self.uin = myself['Uin']
            if self.login_post_fn['myself']:
                for fn in self.login_post_fn['myself']:
                    fn(myself, self.uin)
            friends = robot.get_friends()
            if self.login_post_fn['friends']:
                for fn in self.login_post_fn['friends']:
                    fn(friends, self.uin)
            chatrooms = robot.get_chatrooms()
            if self.login_post_fn['chatrooms']:
                for fn in self.login_post_fn['chatrooms']:
                    fn(chatrooms, self.uin)
            mps = robot.get_mps()
            if self.login_post_fn['mps']:
                for fn in self.login_post_fn['mps']:
                    fn(mps, self.uin)
            #获取联系人，并保存
            try:
                self.db["WechatRobotInfoDB"].insert(myself)
            except:
                self.error(traceback.format_exc())
            for item in friends:
                try:
                    item['IUin'] = self.uin
                    self.db["WechatRobotFriendsDB"].insert(item)
                except:
                    self.error(traceback.format_exc())
            for item in chatrooms:
                try:
                    item['IUin'] = self.uin
                    self.db["WechatRobotChatRoomsDB"].insert(item)
                except:
                    self.error(traceback.format_exc())
            for item in mps:
                try:
                    item['IUin'] = self.uin
                    self.db["WechatRobotMpsDB"].insert(item)
                except:
                    self.error(traceback.format_exc())
            if self.login_post_fn['all']:
                for fn in self.login_post_fn['all']:
                    fn(robot, self.uin)

        def logout():
            self.info("The Wechat was logout @ Process of No.%s " % (self.__uid))

        def qr_callback(**kwargs):
            try:
                qrcode = kwargs.get('qrcode')
                if qrcode:
                    dirname = os.path.join(self.temp_dir, "qr", "service")
                    qrfile = "wxqr_%s.png" % (self.__uid)
                    if os.path.exists(dirname) == False:
                        os.makedirs(dirname)
                    self.qrfile = os.path.join(dirname, qrfile)
                    self.info(self.qrfile)
                    with open(self.qrfile, 'wb') as f:
                        f.write(qrcode)
            except:
                self.error(traceback.format_exc())

        @robot.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
        def text_reply(msg):
            try:
                msg["IUin"] = self.uin
                self.db['WechatRobotChatInfoDB'].insert(msg)
    #            reply = self.get_message(msg.text, msg.user.userName)
    #            msg.user.send('%s' % reply)
                if self.message_queue:
                    self.message_queue.put_nowait({"user": msg.user.userName, "msg": msg.text, "nick": "", "auser": ""})
            except:
                self.error(traceback.format_exc())

        @robot.msg_register([TEXT, MAP, CARD, NOTE, PICTURE, RECORDING, VOICE, ATTACHMENT, VIDEO], isMpChat=True)
        def text_replay(msg):
            try:
                msg["IUin"] = self.uin
                self.db['WechatRobotMpsChatDB'].insert(msg)
            except:
                self.error(traceback.format_exc())

        @robot.msg_register(SHARING, isMpChat=True)
        def text_replay(msg):
            try:
                msg["IUin"] = self.uin
                self.db['WechatRobotMpsSharingDB'].insert(msg)
            except:
                self.error(traceback.format_exc())

        @robot.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
        def download_files(msg):
            try:
                msg.download(msg.fileName)
                typeSymbol = {
                    PICTURE: 'img',
                    VIDEO: 'vid', }.get(msg.type, 'fil')
                self.info('@%s@%s' % (typeSymbol, msg.fileName))
                return '@%s@%s' % (typeSymbol, msg.fileName)
            except:
                self.error(traceback.format_exc())

        @robot.msg_register(FRIENDS)
        def add_friend(msg):
            try:
                msg.user.verify()
                msg["IUin"] = self.uin
                self.db['wechat_robot_new_friend'].insert(msg)
            except:
                self.error(traceback.format_exc())


        @robot.msg_register(TEXT, isGroupChat=True)
        def text_reply(msg):
            try:
                self.db['WechatRobotGroupChatDB'].insert(msg)
                if msg.isAt:
                    if self.message_queue:
                        self.message_queue.put_nowait({"user": msg.user.userName, "msg": msg.text.split(u'\u2005')[1], "nick": msg.actualNickName, "auser": msg.actualUserName})
    #                reply = self.get_message(msg.text, msg.user.userName)
    #                msg.user.send(u'@%s\u2005 %s' % (
    #                    msg.actualNickName, reply))
            except:
                self.error(traceback.format_exc())

        try:
            self.info("wechat will running")
            f = None if self.debug_mode else qr_callback
            statusStorageDir = os.path.join(self.temp_dir, "wechat")
            self.info("login temp dir: %s" % statusStorageDir)
            if os.path.exists(statusStorageDir) == False:
                os.makedirs(statusStorageDir)
            statusStorage = os.path.join(statusStorageDir, "%s.pkl" % self.__uid)
            robot.auto_login(hotReload=True, statusStorageDir=statusStorage, loginCallback=login, exitCallback=logout, qrCallback=f, enableCmdQR=1 if self.debug_mode else False)
            #自动回复
            t = utils.run_in_thread(self.reply_fn, robot)
            robot.run(self.debug_mode)
        except:
            self.error(traceback.format_exc())

    def reply_fn(self, robot):
        if not self.message_queue:
            return
        self.info("auto reply is starting")
        while True:
            try:
                message = self.message_queue.get_nowait()
                uuid = utils.md5("%s%s" % (message['user'], message['auser']))
                if uuid not  in self.prepared_session:
                    for fn in self.prepare_reply:
                        fn(robot, uuid)
                    self.prepared_session.add(uuid)
                nick = message['nick']
                reply = self.get_message(message['msg'], uuid)
                if reply:
                    if nick:
                        reply = u'@%s\u2005%s' % (nick, reply)
                    robot.send(reply, message['user'])
                time.sleep(0.1)
            except queue.Empty:
#                self.debug("queue is empty")
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.error(traceback.format_exc())
