import urllib.parse
import urllib.request
from datetime import datetime
import pytz
from config import settings


def get_now_str():
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    return now.strftime("%H:%M:%S")




def send_telegram_msg(token, chat_id, text):
	full_message = f"[{get_now_str()}] {text}"
	safe_text = urllib.parse.quote(full_message)
	url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={safe_text}"
	try:
		with urllib.request.urlopen(url, timeout=10) as response:
			return response.read().decode('utf-8')
	except Exception as e:
		print(f">>> [TG ERROR] Не удалось отправить сообщение: {e}", flush=True)
		return None


def notify_all(message: str):
    print(message, flush=True)
    for chat in settings.CHAT_IDS:
        try:
            send_telegram_msg(settings.TOKEN, chat, message)
        except:
            pass
