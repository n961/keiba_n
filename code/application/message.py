from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import os


class LineBotMessenger:

    def __init__(self):
        self.line_bot_api = LineBotApi(os.environ['LINEBOTKEY'])
        self.groupId =os.environ['GROUPID']

    def bet_message(self, race_id, number):
        text = f'馬券購入\nレースID: {race_id}\n馬番: {number}'
        self._message(text)

    def error_message(self, method):
        text = f'処理中にエラーが発生しました\n処理名: {method}'
        self._message(text)

    def _message(self, text):
        try:
            self.line_bot_api.push_message(self.groupId, TextSendMessage(text=text))
        except LineBotApiError as e:
            print(e)