document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const dateElement = document.getElementById('currentDate');

    // Set real date
    if (dateElement) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = new Date().toLocaleDateString('en-US', options);
    }
    
    // Sidebar toggle logic
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                // Mobile behavior: show/hide
                sidebar.classList.toggle('open');
            } else {
                // Desktop behavior: collapse
                sidebar.classList.toggle('collapsed');
            }
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && 
            sidebar.classList.contains('open') && 
            !sidebar.contains(e.target) && 
            !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });

    // Handle initial state for large screens
    // No explicit change needed as CSS handles default.
});
