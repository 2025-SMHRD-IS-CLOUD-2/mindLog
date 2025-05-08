import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app.ai.chatbot import ChatbotService
import random
import difflib
import re
import pymysql
from config import Config

# 자연스러운 질문 프롬프트 예시
QUESTION_PROMPTS = [
    "아래 내용을 참고해서 솔직하게 답해줘도 괜찮아요!",
    "부담 갖지 말고 편하게 답해줘도 돼요."
]

def extract_number(text):
    # 입력에서 숫자 추출 (예: '3일', '9일' 등)
    match = re.search(r'(\d+)', text)
    if match:
        return int(match.group(1))
    return None

def match_answer(user_input, options):
    option_texts = [opt['text'] if isinstance(opt, dict) else opt for opt in options]
    user_input_stripped = user_input.strip()
    # 1. 숫자 입력 우선 매칭
    if user_input_stripped.isdigit():
        idx = int(user_input_stripped) - 1
        if 0 <= idx < len(option_texts):
            return idx
    # 2. 숫자 범위 매칭
    num = extract_number(user_input)
    if num is not None:
        for idx, text in enumerate(option_texts):
            # 예: '2-6일', '7-12일' 등에서 범위 추출
            range_match = re.search(r'(\d+)[^\d]+(\d+)', text)
            if range_match:
                start, end = int(range_match.group(1)), int(range_match.group(2))
                if start <= num <= end:
                    return idx
            # '거의 매일' 등은 13일 이상으로 간주(예시)
            if "거의 매일" in text and num >= 13:
                return idx
            if "없음" in text and num == 0:
                return idx
    # 3. 키워드 포함 매칭
    for idx, text in enumerate(option_texts):
        if text.replace(" ", "") in user_input.replace(" ", ""):
            return idx
        for word in text.replace("-", " ").split():
            if word in user_input:
                return idx
    # 4. difflib 유사도 매칭 (cutoff 상향)
    best_match = difflib.get_close_matches(user_input, option_texts, n=1, cutoff=0.6)
    if best_match:
        return option_texts.index(best_match[0])
    # 5. 그래도 없으면 첫 번째 옵션 선택
    return 0

def check_db_result(user_id, assessment_type):
    """DB에 저장된 결과 확인"""
    conn = Config.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT * FROM ASSESSMENT_HISTORY 
                WHERE USER_SEQ = %s AND ASSESSMENT_TYPE = %s 
                ORDER BY ASSESSMENT_DATE DESC LIMIT 1
            """
            cursor.execute(sql, (user_id, assessment_type))
            result = cursor.fetchone()
            if result:
                print("\nDB 저장 결과:")
                print(f"점수: {result['SCORE']}")
                print(f"위험도: {result['RISK_LEVEL']}")
                print(f"상세 응답: {result['DETAILS']}")
            else:
                print("\nDB에 결과가 저장되지 않았습니다.")
    finally:
        conn.close()

if __name__ == "__main__":
    # 테스트용 user_id (실제 DB에 있는 user_id 사용)
    TEST_USER_ID = 1  # 실제 DB에 있는 user_id로 변경해주세요
    
    chatbot = ChatbotService()
    print("안녕하세요! 마음 건강 자가진단을 시작할게요. 아래 질문에 솔직하게 답해주면 도움이 될 거예요!\n")
    print(chatbot.start_survey('PHQ-9', user_id=TEST_USER_ID))

    for i in range(len(chatbot.survey_questions)):
        q = chatbot.survey_questions[i]
        prompt = random.choice(QUESTION_PROMPTS)
        print(f"Q{i+1}. {q['text']} {prompt}")
        options = q['options']
        for idx, opt in enumerate(options):
            if isinstance(opt, dict):
                print(f"  {idx+1}. {opt['text']}")
            else:
                print(f"  {idx+1}. {opt}")
        # 사용자 자연어 입력 받기
        user_input = input("답변을 입력하세요: ")
        choice = match_answer(user_input, options)
        answer = options[choice]['text'] if isinstance(options[choice], dict) else options[choice]
        print(f"선택된 답변: {answer}")
        print(chatbot.answer_survey(answer))

    print(chatbot.next_ending_message())
    print(chatbot.next_ending_message())
    print(chatbot.next_ending_message())
    
    # DB 저장 결과 확인
    check_db_result(TEST_USER_ID, 'PHQ-9') 