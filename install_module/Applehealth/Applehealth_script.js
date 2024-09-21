document.addEventListener('DOMContentLoaded', function() {
            var link = document.getElementById('Applehealth-link');
            var currentIp = window.location.hostname;  // Get the current IP address
            var newPort = '3000';  // New port number
            
            link.addEventListener('click', function(event) {
                event.preventDefault();
                var newUrl = 'http://' + currentIp + ':' + newPort;
                window.open(newUrl, '_blank');
            });
        });

