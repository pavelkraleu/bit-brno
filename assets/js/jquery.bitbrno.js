/* jQuery  */

/*global $, jQuery, console*/

jQuery(document).ready(function ($) {
    'use strict';


    // extensions

    jQuery.fn.toggleCaron = function () {
        return this.each(function () {
            $(this).toggleClass('icon-caron-up').toggleClass('icon-caron-down');
        });
    };

    jQuery.fn.fullHeight = function () {
        var elem = $(this).first();
        return elem.height() + parseInt(elem.css('margin-top'), 10) + parseInt(elem.css('margin-bottom'), 10) + parseInt(elem.css('padding-top'), 10) + parseInt(elem.css('padding-bottom'), 10);

    };

    function go(current, target, duration, direction) {
        current.addClass('go-out ' + direction);
        target.addClass('go-prep ' + direction).show();

        setTimeout(function () { // start it
            target.addClass('go-in');
        }, 1);

        setTimeout(function () { // cleanup
            current.removeClass('active go-out ' + direction);
            target.removeClass('go-prep go-in' + direction);
            target.addClass('active');
        }, duration);
    }

    function dial(elem, time, callback) {
        $(elem).pieChartCountDown({time : time, color : '#D9D9D9', size : 220, infinite : false, background: 'rgba(0,0,0,0)', callback : callback});
    }


    // main

    $('.collapsible h2').append('<span class="icon icon-caron-up">');

    $('.collapsible.closed .content').hide().parent().find('.icon').toggleCaron();
    $('.collapsible').on('click', 'h2', function (e) {
        $(this).toggleClass('expanded');
        $(this).find('.icon').toggleCaron();
        $(this).parent().find('.content').slideToggle();
    });

    $('.collapsible:first').addClass('first');

    $('.button.full.traversing').append('<span class="icon icon-arrow-right">');


    // page transitions

    //$('.board').css('min-height', $(window).height());
    $('.container').css('height', $(window).height());

    $('.board').each(function () {
        var footer = $(this).find('.footer:first');
        if (footer.length !== 0) {
            $(this).css('padding-bottom', footer.fullHeight());
        }
    });

    $('.board:first').addClass('active');
    $('.board:not(:first)').hide();

    // push forward
    $('.board').on('click', '[data-frw]', function (e) {
        e.preventDefault();
        var target = $($(this).attr('data-frw')),
            current = $('.board.active'),
            duration = 400,
            direction = 'frw';
        go(current, target, duration, direction);
    });

    // push back
    $('.board').on('click', '[data-bck]', function (e) {
        e.preventDefault();
        var target = $($(this).attr('data-bck')),
            current = $('.board.active'),
            duration = 400,
            direction = 'bck';
        go(current, target, duration, direction);
    });

    $('.board').on('click', '[data-dial]', function (e) {
        var waitdial = $($(this).attr('data-dial')),
            confdial = $($('#dial-confirmed'));
        dial(waitdial, waitdial.attr('data-dial-duration'), function () {
            waitdial.css('background', '#D9D9D9');
            go($('.board.active'), $(waitdial.attr('data-dial-to')), 400, 'frw');
            dial(confdial, confdial.attr('data-dial-duration'), function () {
                confdial.css('background', '#D9D9D9');
            });
        });
    });


});