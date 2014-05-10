//theme changer, dawg
function supports_html5_storage() {
	try {
		return 'localStorage' in window && window['localStorage'] !== null;
	} catch (e) {
		return false;
	}
}

function set_theme(theme) {
	$('link[title="theme"]').attr('href', theme);
	if (supports_html5_storage()) {
		localStorage.theme = theme;
	}
}
function make_loading_dialog() {
	var spinner_html = '<div style="height:200px;">';
	spinner_html += '<span class="spinner"style="position:absolute;display:block;top:50%;left:50%;"id="loading-spinner"></span>';
	spinner_html += '</div>';
	var loading_dialog = bootbox.dialog({
		title: 'Sending to Pi',
		message: spinner_html,
		closeButton: false
	});
	
	var opts = {
		lines: 17, // The number of lines to draw
		length: 0, // The length of each line
		width: 8, // The line thickness
		radius: 60, // The radius of the inner circle
		corners: 0, // Corner roundness (0..1)
		rotate: 0, // The rotation offset
		direction: 1, // 1: clockwise, -1: counterclockwise
		color: '#FFF', // #rgb or #rrggbb or array of colors
		speed: 0.7, // Rounds per second
		trail: 56, // Afterglow percentage
		shadow: false, // Whether to render a shadow
		hwaccel: true, // Whether to use hardware acceleration
		className: 'spinner', // The CSS class to assign to the spinner
		zIndex: 2e9, // The z-index (defaults to 2000000000)
		top: '50%', // Top position relative to parent
		left: '50%' // Left position relative to parent
	};
	
	var target = document.getElementById('loading-spinner');
	var spinner = new Spinner(opts).spin(target);
	return loading_dialog;
}
function open_send_to_pi_dialog() {
	bootbox.dialog({
		title: 'Send to Pi',
		message: '<p>Please paste/enter the URL of the content you\'d like to send to the Pi.</p>' +
				'<div class="input-group">' +
					'<span class="input-group-addon">url</span>' +
					'<input type="text" class="form-control" id="send-to-pi-url" placeholder="http://example.com/">' +
				'</div>',
		buttons: {
			cancel: {
				label: "Cancel",
				className: "btn-default"
			},
			send: {
				label: "Send!",
				className: "btn-primary",
				callback: function() {
					send_url_to_pi($('#send-to-pi-url').val());
				}
			}
		}
	});
}

function send_url_to_pi(url) {
	var loading_dialog = make_loading_dialog();
	$.get('/play?url=' + url).always(function(data, status, xhr) {
		//this is teh callback
		loading_dialog.modal('hide'); // Swaggin :D
		if(xhr.status == 204 || xhr.status == 200) { //success!
			bootbox.alert("Sent to Pi successfully!", function() {
				//redirect to remote cause it's useful.
				window.location.href = "/remote";
			});
		} else {
			bootbox.alert('Sending failed! Check the URL and try again.' + 
						'<p><a class="btn" data-toggle="collapse" data-target="#view-error-details">View details &raquo;</a></p>' +
						'<div class="collapse" id="view-error-details">' + data.responseText + '</div>', function() {
				//open send to pi so they can try again
				open_send_to_pi_dialog();
			});
		}
	});
}


$(document).ready(function () {
	if (supports_html5_storage()) {
		var theme = localStorage.theme;
		if (theme) {
			set_theme(theme);
		}
	} else {
		/* Don't annoy user with options that don't persist */
		$('#theme-dropdown').hide();
	}
    //stick in the fixed 100% height behind the navbar but don't wrap it
    $('#slide-nav.navbar .container').append($('<div id="navbar-height-col"></div>'));
    // Enter your ids or classes
    var toggler = '.navbar-toggle';
    var pagewrapper = '#page-content';
    var navigationwrapper = '.navbar-header';
    var menuwidth = '100%'; // the menu inside the slide menu itself
    var slidewidth = '80%';
    var menuneg = '-100%';
    var slideneg = '-80%';
    $("#slide-nav").on("click", toggler, function (e) {
        var selected = $(this).hasClass('slide-active');
        $('#slidemenu').stop().animate({
            left: selected ? menuneg : '0px'
        });
        $('#navbar-height-col').stop().animate({
            left: selected ? slideneg : '0px'
        });
        $(pagewrapper).stop().animate({
            left: selected ? '0px' : slidewidth
        });
        $(navigationwrapper).stop().animate({
            left: selected ? '0px' : slidewidth
        });
        $(this).toggleClass('slide-active', !selected);
        $('#slidemenu').toggleClass('slide-active');
        $('#page-content, .navbar, body, .navbar-header').toggleClass('slide-active');
    });
    
    var selected = '#slidemenu, #page-content, body, .navbar, .navbar-header';
    
    $(window).on("resize", function () {
        if ($(window).width() > 767 && $('.navbar-toggle').is(':hidden')) {
            $(selected).removeClass('slide-active');
        }
    });
    $('.sendToPiButton').click(function() {
		open_send_to_pi_dialog();
	});

});
