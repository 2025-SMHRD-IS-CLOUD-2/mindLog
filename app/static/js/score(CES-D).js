document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("cesd-form");
    const scoreResult = document.getElementById("score-result");
    const reverseItems = [4, 8, 12, 16];
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      let total = 0;
      for (let i = 1; i <= 20; i++) {
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
        if (reverseItems.includes(i)) {
          value = 3 - value;
        }
        total += value;
      }
      let message = `총점: ${total}점`;
      if (total < 21) {
        message += " (정상 범위)";
      } else if (total < 25) {
        message += " (가벼운~중간 우울, 주위에 도움 요청 권고)";
      } else {
        message += " (심한 우울, 전문가 상담 권고)";
      }
      scoreResult.textContent = message;
      alert(message);
    });
    form.addEventListener("reset", function () {
      setTimeout(function () {
        scoreResult.textContent = "";
      }, 10);
    });
  });