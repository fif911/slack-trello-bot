from trello import TrelloApi
from datetime import datetime,timedelta
import pprint
print( datetime.now())
trello = TrelloApi("4e62c19237c9761ef8c1270806619937")
trello.set_token('1d8ef5be08601172633e9a507542323ded7ab3e7039c273db6949cd3c49a1f0b')

remind_time = datetime.now() - timedelta(hours=2)
created_card = trello.cards.new("new", "594e739b8ccf77c3c1e776f2", desc="name of the autor here")

# info = trello.boards.get("594e714b01b2bf68d672c0ce")
# pprint.pprint(trello.lists.get_action("594e739b8ccf77c3c1e776f2"))
# pprint.pprint(info)
trello.cards.update_due(created_card.get('id'), remind_time)

trello.cards.new_label(created_card.get('id'),"orange")
trello.cards.delete_label_color("orange",created_card.get('id'))
#when done
trello.cards.set_due_done(created_card.get('id'), "true")
# trello.cards.new_label(created_card.get('id'),"green")
#
# 59537a667a7818b19dd664fb
# a.zakotyanskyi##5954d2f54c7dcb22de81a5a6
# ok_shelest##5954d2f6f685b669f07db108

