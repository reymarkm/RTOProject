$(document).ready(function () {
    var allOptions = $('#selectCity option')
    $('#selectProv').change(function () {
        $('#selectCity option').remove()
        var classN = $('#selectProv option:selected').prop('class');
        var opts = allOptions.filter('.' + classN);
        $.each(opts, function (i, j) {
            $(j).appendTo('#selectCity');
        });
    });
});