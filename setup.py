# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"),
# see LICENSE for more details: http://www.apache.org/licenses/LICENSE-2.0.

__author__ = "Zhang Yi <loeyae@gmail.com>"
__date__ = "$2019-2-19 9:16:07$"

from setuptools import setup, find_packages

setup(
    name="cdspider_robot",
    version="0.1.3",
    description="数据采集框架聊天机器人",
    author='Zhang Yi',
    author_email='loeyae@gmail.com',
    license="Apache License, Version 2.0",
    url="https://github.com/loeyae/lspider_robot.git",
    install_requires=[
        'aiml>=0.9.1'
        'itchat>=1.3.10',
        'cdspider>=0.1.4',
    ],
    packages=find_packages(),

    package_data={
        'cdspider_robot': [
            'config/*.conf',
            'config/*.json',
            'config/aiml/*.aiml',
            'config/aiml/*.xml',
        ]
    },
    entry_points={
        'console_scripts': [
            'cdspider_robot = cdspider_robot.run:main',
        ],
        'cdspider.robots': [
            'wxchat=cdspider_robot.robots:WxchatRobots',
            'aichat=cdspider_robot.robots:AichatRobots',
        ],
        'cdspider.dao.mongo': [
            'WechatRobotChatInfoDB=cdspider_robot.database.mongo:WechatRobotChatInfoDB',
            'WechatRobotChatRoomsDB=cdspider_robot.database.mongo:WechatRobotChatRoomsDB',
            'WechatRobotFriendsDB=cdspider_robot.database.mongo:WechatRobotFriendsDB',
            'WechatRobotGroupChatDB=cdspider_robot.database.mongo:WechatRobotGroupChatDB',
            'WechatRobotInfoDB=cdspider_robot.database.mongo:WechatRobotInfoDB',
            'WechatRobotMpsChatDB=cdspider_robot.database.mongo:WechatRobotMpsChatDB',
            'WechatRobotMpsSharingDB=cdspider_robot.database.mongo:WechatRobotMpsSharingDB',
        ]
    }
)
