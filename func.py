import time
import connector
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters
from config import TOKEN
import schedule

bot = telegram.Bot(token=TOKEN)


def start(update, context):
    try:
        connector.get_connection().keys()
        print('进入start函数')
        update.message.reply_text(
            '在呢！系统运行正常~',
        )
    except Exception as e:
        print(e)
        print('进入start函数')
        update.message.reply_text("系统故障，Redis连接失败，请检查！")
        update.message.reply_text("错误信息：" + str(e))


def chat_content_exec(update, context):
    try:
        r = connector.get_connection()
        text = update.message.text
        chat_type = update.effective_chat.type
        user_id = update.effective_user.id
        chat_id = update.effective_message.chat_id
        # 限制为群组
        if chat_type != "supergroup":
            return
        # 限制文字长度不能超过80字
        if len(text) > 80:
            return
        # 取消注释开启独享模式（仅授权群组可用）
        # if chat_id not in ["1231242141"]:
        #     return
        try:
            username = update.effective_user.username
        except Exception as e:
            username = update.effective_user.id
        user = update.message.from_user
        firstname = ""
        lastname = ""
        try:
            firstname = str(user["first_name"])
        except Exception as e:
            print(e)
            print("用户没有设置 firstname")
        try:
            lastname = str(user["last_name"])
        except Exception as e:
            print(e)
            print("用户没有设置 last_name")
        if len(firstname) == 0 and len(lastname) == 0:
            name = username
        elif len(firstname) == 0 and len(lastname) != 0:
            name = lastname
        elif len(firstname) != 0 and len(lastname) == 0:
            name = firstname
        elif len(firstname) != 0 and len(lastname) != 0:
            name = firstname + " " + lastname
        print("\n---------------------------")
        print("内容: " + text[:10])
        print("群组类型: " + str(chat_type))
        print("用户ID: " + str(user_id))
        print("chat_id: " + str(chat_id))
        if "/" in text:
            print("这是一条指令信息，跳过")
            return
        else:
            if text[-1] not in ["，", "。", "！", "：", "？", "!", "?", ",", ":", "."]:
                r.append("{}_chat_content".format(chat_id), text + "。")
            else:
                r.append("{}_chat_content".format(chat_id), text)
            r.incrby("{}_total_message_amount".format(chat_id))
            r.hincrby("{}_user_message_amount".format(chat_id), name)
        print("---------------------------")
    except Exception as e:
        print(e)
        print("用户数据提取、入库错误")


def check_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


start_handler = CommandHandler('start', start)
chat_content_handler = MessageHandler(Filters.text, chat_content_exec)
