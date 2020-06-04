$(document).ready(function () {
    var allOptions = $('#selectCity option')
    $('#selectProvince').change(function () {
        $('#selectCity option').remove()
        var classN = $('#selectProvince option:selected').prop('class');
        var opts = allOptions.filter('.' + classN);
        $.each(opts, function (i, j) {
            $(j).appendTo('#selectCity');
        });
    });
});