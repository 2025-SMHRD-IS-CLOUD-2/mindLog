document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("cesd-form");
    const scoreResult = document.getElementById("score-result");
    
    // 제출 이벤트 처리
    form.addEventListener("submit", function(event) {
      event.preventDefault();
      
      let total = 0;
      
      // 각 문항 점수 계산
      for (let i = 1; i <= 10; i++) {
        const radios = document.getElementsByName("q" + i);
        let value = null;
        
        for (const radio of radios) {
          if (radio.checked) {
            value = parseInt(radio.value, 10);
            break;
          }
        }
        
        if (value === null) {
          alert(i + "번 문항에 답변하지 않았습니다.");
          return;
        }
        
        total += value;
      }
      
      // 결과 표시
      let message = `총점: ${total}점`;
      
      // 점수 해석 (10점 이상이면 우울 위험)
      if (total >= 10) {
        message += " (우울 위험군)";
      } else {
        message += " (정상 범위)";
      }
      
      scoreResult.textContent = message;
      alert(message);
    });
    
    // 초기화 이벤트 처리
    form.addEventListener("reset", function() {
      setTimeout(function() {
        // 연령, 성별, 실시일 초기화
        form.querySelector('input[name="age"]').value = "";
        form.querySelector('select[name="gender"]').selectedIndex = 0;
        form.querySelector('input[name="date"]').value = "";
        scoreResult.textContent = "";
      }, 10);
    });
  });