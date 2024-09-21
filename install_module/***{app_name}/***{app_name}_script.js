document.addEventListener('DOMContentLoaded', function() {
            var link = document.getElementById('***{app_name}-link');
            var currentIp = window.location.hostname;  // Get the current IP address
            var newPort = '***';  // New port number
            
            link.addEventListener('click', function(event) {
                event.preventDefault();
                var newUrl = 'http://' + currentIp + ':' + newPort;
                window.open(newUrl, '_blank');
            });
        });

