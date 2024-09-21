document.addEventListener('DOMContentLoaded', function() {
            var link = document.getElementById('Dock-link');
            var currentIp = window.location.hostname;  // Get the current IP address
            var newPort = '3009';  // New port number
            
            link.addEventListener('click', function(event) {
                event.preventDefault();
                var newUrl = 'http://' + currentIp + ':' + newPort;
                window.open(newUrl, '_blank');
            });
        });

