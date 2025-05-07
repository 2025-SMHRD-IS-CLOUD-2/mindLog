from flask_login import UserMixin

class User(UserMixin):
    """
    사용자 모델 클래스
    Flask-Login과 호환되도록 UserMixin을 상속받습니다.
    """
    def __init__(self, user_data):
        """
        데이터베이스에서 가져온 사용자 데이터로 객체 초기화
        
        Args:
            user_data (dict): 데이터베이스에서 가져온 사용자 정보
        """
        self.id = user_data['USER_SEQ']
        self.user_id = user_data['USER_ID']
        self.nickname = user_data['NICKNAME']
        self.password_hash = user_data['PASSWORD_HASH']
        self.birth_date = user_data['BIRTH_DATE']
        self.region = user_data['REGION']
        
    def get_id(self):
        """
        Flask-Login에서 사용자 식별을 위한 ID 반환
        
        Returns:
            str: 사용자 고유번호(USER_SEQ)를 문자열로 반환
        """
        return str(self.id)