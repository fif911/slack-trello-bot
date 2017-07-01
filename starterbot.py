import shutil
from trello import TrelloApi
import os, slackclient, time
import random
from datetime import datetime, timedelta
# --------------------------- CONSTANTS AND API

BOT_SLACK_TOKEN = "BOT SLACK TOKEN HERE"

trello = TrelloApi("905145fc51f29a1777f509d92ba8ba89")
trello.set_token("fd94100903a3bac516258849865a9040a291d7af82599d55c8cc2c336cb547ea")
SOCKET_DELAY = 1
VALET_SLACK_ID = "U60RV3RQ8"
VALET_SLACK_NAME = 'megatron'
valet_slack_client = slackclient.SlackClient(BOT_SLACK_TOKEN)
EVERY_DAY_REMIND_HOUR = datetime.now().replace(hour=17, minute=00, second=00)

# --------------------------- METHODS
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


def get_board_id():
    with open('board_info.txt', 'r', encoding='utf-8') as file:
        file.seek(0)
        line = file.readline()

        if line[-2:]=="\n":
            line = line[:-2]
        return line.strip()

def get_username(user_id):

    for user in valet_slack_client.api_call("users.list").get('members'):

        if user.get('id') == user_id:
            return (user.get('name'))

def update_board_id(new_board_id):
    with open('board_info.txt', 'r+', encoding='utf-8') as old_file:
        with open('board_info.txt', 'r+', encoding='utf-8') as file:
            old_file.readline()  # and discard
            file.write(new_board_id+"\n")
            shutil.copyfileobj(old_file, file)
    return new_board_id

# get_board_id()
def get_table_id(username):

    with open('board_info.txt', 'r', encoding='utf-8') as file:
        file.seek(0)
        next(file)
        for line in file:
            line=line.strip()
            if line !="":
                line_info=line.split("##")
                if line_info[0]==username:
                    return line_info[1]


# TODO SLACK Specific
def is_private(event):
    """Checks if on a private slack channel"""
    channel = event.get('channel')
    return channel.startswith('D')


def post_message(message, channel):
    valet_slack_client.api_call('chat.postMessage', channel=channel,
                          text=message, as_user=True)

# how the user is mentioned on slack
def get_mention(user):

    return '<@{user}>'.format(user=user)

valet_slack_mention = get_mention(VALET_SLACK_ID)


# TODO Language Specific
def is_for_me(event):
    """Know if the message is dedicated to me"""
    # check if not my own event

    type = event.get('type')

    if type and type == 'message' and not(event.get('user') == VALET_SLACK_ID):

        if is_private(event):
            return True
        text = event.get('text')
        # channel = event.get('channel')
        if type and type == 'message' and text.startswith("@td "):
            return True
        if type and type == 'message' and text.startswith("@t"):
            return True
        if type and type == 'message' and text.startswith("@cl"):
            return True
        if valet_slack_mention in text.strip().split():
            return True


def say_hi(user_mention):
    """Say Hi to a user by formatting their mention"""
    response_template = random.choice(['Sup, {mention}...',
                                       'Yo!',
                                       'Hola {mention}',
                                       'Bonjour!'])
    return response_template.format(mention=user_mention)


def say_bye(user_mention):
    """Say Goodbye to a user"""
    response_template = random.choice(['see you later, alligator...',
                                       'adios amigo',
                                       'Bye {mention}!',
                                       'Au revoir!'])
    return response_template.format(mention=user_mention)



def handle_task(command, user, channel,related_user):

    username_author = get_username(user)
    user_mention = get_mention(user)
    remind_time = datetime.now() + timedelta(hours=1)
    if related_user=="None":
        response = "Ok. Task for " + user_mention + " is *" + command + ".* \n" \
        "I'll remind you in an hour (" + '{:%H:%M}'.format(remind_time) + ") and at the end of the day(5 p.m.)"


        card_description = "task created by **"+username_author+"**"
        created_card = trello.cards.new(command, get_table_id(username_author), desc=card_description)
    else:

        id_related_user_temp=related_user[:-1]
        id_related_user=id_related_user_temp[2:]

        username_related = get_username(id_related_user)

        response = "Ok. Task for " + related_user + " created by "+user_mention+" is *" + command + ".* \n" \
            "I'll remind "+related_user+" in an hour (" + '{:%H:%M}'.format(remind_time) + \
                   ") and at the end of the day(5 p.m.)"
        card_description = "task created by **" + username_author + "** to ** "+username_related+"**"
        created_card = trello.cards.new(command, get_table_id(username_related), desc=card_description)
    post_message(message=response, channel=channel)

    remind_time_for_trello= datetime.now() - timedelta(hours=6)
    trello.cards.update_due(created_card.get('id'), remind_time_for_trello)
    # trello.cards.new_label(created_card.get('id'), "orange")
    with open('task_list.txt', 'a', encoding='utf-8') as file:
        file.seek(0)
        if related_user=="None":
            file.write("###" + user_mention + "##" + command + "##" + remind_time.strftime(
            "%Y-%m-%d %H:%M:%S") + "##" + channel +"##"+"show" +"###")
        else:
            file.write("###" + user_mention + "##" + command + "##" + remind_time.strftime(
                "%Y-%m-%d %H:%M:%S") + "##" + channel + "##" + "show##" + related_user+"###")

