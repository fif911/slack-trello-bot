import os, slackclient
from trello import TrelloApi
from datetime import datetime,timedelta
import pprint
print( datetime.now())
trello = TrelloApi("4e62c19237c9761ef8c1270806619937")
trello.set_token('1d8ef5be08601172633e9a507542323ded7ab3e7039c273db6949cd3c49a1f0b')
def create_or_pass_files():
    file1_exist=os.path.isfile("task_list.txt")
    file2_exist=os.path.isfile("board_info.txt")
    if not file1_exist:
        file1 = open("task_list.txt", 'w+')
        file1.close()
    else:
        pass
    if not file2_exist:
        file2 = open("board_info.txt", 'w+')
        file2.close()
    else:
        pass

VALET_SLACK_NAME = os.environ.get('VALET_SLACK_NAME')
VALET_SLACK_NAME='megatron'
VALET_SLACK_TOKEN = os.environ.get('VALET_SLACK_TOKEN')
VALET_SLACK_TOKEN='xoxb-204879127824-DpfdsBMLyEGjRyV1rgPfTUdu'
# initialize slack client
valet_slack_client = slackclient.SlackClient(VALET_SLACK_TOKEN)
# check if everything is alright
create_or_pass_files()
is_ok = valet_slack_client.api_call("users.list").get('ok')
# info = trello.lists.new("name","594e714b01b2bf68d672c0ce")
# pprint.pprint(info)

if(is_ok):
    for user in valet_slack_client.api_call("users.list").get('members'):
        if user.get('name') == VALET_SLACK_NAME:
            print(user.get('id'))
            print('___________')
            if user.get('name')!="slackbot":
                print(user.get('name'))
                # created_list = trello.lists.new(user.get('name'),"594e714b01b2bf68d672c0ce")
                # with open('board_info.txt', 'a', encoding='utf-8') as file:
                #     file.seek(0)
                #     file.write("\n"+user.get('name')+"##"+created_list.get('id'))
###<@U0NQHJYNS>## vasa##2017-06-30 13:44:48##C5ZBRV5EG##hidden###<@U0NQHJYNS>##na na##2017-06-30 14:09:23##C5ZBRV5EG##show##<@U23EZGNHH>###<@U0NQHJYNS>##<@U2USHFNJ0> fdgdsgfsdg##2017-06-30 14:10:24##C5ZBRV5EG##show##<@U23EZGNHH>###<@U0NQHJYNS>##<@U5THRECUD> <@U0MSGLE1W> ddfbdvbdfvdfs##2017-06-30 14:10:50##C5ZBRV5EG##show##<@U23EZGNHH>###<@U0NQHJYNS>##lfdhkjldfsvjksvkjsv @t <@U0MSGLE1W>##2017-06-30 14:11:57##C5ZBRV5EG##show##<@U23EZGNHH>###<@U5THRECUD>##sss##2017-06-30 14:19:16##C5ZBRV5EG##show###

