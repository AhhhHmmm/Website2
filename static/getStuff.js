function getBlocks() {
	var subjectID = document.getElementById('subject').value;
	
	if (subjectID)
	{
	options = fetch('get_blocks', 
	{
	method: 'POST',
	headers: {
		'Accept': 'application/json, text/plain, */*',
		'Content-Type': 'application/json'
	},
	body: JSON.stringify({subject_id : subjectID})
	}).then(response => {return response.text();})
	.then((data) => {
			var block = document.getElementById('block');
			block.outerHTML = data;
			$('#block').attr('onchange','getUsers()')
			$('select').each(function() {
				$(this).addClass('form-control');
			});
	});
	}
}

function getUnits() {
	var subjectID = document.getElementById('subject').value;

	if (subjectID)
	{
	options = fetch('get_units', 
	{
	method: 'POST',
	headers: {
		'Accept': 'application/json, text/plain, */*',
		'Content-Type': 'application/json'
	},
	body: JSON.stringify({subject_id : subjectID})
	}).then(response => {return response.text();})
	.then((data) => {
			var unit = document.getElementById('unit');
			unit.outerHTML = data;
			$('#unit').attr('onchange','getLessons()')
			$('select').each(function() {
				$(this).addClass('form-control');
			});
	});
	}
}

function getBlocksAndUnits() {
	getUnits();
	getBlocks();
}

function getLessons() {
	var unitID = document.getElementById('unit').value;

	if (unitID)
	{
	options = fetch('get_lessons', 
	{
	method: 'POST',
	headers: {
		'Accept': 'application/json, text/plain, */*',
		'Content-Type': 'application/json'
	},
	body: JSON.stringify({unit_id : unitID})
	}).then(response => {return response.text();})
	.then((data) => {
			var lesson = document.getElementById('lesson');
			lesson.outerHTML = data;
			$('select').each(function() {
				$(this).addClass('form-control');
			});
	});
	}
}

function getUsers() {
	var blockID = document.getElementById('block').value;

	if (blockID)
	{
	options = fetch('get_users', 
	{
	method: 'POST',
	headers: {
		'Accept': 'application/json, text/plain, */*',
		'Content-Type': 'application/json'
	},
	body: JSON.stringify({block_id : blockID})
	}).then(response => {return response.text();})
	.then((data) => {
			var user = document.getElementById('user');
			user.outerHTML = data;
			$('select').each(function() {
				$(this).addClass('form-control');
			});
	});
	}
}