//variables
let cardBeignDragged;
let dropzones = document.querySelectorAll('.dropzone');
let priorities;
// let cards = document.querySelectorAll('.kanbanCard');
let dataColors = [
    {color:"yellow", title:"backlog"},
    {color:"green", title:"to do"},
    {color:"blue", title:"in progress"},
    {color:"purple", title:"testing"},
    {color:"red", title:"done"}
];
let dataCards = {
    config:{
        maxid:0
    },
    cards:[]
};
let theme="light";
//initialize

console.log("token: ", sessionStorage.getItem('token'));
function make_base_auth() {//username_or_token) {
        var tok = sessionStorage.getItem('token');
        var hash = btoa(tok);
        return "Basic " + hash;
}
if(JSON.parse(localStorage.getItem('@kanban:data'))){
    dataCards = JSON.parse(localStorage.getItem('@kanban:data'));
    $.ajax(
            {
                type: "GET",
                url: "http://127.0.0.1:5000/api/v1/tasks",
                dataType: 'json',
                //contentType: "text/json"
                //username: 'eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwOTEzMzI2NiwiZXhwIjoxNjA5MTM2ODY2fQ.eyJpZCI6MTN9.cbxmKoT4-uZgUhrWE3_5tzL0kh9dSo2hmQSsj1NW3vWzuBH_DaXxXs1BpiawDMrxUy2_-f-w8KklmUEc3oLFig',
                async: true,
                headers: {"Authorization": "Basic " + btoa(sessionStorage.getItem('token')+":"+"")},
                //beforeSend: function (xhr){ 
                //    xhr.setRequestHeader('Authorization', make_base_auth()); 
                //},
                data: {}
            }).done(function(data) {
                console.log("Data: ", data);
                max_id = data.config;
                maxid_oma = max_id['maxid'];
                console.log('maxid: ', maxid_oma);
                //console.log('max_id: ', max_id);
                //dataCards.cards = [];
                for ( var i = 0; i < data.cards.length; i++) {
                    const olijo = false;
                    for (var j=0; j < dataCards.cards.length; j++) {
                        if (data.cards[i].id == dataCards.cards[j].id) {
                            olijo = true;
                        }
                    }
                    if (!olijo) {
                        var card = data.cards[i];
                        console.log('cardsit: ', card);

                        var card_id = card['id'];
                        var card_title = card['title'];
                        console.log('card_title');
                        var card_description = card['description'];
                        var card_position = card['position'];
                        var card_priority = card['priority'];

                        const newCard = {
                            id: card_id,
                            title: card_title,
                            description: card_description,
                            position: card_position,
                            priority: card_priority
                        }
                        dataCards.cards.push(newCard)
                        dataCards.config.maxid = maxid_oma;
                    }
            }
        }
        );

        // let setOfIds = new Set();
        // for (var i = 0; i < dataCards.cards.length; i++) {
        //     card = dataCards.cards[i];
        //     if (!setOfIds.has(card.id)) {
        //         setOfIds.add(card.id)
        //     } else {
        //         deleteCard(card.id);
        //     }
        // }
}

