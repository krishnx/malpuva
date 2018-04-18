/**
 * Created by vauser on 20/3/18.
 */
function validate_inputs() {
    empty = [];
    $('input[name$="_input"]').each(function () {
	    var i = $(this).val().trim();
	    if (!i) {
	        name = $(this).attr('name').replace('_input', '');
            empty.push(name);
        }
    });

    return empty;
}

$(function(){
    $("input[name$='_submission']").on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        form_name = $(this).attr('name').replace('_submission', '');

        not_filled_inputs = validate_inputs();
        if (not_filled_inputs.length < 1) {
            $.ajax({
                url: '/' + form_name,
                data: $('form').serialize(),
                type: 'GET',
                success: function (response) {
                    $('#result').html(JSON.parse(response)['result']);
                    if (JSON.parse(response)['status'] == 'success') {
                        $('#result').css('color', '#32CD32');
                    }
                    else {
                        $('#result').css('color', '#B22222');
                    }
                },
                error: function (error) {
                    $('#result').html(JSON.parse(response)['result']);
                    $('#result').css('color', '#B22222')
                }
            });
        }
        else {
            $('#result').html("Please input values for: <b>" + not_filled_inputs + "</b>");
            $('#result').css('color', '#B22222')
        }

        $("#result").show();
    });
});