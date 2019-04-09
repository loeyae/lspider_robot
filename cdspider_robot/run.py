#! /usr/bin/python
#-*- coding: UTF-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"),
# see LICENSE for more details: http://www.apache.org/licenses/LICENSE-2.0.

__author__="Zhang Yi <loeyae@gmail.com>"
__date__ ="$2019-2-19 10:16:40$"


from cdspider.run import *

rdir = os.path.dirname(os.path.abspath(__file__))

@cli.command()
@click.option('--rebot-cls', default='cdspider_robot.robots.WxchatRobots', callback=load_cls, help='schedule name', show_default=True)
@click.option('--aichat-rpc', default='http://127.0.0.1:27777', help='robot rpc server', show_default=True)
@click.option('-u', '--uuid', help='唯一标识')
@click.pass_context
def wechat(ctx, rebot_cls, aichat_rpc, uuid):
    """
    web wechat
    """
    aichat_rpc = connect_rpc(ctx, None, aichat_rpc)
    rebot_cls = load_cls(ctx, None, rebot_cls)
    robot = rebot_cls(ctx, uuid=uuid)
    reply = lambda m, s: aichat_rpc.reply(m, s)
    def init_aichat(m, s):
        info = m.search_friends()
        k = {
            'name': info['NickName'],
            'age': 18,
            'sex': '男' if info['Sex'] != 1 else '女'
        }
        aichat_rpc.init(k, s)
    init = lambda m, s: init_aichat(m, s)
    robot.add_prepare_reply(init)
    robot.set_reply(reply)
    robot.run()

@cli.command()
@click.option('--rebot-cls', default='cdspider_robot.robots.AichatRobots', callback=load_cls, help='schedule name', show_default=True)
@click.option('-u', '--uuid', default=None, help='唯一标识', show_default=True)
@click.option('-b', '--bot-data', default=os.path.join(rdir, 'config', 'aiml'), help='AI头脑文件目录', show_default=True)
@click.option('-c', '--commands', multiple=True, help='commands')
@click.pass_context
def aichat(ctx, rebot_cls, uuid, bot_data, commands):
    """
    Aiml bot
    """
    rebot_cls = load_cls(ctx, None, rebot_cls)
    robot = rebot_cls(ctx, commands = commands, bot_data = bot_data)
    robot.run(uuid)

@cli.command()
@click.option('--rebot-cls', default='cdspider_robot.robots.AichatRobots', callback=load_cls, help='rebot name', show_default=True)
@click.option('-b', '--bot-data', default=os.path.join(rdir, 'config', 'aiml'), help='AI头脑文件目录', show_default=True)
@click.option('-c', '--commands', multiple=True, help='commands')
@click.option('-s', '--settings', default=None, multiple=True, help='bot settings: [name, sex, age, company]', show_default=True)
@click.option('--xmlrpc-host', default='0.0.0.0', help="xmlrpc bind host", show_default=True)
@click.option('--xmlrpc-port', default=27777, help="xmlrpc bind port", show_default=True)
@click.option('--debug', default=False, is_flag=True, help='debug模式', show_default=True)
@click.pass_context
def aichat_rpc(ctx, rebot_cls, bot_data, commands, settings, xmlrpc_host, xmlrpc_port, debug):
    """
    Aiml bot rpc
    """
    rebot_cls = load_cls(ctx, None, rebot_cls)
    robot = rebot_cls(ctx, commands = commands, bot_data = bot_data, settings = settings)
    robot.xmlrpc_run(xmlrpc_port, xmlrpc_host)

@cli.command()
@click.option('--aichat-rpc', default='http://127.0.0.1:27777', help='robot rpc server')
@click.pass_context
def aichat_rpc_hello(ctx, aichat_rpc):
    """
    测试Aiml bot rpc
    """
    g = ctx.obj
    aichat_rpc = connect_rpc(ctx, None, aichat_rpc)
    print(aichat_rpc.hello())

if __name__ == "__main__":
    main()
