
let date = new Date();
let year = date.getFullYear();
let currMonth = date.getMonth()+1;
let today = date.getDate();
let weekday = date.getDay();
let WrapDay = document.getElementById("wrap_day");
let scheduleDate = document.getElementById("scheduleDate");
let schedule = document.getElementById("schedule");
var btnWrap = document.getElementsByClassName("buttonWrap");

    
function change() {
    let appoints =document.getElementsByClassName("appointmentInfo");
    for(let i = 0; i< appoints.length; i++){
        const appoint = appoints[i]
        let buttonWrap = document.createElement("div")
        buttonWrap.setAttribute("class","buttonWrap");
        let cancel = document.createElement("button"); // 예약 취소 버튼
        cancel.innerText = "예약취소"
        cancel.setAttribute("class","cancel");
        // 예약 취소 버튼 이벤트 처리
        cancel.addEventListener("click",function(){
          
                const appointmentSeq = element["APPOINTMENT_SEQ"] ;
           
            const params = new URLSearchParams({appointmentSeq}).toString();
            window.location.href = `/counseling/cancel-appointment?${params}`;
        });
        let scheduleChange = document.createElement("button"); // 예약 변경 버튼
        scheduleChange.setAttribute("class","scheduleChange");
        scheduleChange.innerText = "예약 변경"
        // 예약 변경 버튼 이벤트 처리
        scheduleChange.addEventListener("click",function(){
            
        });
        buttonWrap.appendChild(cancel);
        buttonWrap.appendChild(scheduleChange);
        appoint.appendChild(buttonWrap);
        schedule.appendChild(appoint)
        appoint.addEventListener("click",function(e){
            const clicked = e.currentTarget.closest(".appointmentInfo");
            if (!clicked) return;
            // 현재 이미 선택된 요소
            const currentlySelected = document.querySelector(".appointmentInfo.selected");
            // 이미 선택된 걸 다시 클릭했으면 해제
            if (currentlySelected === clicked) {
                clicked.classList.remove("selected");
            } else { // 이외의 것을 선택하면 기존 선택된 것의 classList에서 selected를 제거
                if (currentlySelected) currentlySelected.classList.remove("selected");
                    // 현재 선택한 것의 classList에 selected 클래스 추가
                    clicked.classList.add("selected");
                }
            })
    }
}

change()

