document.addEventListener('DOMContentLoaded', function() {
    var button = document.getElementById('Robot-button');  // Make sure this ID matches the button's ID
    var currentIp = window.location.hostname;  // Get the current IP address
    var newPort = '3012';  // Specify the new port number
    
    button.addEventListener('click', function(event) {
        event.preventDefault();  // This line might not be necessary since it's a button, not a link, but it doesn't hurt to keep it
        var newUrl = 'http://' + currentIp + ':' + newPort;  // Construct the new URL with the specified port
        window.open(newUrl, '_blank');  // Open the new URL in a new tab/window
    });
});

