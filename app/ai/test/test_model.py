import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app.ai import DepressionModel

model = DepressionModel()
text = "요즘 너무 우울하고 힘들어요."
result = model.predict(text)
print("예측 결과:", result)