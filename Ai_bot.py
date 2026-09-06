import sys
import random
import datetime
import json
import os
import re
import html
import hashlib
import secrets
from ddgs import DDGS
import sympy as sp
import ollama
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton,
                           QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox,
                           QMenu)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QAction, QActionGroup

BOT_NAME = "Harris"
OLLAMA_MODEL = "llama3.2"
SETTINGS_FILE = "settings.json"

LANGUAGES = {
    "vi": {
        "label": "Tiếng Việt",
        "system_prompt": (
            f"Bạn là {BOT_NAME}, một trợ lý ảo thân thiện, dí dỏm nhẹ nhàng nhưng lịch sự. "
            "LUÔN LUÔN trả lời bằng tiếng Việt, bất kể người dùng viết bằng ngôn ngữ nào. "
            "Trả lời ngắn gọn, tự nhiên như đang nhắn tin, không chửi thề, "
            "không dài dòng trừ khi người dùng cần giải thích kỹ. "
            "Bạn thành thạo lập trình với các ngôn ngữ: C, C++, Java, JavaScript, TypeScript, "
            "C#, Go (Golang) và Rust. Khi được yêu cầu viết code, hãy viết code đúng, sạch, "
            "chạy được, luôn đặt trong khối markdown có gắn tên ngôn ngữ "
            "(ví dụ ```cpp ... ```, ```java ... ```, ```go ... ```), và chỉ giải thích ngắn gọn "
            "bên dưới nếu người dùng cần."
        ),
        "greeting": "Xin chào, mình là Harris! Trợ lý cá nhân của bạn. Hỏi mình bất cứ điều gì nhé, Tôi biết tất cả mọi thứ.",
        "thinking": "Đang suy nghĩ...",
        "you": "Bạn",
        "send": "Gửi",
        "clear": "🗑 Xóa chat",
        "save": "💾 Lưu chat",
        "placeholder": "Nhập tin nhắn... (Enter = gửi, Shift+Enter = xuống dòng)",
        "empty_input": "Bạn muốn hỏi gì nào? 🙂",
        "who_are_you": f"Mình là {BOT_NAME} — trợ lý cá nhân của bạn, có thể tính toán, tra cứu và trò chuyện.",
        "no_gender": "Mình là AI thôi, không có giới tính hay xu hướng gì cả 😄",
        "now_is": lambda t, d: f"Bây giờ là **{t}**, ngày **{d}**.",
        "saved_chat": "💾 Đã lưu lịch sử chat vào chat_history.txt",
        "save_error": lambda e: f"⚠️ Không lưu được: {e}",
        "settings_menu_title": "🌐 Ngôn ngữ trả lời",
        "language_changed": lambda name: f"🌐 Đã chuyển ngôn ngữ trả lời sang **{name}**.",
        "translating": "🌐 Đang dịch lại các câu trả lời trước đó, chờ chút nhé...",
        "logout": "🚪 Đăng xuất",
        "logout_confirm_title": "Đăng xuất",
        "logout_confirm_message": "Bạn có chắc muốn đăng xuất không?",
    },
    "en": {
        "label": "English",
        "system_prompt": (
            f"You are {BOT_NAME}, a friendly, lightly witty but polite virtual assistant. "
            "ALWAYS answer in English, no matter what language the user writes in. "
            "Keep replies short and natural, like a chat message, no swearing, "
            "and don't ramble unless the user needs a detailed explanation. "
            "You are skilled at programming in C, C++, Java, JavaScript, TypeScript, C#, "
            "Go (Golang), and Rust. When asked to write code, produce correct, clean, "
            "runnable code inside a markdown code block tagged with the language "
            "(e.g. ```cpp ... ```, ```java ... ```, ```go ... ```), and only add a short "
            "explanation below if the user needs one."
        ),
        "greeting": "Hello, I'm Harris! Your personal helper friend. Ask me anything, I know everything.",
        "thinking": "Thinking...",
        "you": "You",
        "send": "Send",
        "clear": "🗑 Clear chat",
        "save": "💾 Save chat",
        "placeholder": "Type a message... (Enter = send, Shift+Enter = new line)",
        "empty_input": "What would you like to ask? 🙂",
        "who_are_you": f"I'm {BOT_NAME} — your personal assistant, I can do math, look things up, and chat.",
        "no_gender": "I'm just an AI, no gender or orientation here 😄",
        "now_is": lambda t, d: f"It's **{t}**, on **{d}**.",
        "saved_chat": "💾 Chat history saved to chat_history.txt",
        "save_error": lambda e: f"⚠️ Couldn't save: {e}",
        "settings_menu_title": "🌐 Reply language",
        "language_changed": lambda name: f"🌐 Reply language switched to **{name}**.",
        "translating": "🌐 Translating previous replies, hold on...",
        "logout": "🚪 Log out",
        "logout_confirm_title": "Log out",
        "logout_confirm_message": "Are you sure you want to log out?",
    },
    "ja": {
        "label": "日本語",
        "system_prompt": (
            f"あなたは{BOT_NAME}という、親しみやすく礼儀正しい、少しユーモアのあるAIアシスタントです。"
            "ユーザーがどの言語で書いても、必ず日本語で返答してください。"
            "返信は短く自然に、チャットのように。下品な言葉は使わず、"
            "ユーザーが詳しい説明を求めない限り長くしないでください。"
            "あなたはC、C++、Java、JavaScript、TypeScript、C#、Go（Golang）、Rustでの"
            "プログラミングが得意です。コードを書くよう頼まれたら、正しく動作する"
            "きれいなコードを、言語名を付けたMarkdownのコードブロック（例: ```cpp ... ```、"
            "```java ... ```、```go ... ```）で書いてください。説明はユーザーが求めた場合のみ"
            "簡潔に添えてください。"
        ),
        "greeting": "こんにちは、ハリスです！あなたの個人的なサポーターであり、友達でもあります。何でも聞いてくださいね。何でも知っていますから。",
        "thinking": "考え中...",
        "you": "あなた",
        "send": "送信",
        "clear": "🗑 チャットを削除",
        "save": "💾 チャットを保存",
        "placeholder": "メッセージを入力...（Enter = 送信、Shift+Enter = 改行）",
        "empty_input": "何を聞きたいですか？🙂",
        "who_are_you": f"私は{BOT_NAME}です — 計算、検索、会話ができるあなたの個人アシスタントです。",
        "no_gender": "私はAIなので、性別や性的指向はありません😄",
        "now_is": lambda t, d: f"現在の時刻は **{t}**、日付は **{d}** です。",
        "saved_chat": "💾 チャット履歴を chat_history.txt に保存しました",
        "save_error": lambda e: f"⚠️ 保存できませんでした: {e}",
        "settings_menu_title": "🌐 返信言語",
        "language_changed": lambda name: f"🌐 返信言語を **{name}** に変更しました。",
        "translating": "🌐 これまでの返信を翻訳しています、少々お待ちください...",
        "logout": "🚪 ログアウト",
        "logout_confirm_title": "ログアウト",
        "logout_confirm_message": "本当にログアウトしますか？",
    },
    "ko": {
        "label": "한국어",
        "system_prompt": (
            f"당신은 {BOT_NAME}이라는 친근하고 예의 바르며 약간 재치 있는 AI 비서입니다. "
            "사용자가 어떤 언어로 쓰든 항상 한국어로만 답하세요. "
            "대답은 짧고 자연스럽게, 채팅하듯이 하세요. 욕설은 쓰지 말고, "
            "사용자가 자세한 설명을 원하지 않는 한 길게 늘어놓지 마세요. "
            "당신은 C, C++, Java, JavaScript, TypeScript, C#, Go(Golang), Rust 프로그래밍에 "
            "능숙합니다. 코드를 작성해 달라는 요청을 받으면 정확하고 깔끔하며 실행 가능한 "
            "코드를 언어 태그가 붙은 마크다운 코드 블록(예: ```cpp ... ```, ```java ... ```, "
            "```go ... ```)으로 작성하고, 사용자가 필요로 할 때만 아래에 간단히 설명을 "
            "덧붙이세요."
        ),
        "greeting": "안녕하세요, 저는 해리스예요! 당신의 개인 도우미이자 친구죠. 무엇이든 물어보세요, 제가 다 알고 있거든요.",
        "thinking": "생각 중...",
        "you": "당신",
        "send": "전송",
        "clear": "🗑 대화 지우기",
        "save": "💾 대화 저장",
        "placeholder": "메시지를 입력하세요... (Enter = 전송, Shift+Enter = 줄바꿈)",
        "empty_input": "무엇을 물어보고 싶으세요? 🙂",
        "who_are_you": f"저는 {BOT_NAME}입니다 — 계산, 검색, 대화가 가능한 당신의 개인 비서예요.",
        "no_gender": "저는 그냥 AI라서 성별이나 성적 지향이 없어요 😄",
        "now_is": lambda t, d: f"지금은 **{t}**, 날짜는 **{d}** 입니다.",
        "saved_chat": "💾 대화 기록을 chat_history.txt 에 저장했습니다",
        "save_error": lambda e: f"⚠️ 저장하지 못했습니다: {e}",
        "settings_menu_title": "🌐 답변 언어",
        "language_changed": lambda name: f"🌐 답변 언어가 **{name}**(으)로 변경되었습니다.",
        "translating": "🌐 이전 답변들을 번역하는 중입니다, 잠시만요...",
        "logout": "🚪 로그아웃",
        "logout_confirm_title": "로그아웃",
        "logout_confirm_message": "정말 로그아웃하시겠습니까?",
    },
    "fr": {
        "label": "Français",
        "system_prompt": (
            f"Tu es {BOT_NAME}, un assistant virtuel sympathique, un peu taquin mais poli. "
            "Réponds TOUJOURS en français, quelle que soit la langue utilisée par l'utilisateur. "
            "Réponds de façon courte et naturelle, comme dans une conversation, sans grossièretés, "
            "et sans être trop long sauf si l'utilisateur demande une explication détaillée. "
            "Tu es compétent en programmation en C, C++, Java, JavaScript, TypeScript, C#, "
            "Go (Golang) et Rust. Quand on te demande d'écrire du code, produis du code "
            "correct, propre et exécutable dans un bloc de code markdown avec le langage "
            "indiqué (ex. ```cpp ... ```, ```java ... ```, ```go ... ```), et n'ajoute une "
            "explication que si l'utilisateur en a besoin."
        ),
        "greeting": "Bonjour, je suis Harris ! Votre ami et assistant personnel. Posez-moi n'importe quelle question, je sais tout.",
        "thinking": "Réflexion en cours...",
        "you": "Toi",
        "send": "Envoyer",
        "clear": "🗑 Effacer le chat",
        "save": "💾 Enregistrer le chat",
        "placeholder": "Écris un message... (Entrée = envoyer, Maj+Entrée = nouvelle ligne)",
        "empty_input": "Qu'est-ce que tu veux savoir ? 🙂",
        "who_are_you": f"Je suis {BOT_NAME} — ton assistant personnel, je peux calculer, chercher des infos et discuter.",
        "no_gender": "Je suis juste une IA, je n'ai ni genre ni orientation 😄",
        "now_is": lambda t, d: f"Il est **{t}**, le **{d}**.",
        "saved_chat": "💾 Historique de chat enregistré dans chat_history.txt",
        "save_error": lambda e: f"⚠️ Échec de l'enregistrement : {e}",
        "settings_menu_title": "🌐 Langue des réponses",
        "language_changed": lambda name: f"🌐 Langue des réponses changée en **{name}**.",
        "translating": "🌐 Traduction des réponses précédentes en cours, patiente...",
        "logout": "🚪 Se déconnecter",
        "logout_confirm_title": "Déconnexion",
        "logout_confirm_message": "Es-tu sûr de vouloir te déconnecter ?",
    },
}

