var menuItemPos, thirdItemPos, thirdItemWidth, oneThroughThreeWidth, triggerWidth, requiresSetHeight;

// This is used when the user clicks a directional arrow in the main nav.
function getScrollValue(direction) {
	var scrollValue = 0;
	var currentLeft = $('.mm-menu-wrapper').scrollLeft();
	var menuItemWidth = $('.mm-menu-items').width();
	var menuWrapperWidth = $('.mm-menu-wrapper').width();
	var menuToWrapperProportion = menuItemWidth / menuWrapperWidth;

	if (direction == 'right') {
		if (menuToWrapperProportion <= 2) {
			// If the quotient is less than 2, then we can scroll to the end and not miss anything
			scrollValue = menuItemWidth - menuWrapperWidth;
		} else {
			// Otherwise, advance the scroll in increments equal to the wrapper's width
			scrollValue = currentLeft + menuWrapperWidth;
		}
	}
	if (direction == 'left') {
		if (menuToWrapperProportion <= 2) {
			scrollValue = 0;
		} else {
			scrollValue = currentLeft - menuWrapperWidth;
		}
	}

	return scrollValue;
}

// Trigger the menu item left/right arrows if width is small enough,
// and expand the search box if width is large enough.
function fitMenuElements() {
	var menuItemWidth = $('.mm-menu-items').width();
	var menuWrapperWidth = $('.mm-menu-wrapper').width();

	var menuUserInfoPos = $('.mm-user-info').position();
	var menuItemPos = $('.mm-menu-items').position();

	if (menuItemWidth > menuWrapperWidth) {
		$('.mm-scroll-arrows').addClass('visible-inline-block');
		$('.mm-menu-wrapper').addClass('mm-scroll-arrows-visible');
	} else {
		$('.mm-scroll-arrows').removeClass('visible-inline-block');
		$('.mm-menu-wrapper').removeClass('mm-scroll-arrows-visible');
	}

	if (menuUserInfoPos.left - (menuItemPos.left + menuItemWidth) > 300) {
		$('.mm-search-field').addClass('mm-search-field-full');
	} else {
		$('.mm-search-field').removeClass('mm-search-field-full');
	}
}

// There are no traditional breakpoints. We go to the smaller size when we run out 
// of room, which we're defining as when the window to scroll the menu gets smaller 
// than the width of the first three elements.
function goToMobileSize() {
	var menuWrapperWidth = $('.mm-menu-wrapper').width();

	if (($('#flex-nav').hasClass('full-size') || $('#flex-nav').hasClass('condensed-size')) && menuWrapperWidth < oneThroughThreeWidth) {
		triggerWidth = $(window).width();
		$('#flex-nav').removeClass('full-size').removeClass('condensed-size').addClass('mobile-size');
		$('.mm-minimize-button, .mm-maximize-button').css('display','none');
	} 
	if ($('#flex-nav').hasClass('mobile-size') && menuWrapperWidth > triggerWidth) {
		var classToAdd = 'full-size';
		if($.cookie('mmSizePref') == "condensed") {
			classToAdd = 'condensed-size';
			$('.mm-maximize-button').css('display','block');
		} else {
			$('.mm-minimize-button').css('display','block');
		}

		$('#flex-nav').removeClass('mobile-size').addClass(classToAdd);
	}
}

function minimizeMenuBar() {
	$('#main-menu').removeClass('full-size').addClass('condensed-size');
	$('#flex-nav').removeClass('full-size').addClass('condensed-size');
	
	$('.mm-maximize-button').css('display','block');
	$('.mm-minimize-button').css('display','none');

	fitMenuElements();
}
function maximizeMenuBar() {
	$('#main-menu').removeClass('condensed-size').addClass('full-size');
	$('#flex-nav').removeClass('condensed-size').addClass('full-size');
	
	$('.mm-minimize-button').css('display','block');
	$('.mm-maximize-button').css('display','none');

	fitMenuElements();
}

// This makes the navbar work correctly with fixed-height content areas.
// As of writing this, it's only necessary with report builder.
function changeContentHeight() {
	var navHeight = $('#flex-nav').height();
	$('.requires-set-height').css('height','calc(100% - '+navHeight+'px)');
}

