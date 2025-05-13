// 비밀번호 찾기(보안질문 기반) 단계별 처리 스크립트
function getQuestion() {
  const user_id = document.getElementById("user_id").value.trim();
  if (!user_id) {
    showResult("아이디를 입력하세요.");
    return;
  }
  fetch("/auth/find-password/question", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("findpw-step1").style.display = "none";
        document.getElementById("findpw-step2").style.display = "block";
        document.getElementById("security-question").innerText = data.question;
        showResult("");
      } else {
        showResult(data.message || "아이디를 찾을 수 없습니다.");
      }
    });
}

function verifyAnswer() {
  const user_id = document.getElementById("user_id").value.trim();
  const answer = document.getElementById("security_answer").value.trim();
  if (!answer) {
    showResult("답변을 입력하세요.");
    return;
  }
  fetch("/auth/find-password/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, answer }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("findpw-step2").style.display = "none";
        document.getElementById("findpw-step3").style.display = "flex";
        showResult("");
      } else {
        showResult(data.message || "답변이 일치하지 않습니다.");
      }
    });
}

function resetPassword() {
  const user_id = document.getElementById("user_id").value.trim();
  const new_password = document.getElementById("new_password").value.trim();
  if (!new_password) {
    showResult("새 비밀번호를 입력하세요.");
    return;
  }
  fetch("/auth/find-password/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, new_password }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("findpw-step3").style.display = "none";
        showResult(
          "비밀번호가 성공적으로 변경되었습니다. 로그인 페이지로 이동해 주세요.",
          true
        );
      } else {
        showResult("비밀번호 변경에 실패했습니다.");
      }
    });
}

function showResult(msg, success = false) {
  const resultDiv = document.getElementById("findpw-result");
  resultDiv.innerText = msg;
  resultDiv.className = success ? "mt-3 text-success" : "mt-3 text-danger";
}
