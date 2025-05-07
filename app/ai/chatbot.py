import os
from typing import Dict, List, Optional
import openai
from dotenv import load_dotenv
from pathlib import Path

# AI 폴더의 .env 파일 로드
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

class ChatbotService:
    def __init__(self):
        # OpenAI API 키 설정
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # 대화 기록 저장
        self.conversation_history: List[Dict] = []
        
        # 위기 개입 임계값
        self.crisis_threshold = float(os.getenv('CRISIS_THRESHOLD', 0.7))
        self.warning_threshold = float(os.getenv('WARNING_THRESHOLD', 0.5))
        
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