def is_help(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens
               for g in ['help', '-help', 'heelp'])
def is_hi(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens
               for g in ['hello', 'bonjour', 'hey', 'hi', 'sup', 'morning', 'hola', 'ohai', 'yo'])


def is_bye(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens
               for g in ['bye', 'goodbye', 'revoir', 'adios', 'later', 'cya'])
def create_list(message,channel):
    board_id_was_uptaded = False
    try:
        message = message.split(' ', 1)[1]
        if message.strip() != "":
            try:
                shadow_board = trello.boards.get(board_id=message)
                try:
                    created_list_test=trello.lists.new("Permissions test",shadow_board.get('id'))
                    trello.lists.update(created_list_test.get('id'),closed="true")
                except:
                    post_message(":warning: \nI have no permissions to modify this board."
                                 " Add me to this board and then i can do it", channel)
                    return
            except:
                post_message(":warning: \nInvalid board id or board is private. Please try again.", channel)
                return
            board_id = update_board_id(message.strip())
            board_id_was_uptaded = True
    except:
        board_id = get_board_id()
    # trello.boards.get()
    os.remove("board_info.txt")

    with open('board_info.txt', 'a', encoding='utf-8') as file:
        file.seek(0)
        file.write(board_id)

        for user in valet_slack_client.api_call("users.list").get('members'):
            if user.get('name') != VALET_SLACK_NAME:
                if user.get('name') != "slackbot":
                    if not user.get('deleted') and not user.get('is_bot'):
                        created_list = trello.lists.new(user.get('name'), board_id)
                        file.write("\n" + user.get('name') + "##" + created_list.get('id'))

    if board_id_was_uptaded:
        post_message(":white_check_mark:\nLists for users was successfully created and board id updated", channel)
        global COMMANDS_AVAILABLE
        COMMANDS_AVAILABLE = True
    else:
        post_message(":white_check_mark:\nLists for users was successfully created", channel)
def in_message_spechial_char(message):
    if "##" in message:
        return True
    elif "###" in message:
        return True
    else:
        return False
def handle_message(message, user, channel,comands_availible):
    message = str(message).strip()
    if in_message_spechial_char(message):
        post_message("Omg. I saw MY spechial char in YOUR message :rage:."
                     " Don't use it pls. For more info type 'help'",channel)
        return
    print(message)
    if message.startswith("@cl "):
        create_list(message=message,channel=channel)

        return
    if not comands_availible:
        post_message(":warning:You can't use comands before definition Board id. To do it type: *@cl* + Board id",channel)
        return

    if message.startswith("@t "):
        related_user_linked=False
        try:
            task_splited = message.split(None, maxsplit=2)
            related_user = task_splited[1]
        except Exception as err:
            text_err = err
            post_message("Ups! Something went wrong: "+str(text_err),channel)
        else:

            if related_user=="<@"+VALET_SLACK_ID+">":
                post_message(message="Sorry, but you can't give assignments to me", channel=channel)
                return
            elif related_user.startswith("<@U"):
                handle_task(command=task_splited[2], user=user, channel=channel, related_user=related_user)
                related_user_linked=True
            if not related_user_linked:
                message = message.split(' ', 1)[1].strip()
                handle_task(command=message, user=user, channel=channel, related_user="None")
    elif message.startswith("@td "):
        task_text =message.split(None,maxsplit=1)[1]
        username=get_username(user)
        desc="task created by "+username+" and marked as 'done'."
        remind_time_for_trello = datetime.now() - timedelta(hours=7)
        created_card = trello.cards.new(task_text, get_table_id(username), desc=desc)
        trello.cards.update_due(created_card.get('id'), remind_time_for_trello)
        trello.cards.set_due_done(created_card.get('id'), "true")
        post_message("Ok. Task for "+get_mention(user)+" is *"+task_text+"*\nI won't reminde you about it.",channel)
    elif message.split(None,maxsplit=1)[0] == "@cl":
        create_list(message,channel)
    else:
        if message.split(None,maxsplit=1)[0] == "@clean":
            os.remove("task_list.txt")
            file = open("task_list.txt", "w+")
            file.close()
            post_message(":white_check_mark:\nMy remind list cleaned.\n"
                         ":warning: I won't remind you about tasks that were on that remind list",channel)
        elif is_help(message):
            help_text="Okkk. It's my little documentation :smile:.\n" \
                      "Pls use the following commands delimited by spaces:\n" \
                       "*@t* + task - To create a task for yourself\n" \
                       "*@t* + _@username_ - To create a task for someone\n" \
                       "*@td* + task - To create a task for yourself which will be marked as done on Trello." \
                      "(I won't remind you about it)\n" \
                       "*@cl* - To create new list on trello for each user in slack team\n" \
                       "*@cl* + _board id_- To create new list on trello for each user in slack team" \
                      " on the specified board and then work with it\n" \
                      "if i *working slow* you can clean my remind list by command *\'@clean\'*\n" \
                       "or just say hello to me :wink:\n" \
                       ":warning: Don't use '##' and '###' - *it's my special char!*"
            post_message(message=help_text,channel=channel)
        elif is_hi(message):
            user_mention = get_mention(user)
            post_message(message=say_hi(user_mention), channel=channel)
        elif is_bye(message):
            user_mention = get_mention(user)
            post_message(message=say_bye(user_mention), channel=channel)
        else:
            response = "Not sure what you mean. I'm just a bot, though! I can help you with executing simple commands. " \
                       "If you need more help you can type 'help' or '-help' or sm like this and i'll understand you :wink: "
            post_message(message=response, channel=channel)

