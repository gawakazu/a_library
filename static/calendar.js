var today = new Date()
var year = today.getFullYear()
var current_year = year
var month = today.getMonth()+ 1 
var current_month = month
var prev = document.getElementById('prev')
var now =today.getDate()
prev.addEventListener('click',nextStage,false)

var next = document.getElementById('next')
next.addEventListener('click',nextStage2,false)
calendar()
function nextStage(){
    today.setMonth(today.getMonth()-1)
    month = today.getMonth() +1 
    year = today.getFullYear()           
    clean()
}
function nextStage2(){
    today.setMonth(today.getMonth()+1)
    month = today.getMonth() + 1
    year = today.getFullYear()           
    clean()
}
function clean(){
    var calendar_box = document.getElementById('calendar_box')
    while(calendar_box.firstChild ){
        calendar_box.removeChild(calendar_box.firstChild );
        }
    var yearMonth = document.getElementById('year_month')
        yearMonth.removeChild(yearMonth.firstChild );
    calendar()
}
//--------------------------day,lastDate-------------------------------//
function calendar(){
    console.log("--u-----",year,month,now,current_year,current_month)
    var day = new Date(year,month-1,1).getDay()
    var lastDate = new Date(year,month,0).getDate()
    var cal = ["<th> 日 </th>","<th> 月 </th>","<th> 火 </th>","<th> 水 </th>","<th> 木 </th>","<th> 金 </th>","<th> 土 </th>"];
    for(var i=0;i<day;i++){
        cal.push("<td class='td4'>-</td>")
    }
    var num = cal.length
    for(var j=1;j<=lastDate;j++){
        if(j==now && year ==current_year && month==current_month){
            cal.push("<td class='td5'>"+j+"</td>")
        }else{
             cal.push("<td class='td4'>"+j+"</td>")
        }
    }
    var cal2 = []
    xxx = ""
    for(var j=0;j<cal.length;j++){
        if((j+1)%7==0){
            xxx += cal[j]
            cal2.push(xxx)
            xxx = ""
        }else{
            xxx += cal[j]
        }
    }
    cal2.push(xxx)
    for(var j=0;j<cal2.length;j++){
        var calendar_box = document.getElementById('calendar_box')
        var calXX = document.createElement('tr')
        calXX.innerHTML = (cal2[j])
        calendar_box.appendChild(calXX)
        }
    
    var yearMonth = document.getElementById('year_month')
    var title = document.createElement('p')
    title.innerHTML = year + "/" + month
    yearMonth.appendChild(title)
}