// 날짜 클릭하면 당일 schedule 보여주는 함수
function showSchedule(days){
    days.addEventListener("click", async function() {
        schedule.innerHTML = "";
        scheduleDate.innerText = "";
        let selectDay = document.createElement('h4');
        selectDay.innerText = `${year}년 ${currMonth}월 ${days.innerText}일`;
        scheduleDate.append(selectDay);
        await fetch('http://127.0.0.1:5000/counseling/get_schedule',{
            method: 'POST',
            body: JSON.stringify({"year":year,"month":currMonth,"day":days.innerText}),
            headers: {
            'Content-Type': 'application/json'
            }
            })
            .then(response => response.json())
            .then(data => {
                if(data.length == 0){
                    schedule.innerHTML = "<p>등록된 일정이 없습니다.</p>"
                }else{
                        data.forEach(element => {
                            let name = element["NAME"];
                            let tel = element["CONTACT"]
                            let address = element["ADDRESS"];
                            let appointDate = element["APPOINTMENT_DATE"];
                            let appointTime = element["APPOINTMENT_TIME"];
                            appointDate = appointDate.replace("GMT","GMT +0900") // 표준시를 한국표준시로 바꿈
                            appointDate = appointDate.replace("00:00:00",appointTime) // 00:00:00시를 불러온 시간 데이터로 바꿈
                            appointDate = new Date(appointDate);
                            let appoint = document.createElement("div");
                            appoint.setAttribute("class","appointmentInfo") 
                            // 예약한 센터와 시간 정보를 담은 요소 만들기기
                            appoint.innerHTML = `<div class = 'center-info'><h3>${name}</h3><span class = 'center-info'>${address}</span>
                            <span class = 'center-info'>${tel}</span></div>
                            <div class = 'time'><p>${appointDate.getFullYear()}년 ${appointDate.getMonth()}월 ${appointDate.getDate()}일</p>
                            <p>${appointDate.getHours()}시 ${appointDate.getMinutes()}분</p></div>`;
                            
                            // 예약 취소 예약 변경 버튼 만들기기
                            let buttonWrap = document.createElement("div")
                            buttonWrap.setAttribute("class","buttonWrap");
                            let cancel = document.createElement("button"); // 예약 취소 버튼
                            cancel.innerText = "예약취소"
                            cancel.setAttribute("class","cancel");
                            // 예약 취소 버튼 이벤트 처리
                            console.log(typeof element["APPOINTMENT_SEQ"])
                            cancel.addEventListener("click",function(e){
                                     e.stopPropagation(); // 부모의 클릭 이벤트 방지
                            // 예약 취소 기능 실행
                                    const appointmentSeq = {
                                        appointmentSeq:element["APPOINTMENT_SEQ"] 
                                    };
                                    const params = new URLSearchParams(appointmentSeq).toString();
                                    window.location.href = `/counseling/cancel-appointment?${params}`;
                            });
                            let scheduleChange = document.createElement("button"); // 예약 변경 버튼
                            scheduleChange.setAttribute("class","scheduleChange");
                            scheduleChange.innerText = "예약 변경"
                            // 예약 변경 버튼 이벤트 처리
                            scheduleChange.addEventListener("click",function(e){
                                e.stopPropagation(); // 부모의 클릭 이벤트 방지
                                // 예약 변경 기능 실행
                                const appointmentSeq = {
                                        appointmentSeq:element["APPOINTMENT_SEQ"] 
                                    };
                                    const params = new URLSearchParams(appointmentSeq).toString();
                                    window.location.href = `/counseling/cancel-appointment?${params}`;
                            });
                            buttonWrap.appendChild(cancel);
                            buttonWrap.appendChild(scheduleChange);
                            appoint.appendChild(buttonWrap);
                            schedule.appendChild(appoint)
                            appoint.addEventListener("click",function(e){
                                const clicked = e.currentTarget.closest(".appointmentInfo");
                                    if (!clicked) return;
                                    // 현재 이미 선택된 요소
                                    const currentlySelected = document.querySelector(".appointmentInfo.selected");
                                    // 이미 선택된 걸 다시 클릭했으면 해제
                                    if (currentlySelected === clicked) {
                                        clicked.classList.remove("selected");
                                    } else { // 이외의 것을 선택하면 기존 선택된 것의 classList에서 selected를 제거
                                        if (currentlySelected) currentlySelected.classList.remove("selected");
                                        // 현재 선택한 것의 classList에 selected 클래스 추가
                                        clicked.classList.add("selected");
                                    }
                            })
                        })
                }
            })
            .catch(error => {
                console.error('에러 발생:', error);
            });
        })
}

// 캘린더 출력 함수
function calendar(year,currMonth,today) {
    WrapDay.innerHTML = ""
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
            let tempYear;
            let tempMonth;
            if(currMonth == 1){
                tempYear = year -1
                selectDay.innerText = `${tempYear}년 12월 ${days.innerText}일`;
            }else{
                tempMonth = currMonth -1
                selectDay.innerText = `${year}년 ${tempMonth}월 ${days.innerText}일`;
            }
            
            scheduleDate.append(selectDay);
            });
            WrapDay.append(days);
        }else if(year == date.getFullYear() && currMonth == date.getMonth()+1 && i - tMFD.getDay() == today){
            let days =  document.createElement("div");
            days.setAttribute("class","days");
            days.innerHTML = `<span id = 'today'>${today}</span>`;
            showSchedule(days)
            WrapDay.append(days);
        }
        else{ // 이번달 날짜 출력
        let days =  document.createElement("div");
            days.setAttribute("class","days");
            days.innerHTML = `<span>${i - tMFD.getDay()}</span>`;
            showSchedule(days);
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
// })z

let changeMonth = document.getElementsByClassName("changeMonth");
for(let i = 0; i < changeMonth.length;i++){ // 월을 바꾸면 그에 맞는 달력으로 변환
    changeMonth[i].addEventListener("click",function () {
        if(i == 0){
            if(currMonth == 1){
                year--;
                currMonth = 12;
            }
            else{
                currMonth--;
            }
            calendar(year,currMonth,today);
        }else{
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
