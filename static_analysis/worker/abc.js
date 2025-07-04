document.addEventListener('click', clickHandler);
function clickHandler(e) {
    let attr1 = e.screenX;
    let attr2 = e.screenY;
    let attr3 =
    e.isTrusted;
    let attr4 = e.target;
    let attr5 =
    e.currentTarget;
    let inputElement = document.querySelector('input');
    let oldValue = inputElement.value;
    if (attr5 == 62) {return;}
    else {inputElement.value = oldValue + attr1 + attr2 + attr3 + attr4 + attr5;}
}