import random
import mail
import PySimpleGUI as sg

from tinydb import TinyDB, Query
from threading import Thread

#sg.theme('DarkAmber')    # Keep things interesting for your users

def pretty_print_law(law):
    return f"{law['Number']}\n\n{law['Text']}\n\n{law['Law']}\n\n"

def pretty_print_thiking(bias):
    return f"{bias['Number']}\n\n{bias['Title']}\n\n{bias['Text']}\n\n"

def pretty_print_fable(fable):
    return f"{fable['Text']}"

def pretty_print_anti_seducer(sed):
    return f"{sed['Text']}"

def conver_user_table_data(users):
    return [list(user.values()) for user in users] 

db = TinyDB("./data/db.json")


law_send_to_users_layout = [[sg.Text("Send message to users in table")],
                            [sg.Button("Delete user", key="delete_user"), sg.Button("Add user", key="add_user"), sg.Button("Edit User", key="edit_user")],
                            [sg.Table([], headings=["Phone", "Name", "Mail"], col_widths=[20, 30, 30],
                                      justification="left",
                                      key="users_table",
                                      select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                      auto_size_columns=False,
                                      enable_events=True,
                                      alternating_row_color="black")],
                            [sg.Combo(["Daily Laws", "Thinking Critically", "Fables", "Anti Seducers"], key="text_type", default_value="Daily Laws"), \
                             sg.Button('Pick at random', key="users_pick_random_text"), \
                             sg.Button("Send to all users", key="users_send_all_mail")],
                            [sg.Multiline(key="users_law"+sg.WRITE_ONLY_KEY, size=(100, 20), font="Ariel 10")],
                            [sg.Exit()]]


layout = law_send_to_users_layout


window = sg.Window("Nice texts sender", layout, finalize=True)

def process_edituser_windown(element_name):
    users = db.table('users')
    user = users.get(Query()['Name'] == element_name)
    edit_user_layout = [[sg.Text("User Name"), sg.Input(key="Name", default_text=user["Name"])],
                        [sg.Text("User mail"), sg.Input(key="Mail", default_text=user["Mail"])],
                        [sg.Text("User Number"),sg.Input(key="Number", default_text=user["Number"])],
                        [sg.Button("Confirm", key="confirm_useredit"), sg.Exit()]]
    edit_windown = sg.Window("Edit user", edit_user_layout)
    while True:
        event, values = edit_windown.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'confirm_useredit':
            users.update(values, Query()['Name'] == element_name)
            data = conver_user_table_data(users)
            window["users_table"].update(data)
            break

    edit_windown.close()

def process_adduser_windown():
    add_user_layout = [[sg.Text("User Name"), sg.Input(key="Name")],
                       [sg.Text("User mail"), sg.Input(key="Mail")],
                       [sg.Text("User Number"),sg.Input(key="Number")],
                       [sg.Button("Confirm", key="confirm_useradd"), sg.Exit()]]

    add_windown = sg.Window("Add user", add_user_layout)
    while True:
        event, values = add_windown.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'confirm_useradd':
            users = db.table('users')
            users.insert(values)
            data = conver_user_table_data(users)
            window["users_table"].update(data)
            break

    add_windown.close()


def program_init():
    users = db.table('users').all()
    data = conver_user_table_data(users)
    window["users_table"].update(data)

program_init()

while True:
    event, values = window.read()
    #print(event, values)

    # Pick law events
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == "pick_random":
        laws = db.table('laws').all()
        law = random.choice(laws)
        text = pretty_print_law(law)
        window["multiline"+sg.WRITE_ONLY_KEY].update("")
        window["multiline"+sg.WRITE_ONLY_KEY].print(text)

    # User handle
    if event == "add_user":
        process_adduser_windown()
    if event == "delete_user":
        if len(values["users_table"]) != 0:
            val_idx = values["users_table"][0]
            element_name = window["users_table"].get()[val_idx][1]
            users = db.table('users')
            users.remove(Query()['Name'] == element_name)
            data = conver_user_table_data(users)
            window["users_table"].update(data)
    if event == "edit_user":
        if len(values["users_table"]) != 0:
            val_idx = values["users_table"][0]
            element_name = window["users_table"].get()[val_idx][1]
            process_edituser_windown(element_name)

    # Pick random text
    if event == "users_pick_random_text":
        print(values["text_type"])
        if values["text_type"] == "Anti Seducers":
            anti_seds = db.table('seduction_antiseducers').all()
            anti_sed = random.choice(anti_seds)
            text = pretty_print_anti_seducer(anti_sed)
        elif values["text_type"] == "Fables":
            fables = db.table('fables').all()
            fable = random.choice(fables)
            text = pretty_print_fable(fable)
        elif values["text_type"] == "Thinking Critically":
            biases = db.table('thinking').all()
            bias = random.choice(biases)
            text = pretty_print_thiking(bias)
        else:
            laws = db.table('laws').all()
            law = random.choice(laws)
            text = pretty_print_law(law)

        window["users_law"+sg.WRITE_ONLY_KEY].update("")
        window["users_law"+sg.WRITE_ONLY_KEY].print(text)
    if event == "users_send_all_mail":
        text = window["users_law"+sg.WRITE_ONLY_KEY].get()
        if len(text) != 0:
            users = db.table('users').all()
            mail_pwd = open("./mail_info/app_pwd", "r").read()
            mail_addr = open("./mail_info/app_mail", "r").read()
            for user in  users:
                mail_thread = Thread(target=mail.send_mail, args=(mail_addr, mail_pwd, user["Mail"], text))
                mail_thread.start()
            sg.Popup('Mails sent')
        else:
            sg.Popup('No message selected', button_type=sg.POPUP_BUTTONS_ERROR)

window.close()

