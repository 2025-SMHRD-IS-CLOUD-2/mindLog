document.addEventListener('DOMContentLoaded', function() {
    const deleteForm = document.getElementById('deleteForm');
    
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 확인 대화상자 표시
            if (confirm('정말로 회원탈퇴를 진행하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
                // 사용자가 확인을 누르면 폼 제출
                this.submit();
            }
        });
    }

    // 비밀번호 입력 필드에 대한 유효성 검사
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const errorDiv = document.getElementById('passwordError');
            if (this.value.trim() === '') {
                errorDiv.textContent = '비밀번호를 입력해주세요.';
                errorDiv.style.display = 'block';
            } else {
                errorDiv.style.display = 'none';
            }
        });
    }

    // 취소 버튼 처리
    const cancelButton = document.getElementById('cancelDelete');
    if (cancelButton) {
        cancelButton.addEventListener('click', function(e) {
            e.preventDefault();
            // 메인 페이지로 이동
            window.location.href = '/';
        });
    }
});