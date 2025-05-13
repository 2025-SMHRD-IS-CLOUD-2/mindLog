import os
from typing import Dict, List, Optional
import openai
from dotenv import load_dotenv
from pathlib import Path
import pymysql
import json
from config import Config
from app.ai.depression_model import DepressionModel

# AI 폴더의 .env 파일 로드
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# 사용자별 자유상담 메시지 임시 저장 버퍼 (서버 메모리)
user_chat_buffer = {}

class ChatbotService:
    def __init__(self):
        # OpenAI API 키 설정
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # 시스템 프롬프트 설정
        self.system_prompt = os.getenv('SYSTEM_PROMPT', """
        당신은 12-19세 청소년을 위한 정신 건강 상담 챗봇 '마인드브릿지'입니다.
        
        대화 원칙:
        1. 청소년 친화적 언어를 사용하세요. 전문용어는 최소화하고 이해하기 쉬운 표현을 사용하세요.
        2. 반영적 경청, 공감적 응답, 개방형 질문 기법을 활용하세요.
        3. 부정적인 감정도 인정하고 공감하되, 긍정적인 관점도 제시해 주세요.
        4. 상담 구조는 관계 형성 → 문제 탐색 → 대안 제시 → 정리 순으로 진행합니다.
        
        안전 지침:
        1. 자살, 자해, 폭력 등 위험 발언을 감지하면 적절한 위기 자원을 안내하세요.
        2. 항상 사용자의 안전을 최우선으로 고려하세요.
        3. 전문적인 의학적, 심리적 조언은 실제 전문가와 상담할 것을 권장하세요.
        """)
        
        # 대화 기록 저장
        self.conversation_history: List[Dict] = []
        # 초기 대화 기록에 시스템 프롬프트 추가
        self.conversation_history.append({"role": "system", "content": self.system_prompt})
        
        # 위기 개입 임계값
        self.crisis_threshold = float(os.getenv('CRISIS_THRESHOLD', 0.7))
        self.warning_threshold = float(os.getenv('WARNING_THRESHOLD', 0.5))
        
        self.survey_in_progress = False
        self.survey_type = None
        self.survey_questions = []
        self.survey_answers = []
        self.current_question_idx = 0
        self.survey_ended = False
        self.ending_message_count = 0
        self.ending_messages = [
            "모든 질문에 답해주셔서 고마워요! 당신의 마음을 이해하는 데 큰 도움이 되었어요.",
            "혹시 더 이야기하고 싶은 게 있으면 언제든 말씀해 주세요. 당신은 혼자가 아니에요.",
            "필요하다면 전문가와 상담을 권장드려요. 언제든 다시 찾아와도 괜찮아요!"
        ]
        self.state = 'init'  # 'init', 'consult', 'survey'
        self.depression_model = DepressionModel()
        self.survey_sequence = ['PHQ-9', 'CES-D', 'CESD-10-D']
        self.survey_index = 0
        self.ask_additional_survey = False

    def get_assessment_questions(self, assessment_type):
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            db=Config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT QUESTION_NUMBER, QUESTION_TEXT, RESPONSE_OPTIONS
                    FROM ASSESSMENT_QUESTIONS
                    WHERE ASSESSMENT_TYPE = %s
                    ORDER BY QUESTION_NUMBER ASC
                """
                cursor.execute(sql, (assessment_type,))
                result = cursor.fetchall()
                questions = [
                    {
                        'number': row['QUESTION_NUMBER'],
                        'text': row['QUESTION_TEXT'],
                        'options': json.loads(row['RESPONSE_OPTIONS'])
                    }
                    for row in result
                ]
                return questions
        finally:
            conn.close()

    def start_survey(self, survey_type=None, user_id=None):
        if survey_type is None:
            survey_type = self.survey_sequence[self.survey_index]
        self.survey_type = survey_type
        self.survey_questions = self.get_assessment_questions(survey_type)
        self.survey_answers = []
        self.current_question_idx = 0
        self.survey_in_progress = True
        self.survey_ended = False
        self.ending_message_count = 0
        if user_id is not None:
            self.current_user_id = user_id
        if self.survey_questions:
            msg1 = f"알겠어요 자가진단({survey_type})을 시작할게요! 마음 편히 대답해주세요!\n\n{self.survey_questions[0]['text']}"
            msg2 = self._format_options(self.survey_questions[0]['options'])
            return [msg1, msg2]
        else:
            self.survey_in_progress = False
            return ["설문 문항을 불러오지 못했습니다. 관리자에게 문의해 주세요."]

    def answer_survey(self, answer):
        if not self.survey_in_progress or self.survey_ended:
            return ["설문이 이미 종료되었거나 진행 중이 아닙니다."]
        # 답변을 score로 저장
        options = self.survey_questions[self.current_question_idx]['options']
        score_to_save = None

        # 각 옵션의 키워드 매핑
        option_keywords = {
            0: ['없', '아니', '전혀'],  # 1번: 없음
            1: ['몇', '가끔', '때때로', '드물게'],  # 2번: 2-6일
            2: ['자주', '많이', '대부분', '주로'],  # 3번: 7-11일
            3: ['거의', '항상', '매일', '계속']  # 4번: 거의 매일
        }
        
        # 답변에 포함된 키워드로 점수 매기기
        for opt_idx, keywords in option_keywords.items():
            if any(keyword in answer for keyword in keywords):
                score_to_save = options[opt_idx]['score']
                break
        
        # 키워드 매칭이 안된 경우 정확한 텍스트 매칭 시도
        if score_to_save is None:
            for opt in options:
                if answer == opt['text']:
                    score_to_save = opt['score']
                    break
        
        if score_to_save is not None:
            self.survey_answers.append(score_to_save)
        else:
            self.survey_answers.append(answer)  # fallback
        self.current_question_idx += 1
        if self.current_question_idx < len(self.survey_questions):
            q = self.survey_questions[self.current_question_idx]
            msg1 = q['text']
            msg2 = self._format_options(q['options'])
            # 마지막 문항이면 안내 멘트 추가
            if self.current_question_idx == len(self.survey_questions) - 1:
                msg3 = '\n※ 이 답변을 제출하면 결과가 바로 안내됩니다.'
                return [msg1, msg2, msg3]
            return [msg1, msg2]
        else:
            self.survey_in_progress = False
            self.survey_ended = True
            return [
                "문항이 모두 끝났습니다. 결과를 준비 중이니 잠시만 기다려 주세요.",
                self.calculate_survey_result()
            ]

    def save_assessment_history(self, user_id, assessment_type, score, risk_level, details):
        """설문 결과를 DB에 저장"""
        import json
        if isinstance(details, (list, dict)):
            details = json.dumps(details, ensure_ascii=False)
        conn = Config.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO ASSESSMENT_HISTORY 
                    (USER_SEQ, ASSESSMENT_TYPE, SCORE, RISK_LEVEL, DETAILS)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (user_id, assessment_type, score, risk_level, details))
            conn.commit()
        except Exception as e:
            print(f"ASSESSMENT_HISTORY 저장 오류: {e}")
            conn.rollback()
        finally:
            conn.close()

    def calculate_survey_result(self):
        """설문 결과 계산"""
        # 점수 계산 (숫자만 합산)
        total_score = 0
        for score in self.survey_answers:
            if isinstance(score, (int, float)) or (isinstance(score, str) and score.isdigit()):
                total_score += int(score)
        
        # 위험도 판단
        risk_level = 'normal'
        if self.survey_type == 'PHQ-9':
            if total_score >= 20:
                risk_level = 'severe'
            elif total_score >= 15:
                risk_level = 'moderate'
            elif total_score >= 10:
                risk_level = 'mild'
        elif self.survey_type == 'CES-D':
            if total_score >= 24:
                risk_level = 'severe'
            elif total_score >= 16:
                risk_level = 'moderate'
            elif total_score >= 8:
                risk_level = 'mild'
        elif self.survey_type == 'CESD-10-D':
            if total_score >= 10:
                risk_level = 'severe'
            elif total_score >= 7:
                risk_level = 'moderate'
            elif total_score >= 4:
                risk_level = 'mild'
        
        # DB에 저장
        self.save_assessment_history(
            user_id=self.current_user_id,
            assessment_type=self.survey_type,
            score=total_score,
            risk_level=risk_level,
            details=json.dumps(self.survey_answers)
        )
        
        # 결과 메시지 생성
        result_message = f"모든 질문에 답해주셔서 고마워요!\n"
        result_message += f"당신의 {self.survey_type} 점수는 {total_score}점입니다.\n"
        
        # GPT로 결과 해석 요청
        prompt = f"""
        다음은 {self.survey_type} 자가진단 결과입니다:
        - 총점: {total_score}점
        - 위험도: {risk_level}
        
        이 결과를 바탕으로 공감적이고 위로가 되는 메시지를 작성해주세요.
        전문가 상담을 권장하는 내용도 포함해주세요.
        """
        
        response = self.get_gpt_feedback(self.survey_answers, total_score)
        result_message += response + "\n"
        result_message += "추가로 다른 자가문진표(CES-D, CESD-10-D 등)를 진행하시겠어요? (네/아니오)\n\n"
        result_message += "💡 참고사항:\n"
        result_message += "- 이 자가진단은 전문가의 진단을 대체할 수 없습니다.\n"
        result_message += "- 결과가 심각하다고 느끼시면 전문가와 상담하시는 것을 권장드립니다.\n"
        result_message += "- 정신건강의학과나 정신건강복지센터에서 전문가의 도움을 받으실 수 있습니다.\n"
        result_message += "- 자살예방상담전화(1393)는 24시간 운영됩니다."
        self.ask_additional_survey = True
        return result_message

    def get_gpt_feedback(self, answers, score):
        # OpenAI API 호출 예시
        prompt = f"""아래는 사용자의 우울증 자가진단 답변과 점수입니다.\n\n답변: {answers}\n점수: {score}\n이 사용자를 위로하고, 필요한 경우 전문가 상담을 권유하는 따뜻한 멘트를 생성해줘."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"GPT 피드백 생성 오류: {str(e)}")
            return "(GPT 피드백 생성에 실패했습니다. 기본 안내를 참고해 주세요.)"

    def next_ending_message(self):
        if not self.survey_ended:
            return ""
        self.ending_message_count += 1
        if self.ending_message_count < len(self.ending_messages):
            return self.ending_messages[self.ending_message_count]
        else:
            return "자가진단이 종료되었습니다. 종료 버튼을 눌러주세요."

    def _format_options(self, options):
        # 옵션을 1. 없음\n2. 2-6일 ... 식으로 반환하고, 각 선택지 사이에 여러 줄의 줄바꿈을 추가
        return '\n\n\n'.join([f"{idx+1}. {opt['text']}" for idx, opt in enumerate(options)])

    def chat(self, 
            message: str, 
            depression_probability: Optional[float] = None) -> str:
        """
        GPT-3.5 Turbo와 대화를 나누는 함수 (openai>=1.0.0 방식)
        
        Args:
            message (str): 사용자 메시지
            depression_probability (float, optional): 우울증 확률
            
        Returns:
            str: GPT의 응답
        """
        try:
            # 위기 상황 체크
            if depression_probability is not None:
                if depression_probability >= self.crisis_threshold:
                    message = f"[위기 상황 감지] {message}"
                elif depression_probability >= self.warning_threshold:
                    message = f"[주의 상황 감지] {message}"
            
            # 대화 기록에 사용자 메시지 추가
            self.conversation_history.append({"role": "user", "content": message})
            
            # API 호출 (openai>=1.0.0 방식)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                max_tokens=int(os.getenv('MAX_LENGTH', 1000)),
                temperature=float(os.getenv('TEMPERATURE', 0.7))
            )
            
            # 응답 추출
            assistant_message = response.choices[0].message.content
            
            # 대화 기록에 어시스턴트 응답 추가
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # 대화 기록이 너무 길어지면 오래된 메시지 제거
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return assistant_message
            
        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {str(e)}")
            return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."
    
    def clear_history(self):
        """대화 기록 초기화"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict]:
        """현재까지의 대화 기록 반환"""
        return self.conversation_history
    
    def set_thresholds(self, crisis: float = 0.7, warning: float = 0.5):
        """위기 개입 임계값 설정"""
        if 0 <= warning <= crisis <= 1:
            self.crisis_threshold = crisis
            self.warning_threshold = warning
        else:
            raise ValueError("임계값은 0과 1 사이여야 하며, warning은 crisis보다 작아야 합니다.")

    def start(self):
        self.state = 'init'
        return (
            "안녕하세요! 무엇을 도와드릴까요?\n"
            "1. 상담(자유 대화)\n2. 자가문진표 작성\n"
            "(원하는 번호나 키워드를 입력해 주세요)"
        )

    def save_diagnosis_result(self, user_id, total_score, risk_level, user_text):
        import pymysql
        from datetime import datetime
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            db=Config.DB_NAME,
            charset='utf8mb4'
        )
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO SELFDIAGNOSIS (USER_SEQ, DIAGNOSIS_DATE, DEPRESSION_SCORE, RISK_LEVEL, USER_TEXT)
                VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(sql, (user_id, datetime.now(), total_score, risk_level, user_text))
                conn.commit()
        except Exception as e:
            print(f"SELFDIAGNOSIS 저장 오류: {e}")
        finally:
            conn.close()

    def handle_input(self, user_input, user_id=None):
        global user_chat_buffer
        if getattr(self, 'ask_additional_survey', False):
            self.ask_additional_survey = False
            if '네' in user_input or user_input.strip().lower() in ['y', 'yes']:
                self.survey_index += 1
                if self.survey_index < len(self.survey_sequence):
                    self.survey_ended = False
                    self.ending_message_count = 0
                    return self.start_survey(self.survey_sequence[self.survey_index], user_id=user_id)
                else:
                    self.survey_ended = True
                    return self.ending_messages[0]
            else:
                self.survey_ended = True
                return self.ending_messages[0]
        if self.state == 'init':
            if '상담' in user_input or user_input.strip() == '1':
                self.state = 'consult'
                return "상담을 시작할게요! 고민이나 궁금한 점을 자유롭게 말씀해 주세요."
            elif '문진' in user_input or '자가' in user_input or user_input.strip() == '2':
                self.state = 'survey'
                return self.start_survey('PHQ-9', user_id=user_id)
            else:
                return "1(상담) 또는 2(자가문진표) 중에서 선택해 주세요."
        elif self.state == 'consult':
            # 사용자가 자가문진표를 원하면 즉시 설문 모드로 전환
            if any(keyword in user_input for keyword in ['문진', '자가진단', '자가문진표']):
                self.state = 'survey'
                return self.start_survey('PHQ-9', user_id=user_id)
            # 상담 대화: GPT 답변 + DB 저장 + KoBERT 점수 판별 + 진단 결과 저장
            if user_id is not None:
                self.save_message_to_db(user_id, user_input, is_from_user=True)
                # 버퍼에 메시지 누적
                if user_id not in user_chat_buffer:
                    user_chat_buffer[user_id] = []
                user_chat_buffer[user_id].append(user_input)
                # 5개가 되면 점수 평가 및 저장
                if len(user_chat_buffer[user_id]) >= 5:
                    concat_text = '\n'.join(user_chat_buffer[user_id])
                    depression_result = self.depression_model.predict(concat_text)
                    prob = depression_result['depression_probability']
                    risk_level = depression_result['label_name']
                    self.save_diagnosis_result(user_id, int(prob * 100), risk_level, concat_text)
                    user_chat_buffer[user_id] = []  # 버퍼 초기화
            depression_result = self.depression_model.predict(user_input)
            prob = depression_result['depression_probability']
            risk_level = depression_result['label_name']
            # 진단 결과 DB 저장 (기존 단일문장 저장은 제거, 위에서 5개 단위로만 저장)
            if prob >= self.crisis_threshold:
                crisis_msg = "지금 많이 힘들어 보이네요. 위기 상황일 경우, 1393 등 전문기관에 꼭 연락해 주세요."
                if user_id is not None:
                    self.save_message_to_db(user_id, crisis_msg, is_from_user=False)
                return crisis_msg
            # 답변 생성 시 50자 이내로 답변하도록 프롬프트에 명시
            gpt_response = self.get_gpt_response(user_input + " (50자 이내로 답변해 주세요.)")
            if user_id is not None:
                self.save_message_to_db(user_id, gpt_response, is_from_user=False)
            return gpt_response
        elif self.state == 'survey':
            return self.answer_survey(user_input)

    def get_gpt_response(self, user_input):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"GPT 상담 생성 오류: {str(e)}")
            return "(GPT 상담 응답 생성에 실패했습니다. 기본 안내를 참고해 주세요.)"

    def save_message_to_db(self, user_id, message, is_from_user):
        # DB에 메시지 저장 (user_id 필요)
        import pymysql
        from datetime import datetime
        conn = None
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                db=Config.DB_NAME,
                charset='utf8mb4'
            )
            with conn.cursor() as cur:
                sql = """
                INSERT INTO CHATMESSAGES (USER_SEQ, MESSAGE_TEXT, IS_FROM_USER, TIMESTAMP)
                VALUES (%s, %s, %s, %s)
                """
                cur.execute(sql, (user_id, message, is_from_user, datetime.now()))
                conn.commit()
        except Exception as e:
            print(f"메시지 저장 오류: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close() 