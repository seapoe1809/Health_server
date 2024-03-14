document.addEventListener('DOMContentLoaded', function() {
    const appInfo = {
        App_name: 'Dock',  // Replace with the actual app name
        app_folder: 'Dock'       // Replace with the actual image folder
    };

    // Get the install link element"""WILL be in static folder, linking to install.html and subsequently to install_module"
    const installLink = document.getElementById('Dock-link');

    // Add a click event handler to the link
    installLink.addEventListener('click', function() {
        const installUrl = `/install?app_name_file=${appInfo.App_name}&app_folder=${appInfo.app_folder}`;
        window.open(installUrl, '_blank');
    });
});

