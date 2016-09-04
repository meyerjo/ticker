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
            var result_obj = $.parseJSON(data);
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
    })
})