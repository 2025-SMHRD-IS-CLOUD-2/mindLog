document.addEventListener('DOMContentLoaded', function() {
    // 폼 요소 가져오기
    const joinForm = document.getElementById('joinForm');
    
    // 페이지 이동 처리
    function handleNavigation(event) {
        const href = event.target.dataset.href;
        if (href) {
            window.location.href = href;
        }
    }
    
    // 페이지 이동 버튼 이벤트 리스너
    const navigationButtons = document.querySelectorAll('[data-href]');
    if (navigationButtons) {
        navigationButtons.forEach(button => {
            button.addEventListener('click', handleNavigation);
        });
    }
    
    // 회원정보 수정 페이지인 경우
    const editInfoBtn = document.getElementById('editInfo');
    if (editInfoBtn) {
        // 회원정보 수정 기능 구현
        // 실제 구현에서는 필요한 로직 추가
    }
});