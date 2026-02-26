document.addEventListener("DOMContentLoaded", function(){
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function(e){
            let required = form.querySelectorAll("[required]");
            required.forEach(field => {
                if(field.value.trim() === ""){
                    alert("Please fill all required fields");
                    e.preventDefault();
                }
            });
        });
    });
});