#-*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"),
# see LICENSE for more details: http://www.apache.org/licenses/LICENSE-2.0.

"""
:author:  Zhang Yi <loeyae@gmail.com>
:date:    2018-8-4 21:43:09
"""
import time
import pymongo
from ..base import WechatRobotGroupChatDB as BaseWechatRobotGroupChatDB
from cdspider.database.mongo import Mongo

class WechatRobotGroupChatDB(Mongo, BaseWechatRobotGroupChatDB):
    """
    wechat_robot_group_chat data object
    """
    __tablename__ = 'wechat_robot_group_chat'

    def __init__(self, connector, table=None, **kwargs):
        super(WechatRobotGroupChatDB, self).__init__(connector, table = table, **kwargs)
        collection = self._db.get_collection(self.table)
        indexes = collection.index_information()
        if 'IUin' not  in indexes:
            collection.create_index('IUin', name='IUin')
        if 'MsgId' not  in indexes:
            collection.create_index('MsgId', name='MsgId')
        if 'ctime' not  in indexes:
            collection.create_index('ctime', name='ctime')

    def insert(self, obj = {}):
        obj.setdefault('ctime', int(time.time()))
        super(WechatRobotGroupChatDB, self).insert(setting=obj)
        return obj['MsgId']
