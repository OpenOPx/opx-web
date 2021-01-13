const icesitoggle = document.getElementsByClassName('icesi-toggle');
for(i = 0; i < icesitoggle.length; i++){
    icesitoggle[i].addEventListener('click', function(){
        this.classList.toggle('active')
    })
}