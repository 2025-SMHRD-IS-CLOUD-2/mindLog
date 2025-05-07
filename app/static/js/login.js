document.addEventListener('DOMContentLoaded', () => {
    // URL 쿼리 파라미터 제거
    if (window.location.search) {
        window.history.replaceState({}, '', window.location.pathname);
    }

    // 폼 요소 가져오기
    const loginForm = document.querySelector('.login-form');
    if (!loginForm) return;
    
    const idInput = loginForm.querySelector('input[name="user_id"]');
    const passwordInput = loginForm.querySelector('input[name="user_pw"]');
    const loginButton = loginForm.querySelector('.login-button');
    const autoLoginCheckbox = loginForm.querySelector('input[type="checkbox"]');

    // 입력값 검증
    function validateInputs() {
        const id = idInput.value.trim();
        const password = passwordInput.value.trim();
        
        if (id && password) {
            loginButton.style.opacity = '1';
            loginButton.disabled = false;
        } else {
            loginButton.style.opacity = '0.5';
            loginButton.disabled = true;
        }
    }

    // 입력값 변경 감지
    if (idInput && passwordInput) {
        idInput.addEventListener('input', validateInputs);
        passwordInput.addEventListener('input', validateInputs);
    }

    // 초기 버튼 상태 설정
    if (idInput && passwordInput && loginButton) {
        validateInputs();
    }

    // 로그인 폼 제출은 서버에서 처리
    // 프론트에서 추가 로직이 필요한 경우 여기에 작성

    // 회원가입 버튼 클릭
    const signupButton = loginForm.querySelector('.signup-button');
    if (signupButton) {
        signupButton.addEventListener('click', () => {
            console.log('회원가입 버튼 클릭');
            if (signupButton.dataset.href) {
                window.location.href = signupButton.dataset.href;
            }
        });
    }
});