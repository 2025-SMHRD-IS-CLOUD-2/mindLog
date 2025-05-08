document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("phq9-form");
    const scoreResult = document.getElementById("score-result");

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      let total = 0;
      for (let i = 1; i <= 9; i++) {
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
      let message = `총점: ${total}점`;
      // PHQ-9 해석 예시 (참고용, 실제 임상적 해석은 다를 수 있음)
      if (total < 5) {
        message += " (정상 또는 최소 우울)";
      } else if (total < 10) {
        message += " (경미한 우울)";
      } else if (total < 15) {
        message += " (중등도 우울)";
      } else if (total < 20) {
        message += " (중등도~중증 우울)";
      } else {
        message += " (중증 우울)";
      }
      scoreResult.textContent = message;
      alert(message);
    });

    form.addEventListener("reset", function () {
      setTimeout(function () {
        form.querySelector('input[name="age"]').value = "";
        form.querySelector('select[name="gender"]').selectedIndex = 0;
        form.querySelector('input[name="date"]').value = "";
        scoreResult.textContent = "";
      }, 10);
    });
  });