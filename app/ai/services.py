import os
from typing import Dict, List, Optional
import openai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class AIService:
    def __init__(self):
        # OpenAI API 키 설정
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        openai.api_key = self.api_key
        
        # 기본 모델 설정
        self.default_model = "gpt-3.5-turbo"
        
        # 대화 기록 저장
        self.conversation_history: List[Dict] = []
        
    def chat_with_gpt(self, 
                     message: str, 
                     model: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: int = 1000) -> str:
        """
        GPT와 대화를 나누는 함수
        
        Args:
            message (str): 사용자 메시지
            model (str, optional): 사용할 GPT 모델. 기본값은 gpt-3.5-turbo
            temperature (float): 응답의 창의성 정도 (0.0 ~ 1.0)
            max_tokens (int): 최대 토큰 수
            
        Returns:
            str: GPT의 응답
        """
        try:
            # 대화 기록에 사용자 메시지 추가
            self.conversation_history.append({"role": "user", "content": message})
            
            # API 호출
            response = openai.ChatCompletion.create(
                model=model or self.default_model,
                messages=self.conversation_history,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 응답 추출
            assistant_message = response.choices[0].message.content
            
            # 대화 기록에 어시스턴트 응답 추가
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            print(f"GPT API 호출 중 오류 발생: {str(e)}")
            return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."
    
    def clear_conversation_history(self):
        """대화 기록 초기화"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict]:
        """현재까지의 대화 기록 반환"""
        return self.conversation_history
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        텍스트의 감정 분석을 수행하는 함수
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            Dict: 감정 분석 결과
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "당신은 감정 분석 전문가입니다. 주어진 텍스트의 감정을 분석해주세요."},
                    {"role": "user", "content": f"다음 텍스트의 감정을 분석해주세요: {text}"}
                ],
                temperature=0.3
            )
            
            return {
                "text": text,
                "analysis": response.choices[0].message.content
            }
            
        except Exception as e:
            print(f"감정 분석 중 오류 발생: {str(e)}")
            return {
                "text": text,
                "analysis": "감정 분석을 수행할 수 없습니다."
            }

# 싱글톤 인스턴스 생성
ai_service = AIService() 