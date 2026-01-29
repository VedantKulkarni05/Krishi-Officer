(() => {
    document.addEventListener('DOMContentLoaded', () => {
        const header = document.querySelector('.header');
        const hero = document.querySelector('.hero');
        const getStartedBtn = document.getElementById('getStartedBtn');

        // Get Started button click handler with ripple
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', (event) => {
                createRipple(getStartedBtn, event);
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 300);
            });
        }

        // Smooth scroll for internal links
        document.addEventListener('click', (e) => {
            const anchor = e.target.closest('a[href^="#"]');
            if (!anchor) return;

            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });

        // Header scroll shadow with requestAnimationFrame for performance
        let lastScroll = 0;
        const onScroll = () => {
            const currentScroll = window.pageYOffset;
            const shadow = currentScroll > 100 ? '0 4px 16px rgba(0,0,0,0.12)' : '0 2px 8px rgba(0,0,0,0.08)';
            header?.style.setProperty('box-shadow', shadow);
            lastScroll = currentScroll;
        };
        window.addEventListener('scroll', () => requestAnimationFrame(onScroll));

        // Ripple effect
        function createRipple(button, event) {
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = event.clientX - rect.left - size / 2;
            const y = event.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.className = 'ripple';
            button.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        }

        // Parallax effect with throttling
        let lastMove = 0;
        window.addEventListener('mousemove', (e) => {
            const now = Date.now();
            if (now - lastMove < 16) return; // ~60fps
            lastMove = now;

            if (hero) {
                const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
                const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
                hero.style.setProperty('--mouse-x', `${moveX}px`);
                hero.style.setProperty('--mouse-y', `${moveY}px`);
            }
        });

        // Intersection Observer for fade-in animations using CSS class
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
        );

        document.querySelectorAll('.feature-card').forEach((card) => observer.observe(card));

        // Add ripple and fade-in CSS
        const style = document.createElement('style');
        style.textContent = `
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple-animation 0.6s ease-out;
                pointer-events: none;
            }
            @keyframes ripple-animation {
                to { transform: scale(4); opacity: 0; }
            }

            .feature-card {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.6s ease, transform 0.6s ease;
            }
            .feature-card.fade-in {
                opacity: 1;
                transform: translateY(0);
            }
        `;
        document.head.appendChild(style);
    });
})();
