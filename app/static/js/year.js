// No one has time to update the year manually in 1023432 different HTML files
$(function (ready) {
    $(document).ready(function () {
        document.getElementById("riceapps").innerHTML = "A PROJECT OF RICE APPS, " + new Date().getFullYear();
    });
});