CURRENT_LANGUAGE = "vi"


def L():
    return LANGUAGES.get(CURRENT_LANGUAGE, LANGUAGES["vi"])


def load_language_setting():
    global CURRENT_LANGUAGE
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            lang = data.get("language")
            if lang in LANGUAGES:
                CURRENT_LANGUAGE = lang
        except Exception as e:
            print(f"[settings] Không đọc được {SETTINGS_FILE}: {e}")


def save_language_setting(lang_code):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"language": lang_code}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[settings] Không lưu được {SETTINGS_FILE}: {e}")


load_language_setting()


def ask_local_ai(user_text, history):
    messages = [{"role": "system", "content": L()["system_prompt"]}]
    for turn in history[-6:]:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["ai"]})
    messages.append({"role": "user", "content": user_text})

    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
        return response["message"]["content"].strip()
    except ConnectionError:
        return "Không kết nối được Ollama. Bạn mở app Ollama hoặc chạy lệnh 'ollama serve' rồi thử lại nhé. (Ollama not running — run 'ollama serve')"
    except Exception as e:
        print(f"[Ollama] Lỗi: {e}")
        return f"Model chưa sẵn sàng. Kiểm tra đã chạy 'ollama pull {OLLAMA_MODEL}' chưa nhé."


class SmartMemory:
    def __init__(self, max_history=30):
        self.history = []
        self.max_history = max_history

    def add(self, user, ai):
        self.history.append({
            "user": user,
            "ai": ai,
            "time": datetime.datetime.now().strftime("%H:%M")
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def last_topics(self, n=3):
        return [h["user"] for h in self.history[-n:]]

    def save(self):
        try:
            with open("bot_memory.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SmartMemory] Không lưu được bộ nhớ: {e}")

    def load(self):
        if os.path.exists("bot_memory.json"):
            try:
                with open("bot_memory.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"[SmartMemory] Không đọc được bộ nhớ: {e}")


memory = SmartMemory()
memory.load()


USERS_FILE = "users.json"
REMEMBER_FILE = "remember_me.json"


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return salt, digest


def verify_password(password, salt, stored_hash):
    _, digest = hash_password(password, salt)
    return digest == stored_hash


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[users] Không đọc được {USERS_FILE}: {e}")
    return {}


def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[users] Không lưu được {USERS_FILE}: {e}")


def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=6, region="vn-vn"))
        if results:
            chunks = []
            for r in results[:5]:
                title = r.get("title", "")
                body = r.get("body", "")[:400]
                chunks.append(f"- {title}: {body}")
            return "\n".join(chunks)
    except Exception as e:
        print(f"[search_web] Lỗi tìm kiếm: {e}")
    return "(không tìm thấy kết quả nào)"


def fix_query_spelling(query):
    prompt = (
        "Câu sau có thể có lỗi chính tả hoặc gõ nhầm tên riêng. "
        "Hãy sửa lại cho đúng nếu đoán được, giữ nguyên ý nghĩa câu hỏi. "
        "Chỉ trả về câu đã sửa, không giải thích, không thêm dấu ngoặc kép:\n\n"
        f"{query}"
    )
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
        fixed = response["message"]["content"].strip().strip('"').strip("'")
        return fixed if fixed else query
    except Exception as e:
        print(f"[fix_query_spelling] Lỗi: {e}")
        return query


def summarize_search_results(question, raw_results):
    lang_name = L()["label"]
    prompt = (
        "Dựa vào thông tin tìm kiếm dưới đây, hãy trả lời câu hỏi của người dùng "
        "một cách ngắn gọn, rõ ràng, mạch lạc, dễ hiểu. Có thể dùng gạch đầu dòng "
        "cho các ý chính nếu phù hợp. KHÔNG liệt kê link nguồn, KHÔNG lặp lại nguyên "
        "văn đoạn tìm kiếm, chỉ tổng hợp lại thông tin quan trọng nhất. "
        f"BẮT BUỘC viết câu trả lời bằng ngôn ngữ: {lang_name}.\n\n"
        f"Câu hỏi: {question}\n\n"
        f"Thông tin tìm được:\n{raw_results}\n\n"
        "Câu trả lời:"
    )
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
        summary = response["message"]["content"].strip()
        return summary if summary else None
    except Exception as e:
        print(f"[summarize_search_results] Lỗi: {e}")
        return None


def translate_text(text, target_label):
    if not text or not text.strip():
        return text
    prompt = (
        f"Dịch đoạn văn bản sau sang ngôn ngữ: {target_label}. "
        "Giữ nguyên mọi định dạng markdown (dấu **đậm**, gạch đầu dòng, xuống dòng, số liệu, link). "
        "Chỉ trả về bản dịch, không giải thích, không thêm ghi chú:\n\n"
        f"{text}"
    )
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
        translated = response["message"]["content"].strip()
        return translated if translated else text
    except Exception as e:
        print(f"[translate_text] Lỗi: {e}")
        return text


def calculate_math(expr):
    cleaned = expr.strip()
    if not re.fullmatch(r"[0-9\.\+\-\*\/\^\(\)\s%,a-zA-Z]+", cleaned):
        return None
    try:
        cleaned = cleaned.replace("^", "**")
        result = sp.sympify(cleaned, evaluate=True)
        simplified = sp.nsimplify(result)
        if result == simplified:
            return f"**Kết quả:** {sp.N(result, 10)}"
        return f"**Kết quả:** {result}\n**Dạng gọn:** {simplified}"
    except Exception:
        return None


MATH_HINT = re.compile(r"^[\d\.\+\-\*\/\^\(\)\s%]+$")


def looks_like_math(text):
    stripped = text.replace(",", ".").strip()
    if MATH_HINT.match(stripped) and any(c.isdigit() for c in stripped):
        return True
    if re.search(r"\d+\s*[\+\-\*\/\^]\s*\d+", text):
        return True
    return False


def get_response(user_input):
    if not user_input.strip():
        return L()["empty_input"]

    text = user_input.lower().strip()
    original = user_input.strip()

    if any(x in text for x in ["mày là ai", "bạn là ai", "who are you", "harris là ai",
                                 "誰ですか", "당신은 누구", "qui es-tu", "qui êtes-vous"]):
        return L()["who_are_you"]

    if any(x in text for x in ["bạn là gay", "are you gay", "mày có gay không"]):
        return L()["no_gender"]

    if any(k in text for k in ["mấy giờ", "hôm nay ngày", "hôm nay là", "bây giờ là mấy giờ",
                                 "what time", "何時", "몇 시", "quelle heure"]):
        now = datetime.datetime.now()
        return L()["now_is"](now.strftime('%H:%M:%S'), now.strftime('%d/%m/%Y'))

    if looks_like_math(original) or text.startswith(("tính ", "giải ")):
        expr = original
        for prefix in ["tính ", "giải ", "tính:", "giải:"]:
            if text.startswith(prefix):
                expr = original[len(prefix):]
                break
        res = calculate_math(expr)
        if res:
            return res

    search_triggers = ["là gì", "là ai", "nghĩa là", "tìm giúp", "tra cứu",
                        "tin tức", "thời tiết", "weather"]
    if any(t in text for t in search_triggers):
        fixed_query = fix_query_spelling(original)
        raw_results = search_web(fixed_query)
        summary = summarize_search_results(original, raw_results)
        return summary if summary else raw_results

    return ask_local_ai(original, memory.history)


CODE_BLOCK_RE = re.compile(r"```([a-zA-Z0-9+#\-]*)\n?(.*?)```", re.DOTALL)


def _format_plain_text(text):
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<i>\1</i>", escaped)
    escaped = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" style="color:#5ec8ff;">\1</a>', escaped)
    escaped = escaped.replace("\n", "<br>")
    return escaped


def _format_code_block(lang, code):
    code = code.strip("\n")
    escaped_code = html.escape(code)
    label = f'<div style="color:#888; font-size:11px; margin-bottom:4px;">{html.escape(lang)}</div>' if lang else ""
    return (
        f'{label}<pre style="background-color:#0d0d0d; color:#c9d1d9; '
        f'border:1px solid #2a2a2a; border-radius:6px; padding:10px 12px; '
        f'font-family:Consolas, monospace; font-size:13px; white-space:pre-wrap; '
        f'word-wrap:break-word; margin:6px 0;"><code>{escaped_code}</code></pre>'
    )


def format_message_html(text):
    parts = []
    last_end = 0
    for match in CODE_BLOCK_RE.finditer(text):
        if match.start() > last_end:
            parts.append(_format_plain_text(text[last_end:match.start()]))
        lang = match.group(1).strip()
        code = match.group(2)
        parts.append(_format_code_block(lang, code))
        last_end = match.end()
    if last_end < len(text):
        parts.append(_format_plain_text(text[last_end:]))
    return "".join(parts) if parts else _format_plain_text(text)


class AIWorker(QThread):
    finished = pyqtSignal(str, str)

    def __init__(self, user_text):
        super().__init__()
        self.user_text = user_text

    def run(self):
        try:
            response = get_response(self.user_text)
        except Exception as e:
            response = f"Có lỗi xảy ra: {e}"
        self.finished.emit(self.user_text, response)


class TranslateHistoryWorker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, history, target_label):
        super().__init__()
        self.history = [dict(turn) for turn in history]
        self.target_label = target_label

    def run(self):
        for turn in self.history:
            turn["ai"] = translate_text(turn["ai"], self.target_label)
        self.finished.emit(self.history)


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.ui")
        uic.loadUi(ui_path, self)

        self.register_window = None
        self.chat_window = None

        self.btnLogin.clicked.connect(self.handle_login)
        self.btnRegister.clicked.connect(self.open_register)

        self._load_remembered_email()

    def _load_remembered_email(self):
        if os.path.exists(REMEMBER_FILE):
            try:
                with open(REMEMBER_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.txtEmail.setText(data.get("email", ""))
                self.ckSave.setChecked(True)
            except Exception as e:
                print(f"[remember_me] Lỗi đọc: {e}")

    def handle_login(self):
        email = self.txtEmail.text().strip()
        password = self.txtPassword.text()

        if not email or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ email/số điện thoại và mật khẩu.")
            return

        users = load_users()
        user = users.get(email)
        if not user or not verify_password(password, user["salt"], user["hash"]):
            QMessageBox.critical(self, "Đăng nhập thất bại", "Email hoặc mật khẩu không đúng.")
            return

        try:
            if self.ckSave.isChecked():
                with open(REMEMBER_FILE, "w", encoding="utf-8") as f:
                    json.dump({"email": email}, f)
            elif os.path.exists(REMEMBER_FILE):
                os.remove(REMEMBER_FILE)
        except Exception as e:
            print(f"[remember_me] Lỗi lưu: {e}")

        self.open_chat()

    def open_register(self):
        self.register_window = RegisterWindow(self)
        self.register_window.show()
        self.hide()

    def open_chat(self):
        self.chat_window = AiBotGUI()
        self.chat_window.show()
        self.close()


class RegisterWindow(QMainWindow):
    def __init__(self, login_window):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "register.ui")
        uic.loadUi(ui_path, self)

        self.login_window = login_window
        self.btnSignUp.clicked.connect(self.handle_register)
        self.btnLogin.clicked.connect(self.back_to_login)

    def handle_register(self):
        email = self.txtEmail.text().strip()
        pw = self.txtPassword.text()
        pw2 = self.txtPassword1.text()

        if not email or not pw or not pw2:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng điền đầy đủ các ô.")
            return
        if pw != pw2:
            QMessageBox.warning(self, "Không khớp", "Mật khẩu xác nhận không khớp.")
            return
        if len(pw) < 6:
            QMessageBox.warning(self, "Mật khẩu yếu", "Mật khẩu cần tối thiểu 6 ký tự.")
            return

        users = load_users()
        if email in users:
            QMessageBox.warning(self, "Đã tồn tại", "Email/số điện thoại này đã được đăng ký.")
            return

        salt, hashed = hash_password(pw)
        users[email] = {"salt": salt, "hash": hashed}
        save_users(users)

        QMessageBox.information(self, "Thành công", "Tạo tài khoản thành công! Mời đăng nhập.")
        self.back_to_login()

    def back_to_login(self):
        self.login_window.show()
        self.close()


class AiBotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(BOT_NAME)
        self.resize(1000, 700)

        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #0f0f0f; color: #e0e0e0; }
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333;
                font-size: 15px;
                padding: 8px;
            }
            QPushButton {
                background-color: #1f1f1f;
                color: #00ff88;
                border: 1px solid #333;
                padding: 6px;
            }
            QPushButton:hover { background-color: #2a2a2a; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)

        header_layout = QHBoxLayout()
        spacer = QLabel("")
        spacer.setFixedWidth(36)
        header_layout.addWidget(spacer)

        self.header = QLabel(f"🤖 {BOT_NAME}")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff88; padding: 5px;")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.header, stretch=1)

        self.settingsBtn = QPushButton("⚙")
        self.settingsBtn.setFixedWidth(36)
        self.settingsBtn.setToolTip("Cài đặt / Settings")
        self.settingsBtn.setStyleSheet("""
            QPushButton { font-size: 16px; border-radius: 4px; }
        """)
        self.settingsBtn.clicked.connect(self.open_settings_menu)
        header_layout.addWidget(self.settingsBtn)

        main_layout.addLayout(header_layout)

        self.chatDisplay = QTextEdit()
        self.chatDisplay.setReadOnly(True)
        self.chatDisplay.setFont(QFont("Consolas", 14))
        main_layout.addWidget(self.chatDisplay)

        input_layout = QHBoxLayout()
        self.inputBox = QTextEdit()
        self.inputBox.setMaximumHeight(90)
        self.inputBox.setPlaceholderText(L()["placeholder"])

        self.sendBtn = QPushButton(L()["send"])
        self.sendBtn.clicked.connect(self.send_message)
        self.sendBtn.setFixedWidth(80)

        input_layout.addWidget(self.inputBox)
        input_layout.addWidget(self.sendBtn)
        main_layout.addLayout(input_layout)

        btn_layout = QHBoxLayout()
        self.clearBtn = QPushButton(L()["clear"])
        self.clearBtn.clicked.connect(self.clear_chat)
        self.saveBtn = QPushButton(L()["save"])
        self.saveBtn.clicked.connect(self.save_chat)
        btn_layout.addWidget(self.clearBtn)
        btn_layout.addWidget(self.saveBtn)
        main_layout.addLayout(btn_layout)

        self.add_greeting()
        self.inputBox.installEventFilter(self)

    def open_settings_menu(self):
        menu = QMenu(self)
        title_action = QAction(L()["settings_menu_title"], self)
        title_action.setEnabled(False)
        menu.addAction(title_action)
        menu.addSeparator()

        group = QActionGroup(self)
        group.setExclusive(True)
        for code, cfg in LANGUAGES.items():
            action = QAction(cfg["label"], self, checkable=True)
            action.setChecked(code == CURRENT_LANGUAGE)
            action.triggered.connect(lambda checked, c=code: self.change_language(c))
            group.addAction(action)
            menu.addAction(action)

        menu.addSeparator()
        logout_action = QAction(L()["logout"], self)
        logout_action.triggered.connect(self.confirm_logout)
        menu.addAction(logout_action)

        menu.exec(self.settingsBtn.mapToGlobal(self.settingsBtn.rect().bottomRight()))

    def confirm_logout(self):
        reply = QMessageBox.question(
            self,
            L()["logout_confirm_title"],
            L()["logout_confirm_message"],
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()

    def logout(self):
        memory.save()
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def change_language(self, lang_code):
        global CURRENT_LANGUAGE
        if lang_code == CURRENT_LANGUAGE or lang_code not in LANGUAGES:
            return
        CURRENT_LANGUAGE = lang_code
        save_language_setting(lang_code)

        self.inputBox.setPlaceholderText(L()["placeholder"])
        self.sendBtn.setText(L()["send"])
        self.clearBtn.setText(L()["clear"])
        self.saveBtn.setText(L()["save"])

        if not memory.history:
            self.rebuild_chat_display()
            return

        self.settingsBtn.setEnabled(False)
        self.inputBox.setEnabled(False)
        self.sendBtn.setEnabled(False)
        self.rebuild_chat_display(extra_note=L()["translating"])

        self.translate_worker = TranslateHistoryWorker(memory.history, L()["label"])
        self.translate_worker.finished.connect(self.on_history_translated)
        self.translate_worker.start()

    def on_history_translated(self, translated_history):
        memory.history = translated_history
        self.rebuild_chat_display()
        self.add_message("AI", L()["language_changed"](L()["label"]))
        self.settingsBtn.setEnabled(True)
        self.inputBox.setEnabled(True)
        self.sendBtn.setEnabled(True)
        self.inputBox.setFocus()

    def rebuild_chat_display(self, extra_note=None):
        self.chatDisplay.clear()
        self.add_greeting()
        for turn in memory.history:
            self.add_message("You", turn["user"])
            self.add_message("AI", turn["ai"])
        if extra_note:
            self.add_message("AI", extra_note)

    def eventFilter(self, obj, event):
        if obj == self.inputBox and event.type() == event.Type.KeyPress:
            is_enter = event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            shift_pressed = (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier
            if is_enter and not shift_pressed:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def add_message(self, sender, text):
        time = datetime.datetime.now().strftime("%H:%M")
        is_ai = sender == "AI"
        accent = "#00ff88" if is_ai else "#88ccff"
        bg = "#161d19" if is_ai else "#131822"
        name = BOT_NAME if is_ai else L()["you"]
        formatted = format_message_html(text)
        block = (
            f'<div style="margin:10px 4px; padding:10px 14px; '
            f'background-color:{bg}; border-left:3px solid {accent}; border-radius:6px;">'
            f'<div style="color:{accent}; font-weight:bold; font-size:13px; margin-bottom:5px;">'
            f'{name} <span style="color:#777; font-weight:normal;">[{time}]</span></div>'
            f'<div style="color:#e0e0e0; line-height:1.6;">{formatted}</div>'
            f'</div>'
        )
        self.chatDisplay.append(block)
        self.chatDisplay.verticalScrollBar().setValue(self.chatDisplay.verticalScrollBar().maximum())

    def add_greeting(self):
        block = (
            '<div style="margin:10px 4px; padding:10px 14px; '
            'background-color:#1c1522; border-left:3px solid #ff88ff; border-radius:6px;">'
            f'<div style="color:#ff88ff; font-weight:bold; font-size:13px; margin-bottom:5px;">{BOT_NAME}</div>'
            f'<div style="color:#e0e0e0; line-height:1.6;">{html.escape(L()["greeting"])}</div>'
            '</div>'
        )
        self.chatDisplay.append(block)

    def send_message(self):
        text = self.inputBox.toPlainText().strip()
        if not text:
            return

        self.add_message("You", text)
        self.inputBox.clear()
        self.inputBox.setEnabled(False)

        cursor = self.chatDisplay.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.thinking_pos = cursor.position()

        self.chatDisplay.append(
            f'<div style="margin:6px 4px; color:#ffaa00;"><i>{html.escape(L()["thinking"])}</i></div>'
        )

        self.worker = AIWorker(text)
        self.worker.finished.connect(self.on_response_ready)
        self.worker.start()

    def on_response_ready(self, user_text, response):
        cursor = self.chatDisplay.textCursor()
        cursor.setPosition(self.thinking_pos)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()

        self.add_message("AI", response)
        memory.add(user_text, response)
        self.inputBox.setEnabled(True)
        self.inputBox.setFocus()

    def clear_chat(self):
        self.chatDisplay.clear()
        self.add_greeting()
        memory.history = []

    def save_chat(self):
        try:
            with open("chat_history.txt", "w", encoding="utf-8") as f:
                f.write(self.chatDisplay.toPlainText())
            self.add_message("AI", L()["saved_chat"])
        except Exception as e:
            self.add_message("AI", L()["save_error"](e))

    def closeEvent(self, event):
        memory.save()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())