def reminde_and_update_file(file,text,remind_time,user,task_list,channel,task,related_user):
    if related_user=="None":

        remind_message_no_related_user = "I must remind " + user + " about task: *" + text + "*.\nDid you do it?" \
                    " If yes please confirm it on Trello"

        post_message(remind_message_no_related_user, channel=channel)
        task_list[task_list.index(task)] = user + "##" + text + "##" + remind_time.strftime(
            "%Y-%m-%d %H:%M:%S") + "##" + channel + "##" + "hidden"
    else:
        remind_message_with_related_user =  user  + " ask me to remind " +related_user+ " about task: *" + text + "*.\n " \
            "Did you do it? If yes please confirm it on Trello"
        post_message(remind_message_with_related_user, channel=channel)
        task_list[task_list.index(task)] = user + "##" + text + "##" + remind_time.strftime(
            "%Y-%m-%d %H:%M:%S") + "##" + channel + "##" + "hidden##"+related_user
    text_in_file = "###"
    for task_iteam in task_list:
        text_in_file += task_iteam + "###"
    file.truncate()
    file.write(text_in_file)

def check_if_need_to_remind():
    with open('task_list.txt', 'r+', encoding='utf-8') as file:
        text_in_file = file.read()
        file.seek(0)

        if text_in_file.strip() != "":
            task_list = text_in_file.split("###")

            task_list = list(filter(None, task_list))
            cur_time = datetime.now()

            if cur_time + timedelta(seconds=5) >= EVERY_DAY_REMIND_HOUR >= cur_time - timedelta(seconds=5):
                for task in task_list:
                    task_info = task.split("##")
                    user = task_info[0]
                    text = task_info[1]
                    channel = task_info[3]
                    try:
                        related_user = task_info[5]
                        post_message("I'm just remind " + related_user + " about task: *" + text + "*. Did you done it?"
                                     , channel)
                    except:
                        post_message("I'm just remind "+user+" about task:*"+text+"*.Did you done it?",channel)

            for task in task_list:


                task_info = task.split("##")
                # get status to check if need to remind
                status = task_info[4]

                if status == "show":


                    remind_time = datetime.strptime(task_info[2], "%Y-%m-%d %H:%M:%S")
                    need_to_remind=(cur_time + timedelta(seconds=10) >= remind_time >= cur_time - timedelta(seconds=10))
                    if need_to_remind:
                        user = task_info[0]
                        text = task_info[1]

                        channel = task_info[3]
                        try:
                            related_user=task_info[5]
                            reminde_and_update_file(file, text, remind_time, user, task_list, channel, task,
                                                related_user)
                        except:
                            reminde_and_update_file(file, text, remind_time, user, task_list, channel, task,
                                                    related_user="None")
# --------------------------- RUN METHOD
create_or_pass_files()
try:
    '''Trying to get board id and check if it correct'''
    shadow_board_id = get_board_id()
    trello.boards.get(shadow_board_id)
except:
    COMMANDS_AVAILABLE = False
else:
    COMMANDS_AVAILABLE = True
# Bot Specific
def run():
    if valet_slack_client.rtm_connect():
        print('[.] Megatron is ON...')
        i = 0
        while True:
            event_list = valet_slack_client.rtm_read()

            if len(event_list) > 0:
                for event in event_list:
                    if is_for_me(event):
                        try:
                            handle_message(message=event.get('text'), user=event.get('user'),
                                           channel=event.get('channel'),comands_availible=COMMANDS_AVAILABLE)
                        except TimeoutError:
                            while_loop = True
                            while while_loop:
                                try:
                                    post_message("It seems like you have some problems with internet connection. Do you?",
                                        event.get('channel'))
                                except TimeoutError:
                                    time.sleep(5)
                                except:
                                    time.sleep(10)
                                else:
                                    while_loop = False
                        except Exception as err:
                            text_error=err
                            post_message("Ups! "+str(text_error), event.get('channel'))

            if i % 10 == 0:
                i=0
                check_if_need_to_remind()

            i+=1


            time.sleep(SOCKET_DELAY)
    else:
        print('[!] Connection to Slack failed!')

if __name__=='__main__':
    run()