$(document).ready(()=>{
    $("#loadingScreen").addClass("d-none");
    theme = localStorage.getItem('@kanban:theme');
    if(theme){
        $("body").addClass(`${theme==="light"?"":"darkmode"}`);
    }
    initializeBoards();
    if(JSON.parse(localStorage.getItem('@kanban:data'))){
        //dataCards = JSON.parse(localStorage.getItem('@kanban:data'));
        $.ajax(
            {
                type: "GET",
                url: "http://127.0.0.1:5000/api/v1/tasks",
                dataType: 'json',
                //contentType: "text/json"
                //username: 'eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwOTEzMzI2NiwiZXhwIjoxNjA5MTM2ODY2fQ.eyJpZCI6MTN9.cbxmKoT4-uZgUhrWE3_5tzL0kh9dSo2hmQSsj1NW3vWzuBH_DaXxXs1BpiawDMrxUy2_-f-w8KklmUEc3oLFig',
                async: true,
                headers: {"Authorization": "Basic " + btoa(sessionStorage.getItem('token')+":"+"")},
                //beforeSend: function (xhr){ 
                //    xhr.setRequestHeader('Authorization', make_base_auth()); 
                //},
                data: {}
            }).done(function(data) {
                console.log("Data: ", data);
                max_id = data.config;
                maxid_oma = max_id['maxid'];
                console.log('maxid: ', maxid_oma);
                //console.log('max_id: ', max_id);
                //dataCards.cards = [];
                // for ( var i = 0; i < data.cards.length; i++) {
                //     const olijo = false;
                //     for (var j=0; j < dataCards.cards.length; j++) {
                //         if (data.cards[i].id == dataCards.cards[j].id) {
                //             olijo = true;
                //         }
                //     }
                //     if (!olijo) {
                for ( var i = 0; i < data.cards.length; i++) {
                        //     const olijo = false;
                var card = data.cards[i];
                console.log('cardsit: ', card);

                var card_id = card['id'];
                var card_title = card['title'];
                console.log('card_title');
                var card_description = card['description'];
                var card_position = card['position'];
                var card_priority = card['priority'];

                const newCard = {
                    id: card_id,
                    title: card_title,
                    description: card_description,
                    position: card_position,
                    priority: card_priority
                }
                dataCards.cards.push(newCard)
                dataCards.config.maxid = maxid_oma;
                }
                    // }
            // }
        }
        );

        let setOfIds = new Set();
        for (var i = 0; i < dataCards.cards.length; i++) {
            card = dataCards.cards[i];
            if (!setOfIds.has(card.id)) {
                console.log("oli jo");
                setOfIds.add(card.id)
            } else {
                deleteCard(card.id);
            }
        }
        initializeComponents(dataCards);
    }
    initializeCards();
    $('#add').click(()=>{
        const title = $('#titleInput').val()!==''?$('#titleInput').val():null;
        const description = $('#descriptionInput').val()!==''?$('#descriptionInput').val():null;
        $('#titleInput').val('');
        $('#descriptionInput').val('');
        if(title && description){
            let id = dataCards.config.maxid+1;
            const newCard = {
                id,
                title,
                description,
                position:"yellow",
                priority: false
            }

            $.ajax(
                {
                    type: "POST",
                    url: "http://127.0.0.1:5000/api/v1/tasks/",
                    dataType: "json",
                    async: true,
                    headers: {"Authorization": "Basic " + btoa(sessionStorage.getItem('token')+":"+"")},
                    data: JSON.stringify(newCard),
                }
            ).done(
                function(data) {

                    uusi_id = data['id'];
                    newCard = {
                        uusi_id,
                        title,
                        description,
                        position:"yellow",
                        priority: false
                    }
                    dataCards.cards.push(newCard);
                    dataCards.config.maxid = uusi_id;

                });
            

       

            //dataCards.cards.push(newCard);
            //dataCards.config.maxid = id;

            let setOfIds = new Set();
            for (var i = 0; i < dataCards.cards.length; i++) {
                card = dataCards.cards[i];
                if (!setOfIds.has(card.id)) {
                    setOfIds.add(card.id)
                } else {
                    deleteCard(card.id);
                }
            }
            save();
            appendComponents(newCard);
            initializeCards();
        }
    });
    $("#deleteAll").click(()=>{
        dataCards.cards = [];
        save();
    });
    

 
   
    $("#theme-btn").click((e)=>{
        e.preventDefault();
        $("body").toggleClass("darkmode");
        if(theme){
            localStorage.setItem("@kanban:theme", `${theme==="light"?"darkmode":""}`)
        }
        else{
            localStorage.setItem("@kanban:theme", "darkmode")
        }
    });
});

function checkCards() {
    for (var i = 0; i < dataCards.cards.length; i++) {
        card = dataCards.cards[i];
        urli =  "http://127.0.0.1:5000/api/v1/task_check/"+(card.id.toString());
        console.log("urli: ", urli);
        $.ajax(
            {
                type: "PUT",
                url: "http://127.0.0.1:5000/api/v1/task_check/"+(card.id.toString()),
                dataType: 'json',
                //contentType: "text/json"
                //username: 'eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwOTEzMzI2NiwiZXhwIjoxNjA5MTM2ODY2fQ.eyJpZCI6MTN9.cbxmKoT4-uZgUhrWE3_5tzL0kh9dSo2hmQSsj1NW3vWzuBH_DaXxXs1BpiawDMrxUy2_-f-w8KklmUEc3oLFig',
                async: true,
                headers: {"Authorization": "Basic " + btoa(sessionStorage.getItem('token')+":"+"")},
                //beforeSend: function (xhr){ 
                //    xhr.setRequestHeader('Authorization', make_base_auth()); 
                //},
                data: JSON.stringify(card)
            }).done(function (data) {

                //dataCards.cards[index] = data.JSON.parse(data)

                if (!data['keep']) {
                    console.log("data['keep']: ", data['keep']);
                    console.log('card: ', JSON.stringify(card));
                    id = dataCards.cards[i].id;
                    deleteCard(id);
                }
    
        });
        


    }
    save();
}

//functions
function initializeBoards(){    
    dataColors.forEach(item=>{
        let htmlString = `
        <div class="board">
            <h3 class="text-center">${item.title.toUpperCase()}</h3>
            <div class="dropzone" id="${item.color}">
                
            </div>
        </div>
        `
        $("#boardsContainer").append(htmlString)
    });
    let dropzones = document.querySelectorAll('.dropzone');
    dropzones.forEach(dropzone=>{
        dropzone.addEventListener('dragenter', dragenter);
        dropzone.addEventListener('dragover', dragover);
        dropzone.addEventListener('dragleave', dragleave);
        dropzone.addEventListener('drop', drop);
    });
}