// Want to have drop shadows serve as a visual cue to scroll horizontally, but
// don't want them to appear when you can't scroll in that direction.
function controlShadows() {
	var currentLeft = $('.mm-menu-wrapper').scrollLeft();
	var menuItemWidth = $('.mm-menu-items').width();
	var menuWrapperWidth = $('.mm-menu-wrapper').width();

	if (currentLeft !== 0) {
		$('.mm-scroll-left-arrow').addClass('has-shadow');
	} else {
		$('.mm-scroll-left-arrow').removeClass('has-shadow');
	}

	if (menuItemWidth - (menuWrapperWidth + currentLeft) >= 3) {
		$('.mm-scroll-right-arrow').addClass('has-shadow');
	} else {
		$('.mm-scroll-right-arrow').removeClass('has-shadow');
	}
}

$(document).ready(function() {
	menuItemPos = $('.mm-menu-items').position();
	thirdItemPos = $('.mm-menu-items > li:nth-child(3)').position();
	thirdItemWidth = $('.mm-menu-items > li:nth-child(3)').width();
	oneThroughThreeWidth = (thirdItemPos.left + thirdItemWidth) - menuItemPos.left;
	requiresSetHeight = $('.requires-set-height').length;


	// IE fallback for pointer-events on search button
	if ($('html').hasClass('lt11')) {
		$('.mm-search-icon').click(function() {
			$('.mm-search-field').focus();
		});
	}

	// There is a somewhat intentional progression here, so be careful if you shift around.
	fitMenuElements();
	controlShadows();
	goToMobileSize();
	if ($.cookie('mmSizePref') == "condensed") { minimizeMenuBar(); }
	if (requiresSetHeight > 0) { changeContentHeight(); } // Needs to happen after height of menu bar is set
	// End of somewhat intentional progression

	$(window).resize(function() {
		fitMenuElements();
		controlShadows();
		goToMobileSize();
		if (requiresSetHeight > 0) { changeContentHeight(); }
	});

	$('.mm-has-submenu > a').click(function(e) {
		if (!$(this).parent().hasClass('active')) {
			e.preventDefault();

			$('.mm-has-submenu.active').each(function() {
				$(this).removeClass('active');
			});

			$(this).parent().addClass('active');

			setTimeout(function () { 
				fitMenuElements();
				// $('.mm-menu-wrapper').scrollLeft(30);
			}, 100);
		}
	});
	
	$('.mm-arrow-right').click(function() {
		controlShadows();

		$('.mm-menu-wrapper').animate({
			scrollLeft: getScrollValue('right'),
		}, 500);
	});

	$('.mm-arrow-left').click(function() {
		controlShadows();

		$('.mm-menu-wrapper').animate({
			scrollLeft: getScrollValue('left'),
		}, 500);
	});

	$('.mm-menu-wrapper').scroll(function() {
		controlShadows();
	});

	$('.mm-search-field').on('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend', function() {
		fitMenuElements();
	});

	$('.mm-user-icon').click(function() {
		$('.mm-user-mobile-menu-wrapper').toggleClass('active');
		$('body').append('<div class="mm-user-menu-click-space"></div>');
	});

	$('.mm-user-name').click(function() {
		if ($('.mm-user-mobile-menu-wrapper').hasClass('active')) {
			$('.mm-user-mobile-menu-wrapper').toggleClass('active');
			$('.mm-user-menu-click-space').remove();
		}
	});

	$(document).on('click', '.mm-user-menu-click-space', function() {
		$('.mm-user-mobile-menu-wrapper').toggleClass('active');
		$('.mm-user-menu-click-space').remove();
	});

	$('.mm-minimize-button').click(function() {
		$.removeCookie('mmSizePref');
		$.cookie('mmSizePref', 'condensed', { expires: 1000, path: '/' });

		minimizeMenuBar();
	    if (requiresSetHeight > 0) { changeContentHeight(); }
	});

	$('.mm-maximize-button').click(function() {
		$.removeCookie('mmSizePref');
		$.cookie('mmSizePref', 'full', { expires: 1000, path: '/' });

		maximizeMenuBar();
	    if (requiresSetHeight > 0) { changeContentHeight(); }
	});
});