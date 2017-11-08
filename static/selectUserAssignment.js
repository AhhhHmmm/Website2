$(document).ready(function() {

	$('form').each(function() {
		$(this).on('submit', function(event) {

			$.ajax({
				// Send the part.id, user.id, and user response.
				data : 
				{ 
					lesson_id : $('#lesson').val(),
					user_id : $('#user').val()
				},
				type : 'POST',
				url : '/table3'
			});

			event.preventDefault();
		});
	});

});