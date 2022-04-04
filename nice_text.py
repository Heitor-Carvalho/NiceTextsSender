import random
import sys
import argparse
import mail
import pywhatkit

from tinydb import TinyDB

def pretty_print_law(law):
    return f"{law['Number']}\n\n{law['Text']}\n\n{law['Law']}\n\n"

def pretty_print_thiking(bias):
    return f"{bias['Number']}\n\n{bias['Title']}\n\n{bias['Text']}\n\n"

def pretty_print_fable(fable):
    return f"{fable['Text']}"

def main():
    db = TinyDB("./data/db.json")

    laws = db.table('laws').all()
    biases = db.table('thinking').all()
    fables = db.table('fables').all()
    users = db.table('users').all()

    try:
        sender_pwd = open("./mail_info/app_pwd", "r").read()
        sender_mail = open("./mail_info/app_mail", "r").read()
    except Exception as e:
        print(e)
        sys.exit(-1)

    parse_cmds = argparse.ArgumentParser(description='Comands to get daily laws from Robert Greene')
    parse_cmds.add_argument('--text', type=str, required=False,
                            default="laws", dest='text_type', choices=["laws", "thinking", "fables"],
                            help='Choose text type')
    parse_cmds.add_argument('--display_mode', type=str, required=False,
                            default="bash", dest='display_mode', choices=["bash", "mail", "whats"],
                            help='Pick a law at random')
    args = parse_cmds.parse_args()

    if args.text_type == "fables":
        fable = random.choice(fables)
        text = pretty_print_fable(fable)
    elif args.text_type == "thinking":
        bias = random.choice(biases)
        text = pretty_print_thiking(bias)
    else:
        law = random.choice(laws)
        text = pretty_print_law(law)

    if (args.display_mode == "bash"):
        print(text)
    elif (args.display_mode == "whats"):
        for user in users:
            print(f"Sending messege to user {user['Name']}")
            pywhatkit.sendwhatmsg_instantly(user["Number"], text, wait_time=15)
    elif (args.display_mode == "mail"):
        for user in users:
            print(f"Sending messege to user {user['Name']}")
            mail.send_mail(sender_mail, sender_pwd, user["Mail"], text)
    else:
        print("Method not implemented")


if __name__ == "__main__":
    main()
