import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import Dict, Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# AI 폴더의 .env 파일 로드
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

class DepressionModel:
    def __init__(self, model_path: Optional[str] = None):
        # 모델 경로 설정
        if model_path is None:
            model_path = os.getenv('MODEL_PATH', 'models/depression/model')
        
        # 절대 경로로 변환
        self.model_path = Path(__file__).parent / model_path
        
        # GPU 사용 가능 여부 확인
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 모델과 토크나이저 로드
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path,
                local_files_only=True
            )
            self.model = self.model.to(self.device)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.unk_token
                
        except Exception as e:
            raise RuntimeError(f"모델 로드 중 오류 발생: {str(e)}")
            
        # 설정값 로드
        self.threshold = float(os.getenv('DEPRESSION_THRESHOLD', 0.5))
        self.max_len = int(os.getenv('MAX_LENGTH', 256))
    
    def predict(self, text: str) -> Dict:
        """
        텍스트 입력에 대한 우울증 확률 예측
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            Dict: 예측 결과 (라벨, 라벨명, 우울증 확률)
        """
        self.model.eval()
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            
        probabilities = torch.softmax(logits, dim=1)
        depression_probability = probabilities[0][1].item()
        
        # 임계값 적용
        label = 1 if depression_probability > self.threshold else 0
        label_name = '우울증' if label == 1 else '정상'
        
        return {
            'label': label,
            'label_name': label_name,
            'depression_probability': depression_probability
        }
    
    def set_threshold(self, threshold: float):
        """임계값 설정"""
        if 0 <= threshold <= 1:
            self.threshold = threshold
        else:
            raise ValueError("임계값은 0과 1 사이여야 합니다.") 