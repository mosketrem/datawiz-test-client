$(document).ready(
        $.ajax({
            type: 'GET',
            async: true,
            url: '/api/changes/',
            // data: "param1=value1&param2=value2;",
            success: function(data) {
                $(".load-changes").hide();
                $("#increase-table").html($(data).find('#increase-table'));
                $("#main-table").html($(data).find('#main-table'));
                $("#drop-table").html($(data).find('#drop-table'));
            },
            // dataType: 'json',
        })
    )
