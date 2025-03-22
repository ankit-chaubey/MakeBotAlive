import requests
import os

CHAT_ID = os.getenv("CHAT_ID")  
OWNER_ID = os.getenv("OWNER_ID")  
BOT_TOKENS = os.getenv("BOT_TOKENS").split()  
PRIMARY_BOT_TOKEN = BOT_TOKENS[0]  
BASE_TELEGRAM_URL = "https://api.telegram.org/bot"

def send_telegram_message(bot_token, chat_id, text):
    url = f"{BASE_TELEGRAM_URL}{bot_token}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text}).json()
        if not response.get("ok"):
            report_error("sendMessage", bot_token, response)
    except Exception as e:
        report_error("sendMessage", bot_token, str(e))

def send_telegram_document(bot_token, chat_id, file_path, caption):
    url = f"{BASE_TELEGRAM_URL}{bot_token}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            response = requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"document": file}).json()
            if not response.get("ok"):
                report_error("sendDocument", bot_token, response)
    except Exception as e:
        report_error("sendDocument", bot_token, str(e))

def report_error(request_type, bot_token, error_data):
    error_message = (
        f"⚠️ Error Detected!\n"
        f"Request: {request_type}\n"
        f"Bot Token Used: {bot_token}\n"
        f"Error Details: {error_data}\n\n"
        f"Please check manually."
    )
    send_telegram_message(PRIMARY_BOT_TOKEN, OWNER_ID, error_message)

def check_bot_status(bot_token):
    bot_info_url = f"{BASE_TELEGRAM_URL}{bot_token}/getMe"
    updates_url = f"{BASE_TELEGRAM_URL}{bot_token}/getUpdates"
    
    try:
        bot_info = requests.get(bot_info_url).json()
        if not bot_info.get("ok"):
            report_error("getMe", bot_token, bot_info)
            return None, None, False
        
        bot_id = bot_info["result"]["id"]
        bot_username = bot_info["result"].get("username", "Unknown")
        bot_name = bot_info["result"]["first_name"]
        file_name = f"Bot{bot_id}.txt"

        try:
            updates = requests.get(updates_url).json()
            if not updates.get("ok"):
                report_error("getUpdates", bot_token, updates)
        except Exception as e:
            report_error("getUpdates", bot_token, str(e))
            updates = "Failed to fetch updates"

        with open(file_name, "w") as file:
            file.write(
                f"BotID: {bot_id}\n"
                f"BotUsername: @{bot_username}\n"
                f"Name: {bot_name}\n\n"
                f"Updates:\n{updates}\n"
                f"------------------------------------\n"
            )

        return bot_id, file_name, True
    except Exception as e:
        report_error("getMe", bot_token, str(e))
        return None, None, False

def main():
    for bot_token in BOT_TOKENS:
        bot_id, file_name, success = check_bot_status(bot_token)
        if success:
            send_telegram_document(bot_token, CHAT_ID, file_name, f"✅ #Bot{bot_id} is online")

if __name__ == "__main__":
    main()
