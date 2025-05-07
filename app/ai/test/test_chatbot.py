import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app.ai import ChatbotService

chatbot = ChatbotService()
user_message = "안녕! 오늘 기분이 어때?"
response = chatbot.chat(user_message)
print("챗봇 응답:", response)