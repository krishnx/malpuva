$(function(){
    // $('#result').html();
    $('#result').hide();
	$('input[name="read_submission"]').on('click', function(e){
	    e.preventDefault();
        e.stopPropagation();
		$.ajax({
			url: '/read',
			data: $('form').serialize(),
			type: 'GET',
			success: function(response){
			    result = JSON.parse(response);
			    var result_html =
                    "<hr/>" +
                    "<div class='result'>" +
                        "<b>Result:</b>" +
                        "<table border=1>" +
                            "<tr>" +
                                "<th>Serial no.</th>"+
                                "<td><b>input1</b></td>" +
                                "<td><b>input2</b></td>" +
                                "<td><b>input3</b></td>" +
                            "</tr>";
			    for (key in result['result']) {
                    result_html +=  "   <tr>";
                    result_html +=  "    <th>" +  key + "</th>";
                    result_html +=  "     <td>" + result['result'][key][0] + "</td>";
                    result_html +=  "     <td>" + result['result'][key][1] + "</td>";
                    result_html +=  "     <td>" + result['result'][key][2] + "</td>";
                    result_html +=  "   </tr>";
                }
                result_html +=  "</table>";
			    result_html +=  "</div>";

			    $('#result').html(result_html);

			},
			error: function(error){
				$('#result').html(error);
			}
		});
		$('#result').show();
	});

	$('input[name="insert_submission"]').on('click', function(e){
	    e.preventDefault();
        e.stopPropagation();
		$.ajax({
            url: '/insert',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                $('#result').html("Insertion was <b>" + JSON.parse(response)['result'] + "</b>");
            },
            error: function (error) {
                $('#result').html(JSON.parse(response)['result']);
            }
		});
		$('#result').show();
    });

	$('input[name="update_submission"]').on('click', function(e){
	    e.preventDefault();
        e.stopPropagation();
		$.ajax({
            url: '/update',
            data: $('form').serialize(),
            type: 'PUT',
            success: function(response) {
                $('#result').html("Update was <b>" + JSON.parse(response)['result'] + "</b>")
            },
            error: function (error) {
                $('#result').html(JSON.parse(response)['result']);
            }
		});
		$('#result').show();
    });
});
