import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app.ai.chatbot import ChatbotService

if __name__ == "__main__":
    chatbot = ChatbotService()
    user_id = 1  # 테스트용 사용자 ID
    print(chatbot.start())

    while True:
        user_input = input("사용자: ")
        response = chatbot.handle_input(user_input, user_id=user_id)
        print(f"챗봇: {response}")
        # 자가문진표 모드에서 설문 종료 후 종료 멘트까지 출력하면 break
        if chatbot.state == 'survey' and chatbot.survey_ended and chatbot.ending_message_count >= len(chatbot.ending_messages)-1:
            print(chatbot.next_ending_message())
            break
        # 상담 모드에서 '종료' 입력 시 종료
        if chatbot.state == 'consult' and user_input.strip() in ['종료', 'quit', 'exit']:
            print("상담을 종료합니다. 언제든 다시 찾아와 주세요!")
            break 