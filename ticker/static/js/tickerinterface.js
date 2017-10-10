$(document).ready(function () {

    $('[data-toggle="popover"]').popover();


    $('input[name="unlock_field"]').on('change', function () {
        if ($(this).prop('checked') == true) {
            $('select[name^="player_"]').prop('disabled', false);
        } else {
            $('select[name^="player_"]').prop('disabled', true);
        }
    });

    $('form[name^="field_"]').find(':button').on('click', function () {
        event.preventDefault();
        var calling_button = this.name;
        var calling_value = this.value;
        var action = $(this).closest('form').attr('action');
        var csrftoken = $(this).closest('form').find('input[name="csrfmiddlewaretoken"]').val();

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                    // Send the token to same-origin, relative URLs only.
                    // Send the token only if the method warrants CSRF protection
                    // Using the CSRFToken value acquired earlier
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        var obj = {};
        obj[calling_button] = calling_value;
        $.ajax({
            url: action + '/json',
            method: 'post',
            data: obj
        }).done(function(data) {
            if (typeof(data) === "object") {
                var result_obj = data;
            } else {
                var result_obj = $.parseJSON(data);
            }
            if (result_obj['type'] == 'score-update') {
                var field_id = result_obj['field_id'];
                var set_id = result_obj['set_id'];
                var game_id = result_obj['game_id'];
                var set_score = result_obj['set_score'];
                var set_number = result_obj['set_number'];

                $('#field_' + field_id + '_current_set_team_a').html(set_score[0]);
                $('#field_' + field_id + '_current_set_label').html('Satz ' + set_number);
                $('#field_' + field_id + '_current_set_team_b').html(set_score[1]);
                $('#field_' + field_id +'_set_' + set_number +'_team_a').html(set_score[0]);
                $('#field_' + field_id +'_set_' + set_number +'_team_b').html(set_score[1]);
                $('#score_game_' + game_id).html(result_obj['game_score']);
                if (result_obj['set_finished']) {
                    $('#field_' + field_id + '_next_set').removeClass('hidden');
                } else {
                    $('#field_' + field_id + '_next_set').addClass('hidden');
                }
            } else if (result_obj['type'] == 'clear-field') {
                var field_id = result_obj['field_id'];
                var game_name = result_obj['game_name'];
                var game_id = result_obj['game_id'];

                var selector_form = 'form[name="field_' + field_id + '"]';
                $(selector_form).find('div.player').html('');
                $(selector_form).find('div.setscore').html('');
                $('#field' + field_id + '_current_set_label').html('');
                $('#field_' + field_id + '_next_set').addClass('hidden');

                // change the link and style of the field in the name
                // TODO: reset the link properly
                $('#row_' + game_id).find('a.fieldname.active').attr('href', '#TODO');
                $('#row_' + game_id).find('.fieldname').removeClass('active');
            } else if (result_obj['type'] == 'update-current-set') {
                var field_id = result_obj['field_id'];
                var selector_form = 'form[name="field_' + field_id + '"]';
                var set_score = result_obj['set_score'];
                var set_number = result_obj['set_number'];

                $('#field_' + field_id + '_current_set_team_a').html(set_score[0]);
                $('#field_' + field_id + '_current_set_team_b').html(set_score[1]);
                $('#field_' + field_id + '_current_set_label').html('Satz ' + set_number);
                $('#field_' + field_id + '_next_set').addClass('hidden');
            } else {
                console.log('Unknown content type: ' +  data)
            }
        })
    });


    function update_score_for_fields_without_token() {
        if (TICKER_UPDATE_URL === undefined) {
            console.log('Update does not work if the update url is not defined');
            return
        }

        var elements = $('input[name^="has_token_"]');
        var fields_with_token = [];
        $(elements).each(function(i, item) {
            if (item.value == 'True') {
                var tmp_name = item.name;
                var field_id = tmp_name.substr(tmp_name.indexOf('has_token_') + 'has_token_'.length);
                fields_with_token.push(field_id)
            }
        });
        $.ajax({
            url: TICKER_UPDATE_URL,
            method: 'get'
        }).done(function (data) {
            if (typeof(data) === "object") {
                var obj = data;
            } else {
                var obj = $.parseJSON(data);
            }
            // if games is empty we return it
            if (('games' in obj) === false) {
                console.log('Games field has to be in the objs')
                return
            }
            $(obj['games']).each(function (i, item) {
                if (('field' in item) === false) {
                    console.log('Key: "field" is missing in item: ' + item)
                }
                else if (item['field'] !== -1) {
                    var elements = $('input[name="has_token_' + item['field'] + '"]');
                    var result_string = '';
                    $(item['sets']).each(function(j, set_item) {
                        // update the fields
                        $('#field_' + item['field'] + '_set_' + set_item[1] + '_team_a').html(set_item[2][0]);
                        $('#field_' + item['field'] + '_set_' + set_item[1] + '_team_b').html(set_item[2][1]);

                        // create the result string
                        result_string += set_item[2][0] + ':' + set_item[2][1] + ' ';
                    });
                    // write string to field
                    $('#score_game_' + item['id']).html(result_string);
                    // update the current set
                    var current_set = item['current_set'];
                    $('#field_' + item['field'] + '_current_set_team_a').html(item['sets'][current_set-1][2][0]);
                    $('#field_' + item['field'] + '_current_set_team_b').html(item['sets'][current_set-1][2][1]);
                }
            });
        });
    }

    setInterval(update_score_for_fields_without_token, 5000);

});