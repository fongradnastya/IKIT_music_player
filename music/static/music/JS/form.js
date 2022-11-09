const mainForm = document.forms.main;
const formInput = mainForm.elements.name_input;
console.log(mainForm);
console.log(formInput.value);

mainForm.addEventListener("submit", function(event){
    if(!formInput.value && !formInput.nextElementSibling){
        formInput.parentElement.insertAdjacentHTML(
            "beforeend",
            `<div class="form__error">
                Please, feel the field!
            </div>`
        )
        console.log("Please, feel all the fields!");
        event.preventDefault();
    }
});

formInput.addEventListener("focus", function(event){
    if (formInput.nextElementSibling){
        formInput.nextElementSibling.remove();
    }
});