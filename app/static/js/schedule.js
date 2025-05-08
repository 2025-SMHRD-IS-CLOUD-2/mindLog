
let date = new Date();
let year = date.getFullYear();
let currMonth = date.getMonth()+1;
let today = date.getDate();
let weekday = date.getDay();
let WrapDay = document.getElementById("wrap_day");
function calendar(year,currMonth,today) {
    let month = document.getElementsByClassName("month");
    let calendar = document.getElementById("calendar");
    let tMFD = new Date(year,currMonth-1,1); // 이번달 첫날짜 데이터
    let tMLD = new Date(year,currMonth,0); // 이번달 마지막 일 데이터
    let lMLD = new Date(year,currMonth-1,0); // 저번달 마지막 날짜 데이터
    month[0].innerText = `${year}년 ${currMonth}월`;
    for (let i = 1; i <= tMLD.getDate()+tMFD.getDay(); i++) {
        if(i <= tMFD.getDay()){ // 저번달 날짜들 이번달 첫날 앞에 출력
            let days =  document.createElement("div")
            days.setAttribute("class","days")
            days.innerHTML = `<span class = 'LMD'>${lMLD.getDate()-tMFD.getDay()+i}</span>`;
            days.addEventListener("click", function() {
            scheduleDate.innerText = "";
            let selectDay = document.createElement('h4');
            if(currMonth == 1){
                selectDay.innerText = `${year-1}년 12월 ${days.innerText}일`;
            }else{
                selectDay.innerText = `${year}년 ${currMonth-1}월 ${days.innerText}일`;
            }
            scheduleDate.append(selectDay);
            });
            WrapDay.append(days);
        }else if(year == date.getFullYear() && currMonth == date.getMonth()+1 && i - tMFD.getDay() == today){
            let days =  document.createElement("div");
            days.setAttribute("class","days");
            days.innerHTML = `<span id = 'today'>${today}</span>`;
            days.addEventListener("click", async function() {
            scheduleDate.innerText = "";
            let selectDay = document.createElement('h4');
            selectDay.innerText = `${year}년 ${currMonth}월 ${days.innerText}일`;
            scheduleDate.append(selectDay);
            await fetch('http://127.0.0.1:5000/counseling/get_schedule',{
            method: 'POST',
            body: JSON.stringify({ url: window.location.href }),
            headers: {
            'Content-Type': 'application/json'
            }
            })
            .then(response => response.json())
            .then(data => {
                console.log('받은 데이터:', data);
                data.forEach(user => {
                const div = document.createElement('div');
                div.textContent = `${user.id}: ${user.name}`;
                document.body.appendChild(div);
                });
            })
            .catch(error => {
                console.error('에러 발생:', error);
            });
            });
            WrapDay.append(days);
        }
        else{ // 이번달 날짜 출력
        let days =  document.createElement("div");
            days.setAttribute("class","days");
            days.innerHTML = `<span>${i - tMFD.getDay()}</span>`;
            days.addEventListener("click", function() {
            scheduleDate.innerText = "";
            let selectDay = document.createElement('h4');
            selectDay.innerText = `${year}년 ${currMonth}월 ${days.innerText}일`;
            scheduleDate.append(selectDay);
            });
            WrapDay.append(days);
        }
    }
}
calendar(year,currMonth,today);
// await fetch('http://127.0.0.1:5500/schedule',{
// method:'POST'
// body: JSON.stringify({ url: window.location.href }),
// headers: {
// 'Content-Type': 'application/json'
// })
let changeMonth = document.getElementsByClassName("changeMonth");
for(let i = 0; i < changeMonth.length;i++){ // 월을 바꾸면 그에 맞는 달력으로 변환
    changeMonth[i].addEventListener("click",function () {
        if(i == 0){
            WrapDay.innerText = ""
            if(currMonth == 1){
                year--;
                currMonth = 12;
            }
            else{
                currMonth--;
            }
            calendar(year,currMonth,today);
        }else{
            WrapDay.innerText = ""
            if(currMonth == 12){
                year++;
                currMonth = 1;
            }else{
                currMonth++;
            }
            calendar(year,currMonth,today);
        }
    })
}