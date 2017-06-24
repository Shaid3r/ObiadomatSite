buttons_html = '<button type="button" class="select_all btn btn-default">Zaznacz wszystko</button>\
                <button type="button" class="deselect_all btn btn-default">Odznacz wszystko</button>';

$(document).ready(function() {
    // Multiselect
    $('.selectpicker').multiselect({
        nonSelectedText: "Nic",
        nSelectedText: "wybrane opcje",
        allSelectedText: "Wszystkie wybrane"
    }).next().after(buttons_html).parent().addClass("btn-group");
    $('.select_all').click(function() {
        $(this).prevAll('.selectpicker').first().multiselect('selectAll', false).multiselect('updateButtonText');
    });
    $('.deselect_all').click(function() {
        $(this).prevAll('.selectpicker').first().multiselect('deselectAll', false).multiselect('updateButtonText');
    }); // End Multiselect

    // Navbar active
    var path = $(location).attr('pathname').split("/");
    if (path[path.length-1] != '' && path[path.length-1] != 'profile') {
		var e = path[path.length-1];
		e = '.nav-sidebar li a[href="/' + e + '"]';
		$('.active').removeClass("active");
		if ($(e).length == 1) {
			$(e).parent().addClass("active");
		}
	}

    // Łączna cena dań
    if ($('.table-dish').length != 0) {
        function cena(object) {
            var c = parseFloat(object.text().replace(',', '.'));
            var ilosc = parseInt(object.next().children().val());
            var wynik = (c * ilosc).toFixed(2).toString().replace('.', ',');
            object.nextAll('.lCena').text(wynik);
        }

        function razem(a, b) {
            var wynik = 0, c;

            a.each(function() {
                c = parseFloat($(this).text().replace(',', '.'));
                wynik = wynik + c;
            });
            b.text(wynik.toFixed(2).toString().replace('.', ','));
        }


        $('.cena').each(function() {
            cena($(this));
            razem($('.lCena'), $('.razem'));
        }).next().children().change(function() {
            cena($(this).parent().prev());
            razem($('.lCena'), $('.razem'));
        });
    }
});

