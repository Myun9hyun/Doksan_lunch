import requests
import telegram
import telegram.ext
import pytesseract
from PIL import Image
from io import BytesIO
import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 텔레그램 봇의 API Token 입력
bot_token = '6195947976:AAEa3VigwvB8vHIoTCgu7NM5YT63pNoqE8U'
bot = telegram.Bot(token=bot_token)
# 텔레그램 봇 객체 생성
updater = telegram.ext.Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher

# 크롤링 함수
def crawl_images(store_id):
    url = f"https://pf-wapi.kakao.com/web/profiles/{store_id}/posts"
    response = requests.get(url)
    json = response.json()
    images = []
    for post in json['items']:
        for media in post.get('media', []):
            if media.get('type') == 'image':
                images.append(media['large_url'])
    return images

# 이미지에서 텍스트 추출 함수
def extract_text_from_image(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(image, lang='kor')
    return text.strip()


# # /menu 명령어 처리 함수
# def handle_menu_command(update, context):
#     chat_id = update.effective_chat.id
#     store_id = "_xfWxfCxj" # 갈까밥상의 store_id
#     images = crawl_images(store_id)
#     if not images:
#         message = "메뉴 정보를 찾을 수 없습니다."
#     else:
#         message = ""
#         for image_url in images[:3]:
#             text = extract_text_from_image(image_url)
#             message += f"{text}\n"
#     bot.send_message(chat_id=chat_id, text=message)
# /menu 명령어 처리 함수
def handle_menu_command(update, context):
    chat_id = update.effective_chat.id
    store_id = "_xfWxfCxj" # 갈까밥상의 store_id
    images = crawl_images(store_id)
    if not images:
        message = "메뉴 정보를 찾을 수 없습니다."
    else:
        for i, image in enumerate(images[:3]):
            text = extract_text_from_image(image)
            message = f"메뉴 {i+1}:\n{text}"
            bot.send_photo(chat_id=chat_id, photo=image, caption=message)


# 정오에 메뉴 전송
def send_menu_at_noon(context: telegram.ext.CallbackContext):
    chat_id = "CHAT_ID" # 채팅방 ID
    store_id = "_xfWxfCxj" # 갈까밥상의 store_id
    images = crawl_images(store_id)
    if not images:
        message = "메뉴 정보를 찾을 수 없습니다."
    else:
        message = ""
        for image_url in images[:3]:
            text = extract_text_from_image(image_url)
            message += f"{text}\n"
    bot.send_message(chat_id=chat_id, text=message)

# 텔레그램 봇에 정오에 메뉴 전송 함수 등록
job_queue = updater.job_queue
job_queue.run_daily(send_menu_at_noon, time=datetime.time(hour=12, minute=0, second=0), context=None)

# 텔레그램 봇에 /menu 명령어 처리 함수 등록
dispatcher.add_handler(telegram.ext.CommandHandler('menu', handle_menu_command))

# 텔레그램 봇 시작
updater.start_polling()
