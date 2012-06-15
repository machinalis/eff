(function($){
    $(document).ready(function(){
        function check_values(){
            if($('#id_is_client').is(':checked')){
                $('label[for="id_first_name"]').addClass('required');
                $('label[for="id_last_name"]').addClass('required');
                $('label[for="id_company"]').parent().parent().show();
            }
            else{
                $('label[for="id_first_name"]').removeClass('required');
                $('label[for="id_last_name"]').removeClass('required');
                $('label[for="id_company"]').parent().parent().hide();
            }
        };
        // Call check_values when load the change_form for user
        check_values();
        
        // Call check_values when checkbox is clicked
        $('#id_is_client').click(function(){
            check_values();
        });            
    });
})(django.jQuery);
