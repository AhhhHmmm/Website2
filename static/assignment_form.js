$(document).ready(function() {

	part_template = _.template($("#part_template").html());

	$('#add_part').on('click', function() {
		var part_num = Number($("input[name='part_count']").val()) + 1;
		$("input[name='part_count']").val(part_num);

		part_compiled = part_template();
		$(this).before(part_compiled)
	});

});