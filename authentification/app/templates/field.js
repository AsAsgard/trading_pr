$("#select").on('change', function(){
    if($(this).val() == "PUT"){
        $("#input").show();
    } else {
        $("#input").hide();
    }
})
