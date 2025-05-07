from typing import Dict
import anthropic
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

class SentimentAnalyzer:
    def __init__(self):
        # Claude API 키 설정
        self.api_key = os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY가 설정되지 않았습니다.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def analyze(self, text: str) -> Dict:
        """
        텍스트의 감정을 분석하는 함수
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            Dict: 감정 분석 결과
        """
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 감정 분석 전문가입니다. 
                        주어진 텍스트의 감정을 다음 카테고리로 분석해주세요:
                        - 기쁨/행복
                        - 슬픔/우울
                        - 분노/짜증
                        - 불안/걱정
                        - 중립
                        
                        각 감정의 강도를 0-100 사이의 숫자로 표현해주세요."""
                    },
                    {
                        "role": "user",
                        "content": f"다음 텍스트의 감정을 분석해주세요: {text}"
                    }
                ],
                max_tokens=500
            )
            
            return {
                "text": text,
                "analysis": response.content[0].text
            }
            
        except Exception as e:
            print(f"감정 분석 중 오류 발생: {str(e)}")
            return {
                "text": text,
                "analysis": "감정 분석을 수행할 수 없습니다."
            } 