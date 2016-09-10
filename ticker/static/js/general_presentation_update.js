function update_presentation() {
    if (TICKER_UPDATE_URL === undefined) {
        console.log('ticker update url is not defined');
        return
    }

    $.ajax({
        url: TICKER_UPDATE_URL,
        method: 'GET'
    }).done(function (data) {
        var obj = $.parseJSON(data);

        $('#score').html(obj['result'][0] + '-' + obj['result'][1]);

        var field_used = {};
        $('section[data-field]').each(function () {
            field_used[$(this).attr('data-field')] = false;
        });
        if ('games' in obj) {
            $(obj['games']).each(function (i, game) {
                var set_str = '';

                $(game['sets']).each(function (i, set) {
                    set_str += set[2][0] + ':' + set[2][1] + ' ';
                });
                $('.game_sets_' + game['id']).html(set_str);
                $('.game_' + game['id'] + '_team_a').html(game['player_a']);
                $('.game_' + game['id'] + '_team_b').html(game['player_b']);

                if (game['field'] != -1) {
                    field_used[game['field']] = true;
                    var field_section = $('section[data-field="' + game['field'] + '"]');
                    $(field_section).find('h2[data-team="a"]').html(game['player_a']);
                    $(field_section).find('h2[data-team="b"]').html(game['player_b']);

                    $(game['sets']).each(function (i, set) {
                        $(field_section).find('td[data-setnr="' + set[1] + '"][data-team="a"]').html(set[2][0]);
                        $(field_section).find('td[data-setnr="' + set[1] + '"][data-team="b"]').html(set[2][1]);
                    });
                }
            });
            $.each(field_used, function (i, used) {
                    if (used == false) {
                        var field_section = $('section[data-field="' + i + '"]');
                        $(field_section).find('h2[data-team="a"]').html('');
                        $(field_section).find('h2[data-team="b"]').html('');

                        for (var setnr = 1; setnr <= 5; setnr++) {
                            $(field_section).find('td[data-setnr="' + setnr + '"][data-team="a"]').html('0');
                            $(field_section).find('td[data-setnr="' + setnr + '"][data-team="b"]').html('0');
                        }
                    }
            });
        }
    });
}

setInterval(update_presentation, 5000);