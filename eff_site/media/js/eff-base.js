<!--
function update_db() {
    $.getJSON("/efi/update-db/",function(json){
        if (json.status == 'ok') {
            alert('Por favor espere, se está procesando el pedido');
        } else {
            alert('Por favor espere, el ultimo pedido fue hecho: ' + json.last_update);
        }
    });
}

$(document).ready(function() {
    $('ul li:has(ul)').hover(
        function(e){
      $(this).find('ul').fadeIn();
        },
        function(e){
      $(this).find('ul').fadeOut();
        }
    );
});
//-->