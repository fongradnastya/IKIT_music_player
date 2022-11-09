const place1 = document.querySelector(".plaseholder_1");
const place2 = document.querySelector(".plaseholder_2");
const track = document.querySelector(".item__track");

place2.ondragover = Drop()

function Drop(event){
    event.preventDefault();
}
