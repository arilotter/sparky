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
    
	$('#sendModal .modal-footer .btn-primary').click(function () {
		var spinner = '<div style="height:200px;">';
		spinner += '<span class="spinner"style="position:absolute;display:block;top:50%;left:50%;"id="send-loading-spinner"></span>';
		spinner += '</div>';
		var loading_dialog = bootbox.dialog({
			title: 'Sending to Pi',
			message: spinner,
			closeButton: false
		});
		
		activate_spinner();
		
		$.get('/play?url=' + $('#send-to-pi-url').val()).always(function(data, status, xhr) {
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
					$('#sendModal').modal();
				});
			}
		});
		return true; //let it close, let it close, can't hold it back anymoooore
	});

});
