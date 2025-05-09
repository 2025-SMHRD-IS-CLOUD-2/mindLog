document.addEventListener("DOMContentLoaded", function () {
  // CES-D 설문
  const cesdForm = document.getElementById("cesd-form");
  const cesdResult = document.getElementById("score-result-cesd");
  if (cesdForm && cesdResult) {
    cesdForm.addEventListener("submit", function (event) {
      event.preventDefault();
      let total = 0;
      const reverse = [4, 8, 12, 16];
      for (let i = 1; i <= 20; i++) {
        const checked = cesdForm.querySelector(`input[name="q${i}"]:checked`);
        let val = checked ? Number(checked.value) : null;
        if (val === null) {
          alert(`${i}번 문항에 답변하지 않았습니다.`);
          return;
        }
        if (reverse.includes(i)) {
          val = 3 - val;
        }
        total += val;
      }
      let message = `총점: ${total}점`;
      cesdResult.textContent = message;
      alert(message);
    });
    cesdForm.addEventListener("reset", function () {
      setTimeout(() => {
        cesdResult.textContent = "";
      }, 10);
    });
  }

  // CESD-10-D 설문
  const cesd10dForm = document.getElementById("cesd10d-form");
  const cesd10dResult = document.getElementById("score-result-cesd10d");
  if (cesd10dForm && cesd10dResult) {
    cesd10dForm.addEventListener("submit", function (event) {
      event.preventDefault();
      let total = 0;
      const reverse = [1, 6, 8];
      for (let i = 1; i <= 10; i++) {
        const checked = cesd10dForm.querySelector(
          `input[name="q${i}"]:checked`
        );
        let val = checked ? Number(checked.value) : null;
        if (val === null) {
          alert(`${i}번 문항에 답변하지 않았습니다.`);
          return;
        }
        if (reverse.includes(i)) {
          val = 1 - val;
        }
        total += val;
      }
      let message = `총점: ${total}점`;
      cesd10dResult.textContent = message;
      alert(message);
    });
    cesd10dForm.addEventListener("reset", function () {
      setTimeout(() => {
        cesd10dResult.textContent = "";
      }, 10);
    });
  }

  // PHQ-9 설문
  const phq9Form = document.getElementById("phq-9-form");
  const phq9Result = document.getElementById("score-result-phq9");
  if (phq9Form && phq9Result) {
    phq9Form.addEventListener("submit", function (event) {
      event.preventDefault();
      let total = 0;
      for (let i = 1; i <= 9; i++) {
        const checked = phq9Form.querySelector(`input[name="q${i}"]:checked`);
        let val = checked ? Number(checked.value) : null;
        if (val === null) {
          alert(`${i}번 문항에 답변하지 않았습니다.`);
          return;
        }
        total += val;
      }
      let message = `총점: ${total}점`;
      phq9Result.textContent = message;
      alert(message);
    });
    phq9Form.addEventListener("reset", function () {
      setTimeout(() => {
        phq9Result.textContent = "";
      }, 10);
    });
  }

  // 공통 초기화 로직
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("reset", function () {
      setTimeout(() => {
        document.querySelector('input[name="age"]').value = "";
        document.querySelector('select[name="gender"]').selectedIndex = 0;
        document.querySelector('input[name="date"]').value = "";
      }, 10);
    });
  });

  // 탭 전환 로직
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabBtns.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((tc) => tc.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });

  // 오늘 날짜 자동 설정
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;
  document.querySelector('input[name="date"]').value = formattedDate;
});
