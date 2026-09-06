# Harris AI

Harris là một trợ lý ảo (chatbot) chạy trên desktop, xây dựng bằng **PyQt6** và mô hình AI local thông qua **Ollama**. Hỗ trợ đăng nhập/đăng ký tài khoản, trò chuyện, tính toán, tìm kiếm web và đổi ngôn ngữ trả lời.

## ✨ Tính năng

- 💬 Trò chuyện với AI (chạy local qua Ollama, không cần internet để chat)
- 🌐 Tìm kiếm web và tự tóm tắt kết quả (dùng DuckDuckGo Search)
- 🧮 Tính toán biểu thức toán học (dùng SymPy)
- 🌍 Hỗ trợ đa ngôn ngữ (Tiếng Việt / English), dịch lại lịch sử chat khi đổi ngôn ngữ
- 🔐 Hệ thống đăng nhập / đăng ký tài khoản, có "Ghi nhớ đăng nhập"
- 💾 Lưu / xoá lịch sử chat
- 🧠 Bộ nhớ ngắn hạn ghi nhớ các chủ đề đã trò chuyện gần đây

## 📋 Yêu cầu

- Python 3.9 trở lên
- [Ollama](https://ollama.com) đã được cài đặt trên máy
- Model `llama3.2` đã được tải về qua Ollama

## 🚀 Cài đặt

1. **Cài Ollama** (nếu chưa có): tải tại [ollama.com](https://ollama.com), cài đặt theo hướng dẫn cho hệ điều hành của bạn.

2. **Tải model AI** (chạy trong terminal):
   ```bash
   ollama pull llama3.2
   ```

3. **Clone hoặc tải project này về máy**, sau đó cài các thư viện Python cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Chạy chương trình

```bash
python Ai_bot.py
```

Lần đầu chạy, bạn cần đăng ký tài khoản trước khi đăng nhập vào giao diện chat.

## 🗂️ Cấu trúc project

```
Harris_ai/
├── Ai_bot.py          # File chính, chứa toàn bộ logic app
├── login.ui           # Giao diện đăng nhập
├── register.ui         # Giao diện đăng ký
├── settings.json       # Lưu cài đặt ngôn ngữ
├── requirements.txt    # Danh sách thư viện cần cài
└── README.md
```

> **Lưu ý:** các file `users.json`, `remember_me.json`, `bot_memory.json` được tạo tự động khi chạy chương trình (chứa tài khoản người dùng và bộ nhớ chat) — không nên đưa lên GitHub công khai.

## ⚠️ Giới hạn

Vì AI chạy local qua Ollama, máy chạy chương trình cần đủ cấu hình để chạy model `llama3.2` mượt (khuyến nghị RAM 8GB trở lên).

## 📄 License

Dự án này được phát hành miễn phí. Thêm giấy phép cụ thể (ví dụ MIT License) tại đây nếu bạn muốn cho phép người khác tự do sử dụng và chỉnh sửa mã nguồn.