function initializeCards(){
    cards = document.querySelectorAll('.kanbanCard');
    
    cards.forEach(card=>{
        card.addEventListener('dragstart', dragstart);
        card.addEventListener('drag', drag);
        card.addEventListener('dragend', dragend);
    });
}

function initializeComponents(dataArray){
    //create all the stored cards and put inside of the todo area
    dataArray.cards.forEach(card=>{
        appendComponents(card); 
    })
}

function appendComponents(card){
    //creates new card inside of the todo area
    let htmlString = `
        <div id=${card.id.toString()} class="kanbanCard ${card.position}" draggable="true">
            <div class="content">               
                <h4 class="title">${card.title}</h4>
                <p class="description">${card.description}</p>
            </div>
            <form class="row mx-auto justify-content-between">
                <span id="span-${card.id.toString()}" onclick="togglePriority(event)" class="material-icons priority ${card.priority? "is-priority": ""}">
                    star
                </span>
                <button class="invisibleBtn">
                    <span class="material-icons delete" onclick="deleteCard(${card.id.toString()})">
                        remove_circle
                    </span>
                </button>
            </form>
        </div>
    `
    $(`#${card.position}`).append(htmlString);
    priorities = document.querySelectorAll(".priority");
}

function togglePriority(event){
    event.target.classList.toggle("is-priority");
    dataCards.cards.forEach(card=>{
        if(event.target.id.split('-')[1] === card.id.toString()){
            card.priority=card.priority?false:true;
        }
    })
    save();
}

function deleteCard(id){
    dataCards.cards.forEach(card=>{
        if(card.id === id){
            let index = dataCards.cards.indexOf(card);
            console.log(index)
            dataCards.cards.splice(index, 1);
            console.log(dataCards.cards);
            save();
        }
    })
}


function removeClasses(cardBeignDragged, color){
    cardBeignDragged.classList.remove('red');
    cardBeignDragged.classList.remove('blue');
    cardBeignDragged.classList.remove('purple');
    cardBeignDragged.classList.remove('green');
    cardBeignDragged.classList.remove('yellow');
    cardBeignDragged.classList.add(color);
    position(cardBeignDragged, color);
}

function save(){
    localStorage.setItem('@kanban:data', JSON.stringify(dataCards));
}

function position(cardBeignDragged, color){
    const index = dataCards.cards.findIndex(card => card.id === parseInt(cardBeignDragged.id));
    dataCards.cards[index].position = color;
    card = dataCards.cards[index];
    console.log("Lähetettävä siirretty kortti: ", JSON.stringify(card));
    $.ajax(
        {
            type: "PUT",
            url: "http://127.0.0.1:5000/api/v1/task/"+(card.id.toString()),
            dataType: 'json',
            //contentType: "text/json"
            //username: 'eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwOTEzMzI2NiwiZXhwIjoxNjA5MTM2ODY2fQ.eyJpZCI6MTN9.cbxmKoT4-uZgUhrWE3_5tzL0kh9dSo2hmQSsj1NW3vWzuBH_DaXxXs1BpiawDMrxUy2_-f-w8KklmUEc3oLFig',
            async: true,
            headers: {"Authorization": "Basic " + btoa(sessionStorage.getItem('token')+":"+"")},
            //beforeSend: function (xhr){ 
            //    xhr.setRequestHeader('Authorization', make_base_auth()); 
            //},
            data: JSON.stringify(card)
        }).done(function (data) {
            //dataCards.cards[index] = data.JSON.parse(data);
            dataCards.card[index].position = data.position

        });
    }


    // let setOfIds = new Set();
    // for (var i = 0; i < dataCards.cards.length; i++) {
    //     card = dataCards.cards[i];
    //     if (!setOfIds.has(card.id)) {
    //         console.log("oli jo");
    //         setOfIds.add(card.id)
    //     } else {
    //         deleteCard(card.id);
    //     }
    // }


    save();
    //localStorage('@kanban:data')
    checkCards();


//cards
function dragstart(){
    dropzones.forEach( dropzone=>dropzone.classList.add('highlight'));
    this.classList.add('is-dragging');
}

function drag(){
    
}

function dragend(){
    dropzones.forEach( dropzone=>dropzone.classList.remove('highlight'));
    this.classList.remove('is-dragging');
}

// Release cards area
function dragenter(){

}

function dragover({target}){
    this.classList.add('over');
    cardBeignDragged = document.querySelector('.is-dragging');
    if(this.id ==="yellow"){
        removeClasses(cardBeignDragged, "yellow");
        
    }
    else if(this.id ==="green"){
        removeClasses(cardBeignDragged, "green");
    }
    else if(this.id ==="blue"){
        removeClasses(cardBeignDragged, "blue");
    }
    else if(this.id ==="purple"){
        removeClasses(cardBeignDragged, "purple");
    }
    else if(this.id ==="red"){
        removeClasses(cardBeignDragged, "red");
    }
    
    this.appendChild(cardBeignDragged);
}

function dragleave(){
  
    this.classList.remove('over');
}

function drop(){
    this.classList.remove('over');
}