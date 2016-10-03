function update_ticker() {

        $.ajax({
            url: MATCH_TICKER_JSON_URL,
            method: 'get'
        }).done(function(data) {
            var obj = $.parseJSON(data);
            $('#team_a').html(obj['team_a']);
            $('#team_b').html(obj['team_b']);
            $('#score').html(obj['result'][0]+ ':' + obj['result'][1]);

            var inp_values = $('input[name^="field_"]');
            var field_used = {};
            $.each(inp_values, function (i, elm) {
               field_used[elm.value] = false;
            });

            for (var i = 0; i < obj['games'].length; i++) {
                // update the fields
                $('#' + obj['games'][i]['id'] + '_name').html(obj['games'][i]['name']);
                $('#' + obj['games'][i]['id'] + '_player_a').html(obj['games'][i]['player_a']);
                $('#' + obj['games'][i]['id'] + '_player_b').html(obj['games'][i]['player_b']);
                // update the sets
                var game = obj['games'][i];
                // if the game is associated to a field we update that as well
                if (game['field'] != -1) {
                    $('#' + game['field'] + '_name').html(game['name']);
                    $('#' + game['field'] + '_player_a').html(game['player_a']);
                    $('#' + game['field'] + '_player_b').html(game['player_b']);
                    field_used[game['field']] = true;
                }

                for (var j = 0; j < game['sets'].length; j++) {
                    $('#set_' + game['sets'][j][0]).html(
                            game['sets'][j][2][0] + ':' + game['sets'][j][2][1]
                    );
                    if (game['field'] != -1) {
                        $('#' + game['field'] + '_' + j + '_team_a').html(game['sets'][j][2][0]);
                        $('#' + game['field'] + '_' + j + '_team_b').html(game['sets'][j][2][1]);
                    }
                }
            }
            // empty ununsed fields
            $.each(field_used, function (fieldid, elm) {
                console.log(fieldid, elm);
                if (elm == false) {
                    $('#' + fieldid + '_name').html('');
                    $('#' + fieldid + '_player_a').html('');
                    $('#' + fieldid + '_player_b').html('');
                    for (var i = 0; i < 5; i++) {
                        $('#' + fieldid + '_' + i + '_team_a').html('');
                        $('#' + fieldid + '_' + i + '_team_b').html('');
                    }
                }
            })
        })
    }

    setInterval(update_ticker, 20000);