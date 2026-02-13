// Academic Research Website JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle Functionality
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    // Load saved theme or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }

    // Mobile Navigation Toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.getElementById('navbar');

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            navbar.classList.toggle('mobile-open');
        });
    }

    // Smooth Scrolling for Navigation Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                navbar.classList.remove('mobile-open');
            }
        });
    });

    // Active Navigation Link Highlighting
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('#navbar a[href^="#"]');

    function updateActiveNavLink() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', updateActiveNavLink);
    updateActiveNavLink(); // Initial call

    // Back to Top Button
    const backToTop = document.getElementById('back-to-top');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });

    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Copy Citation Function
    const copyButtons = document.querySelectorAll('.copy-citation');
    copyButtons.forEach(button => {
        button.addEventListener('click', copyCitation);
    });

    console.log('🎓 Academic Research Website Loaded Successfully!');
});

// Copy Citation Function
function copyCitation() {
    const citationText = `@article{patel2024synergistic,
  title={Synergistic Self-Correction: A Hierarchical Framework for Multi-Stage Reasoning and Error Recovery in Large Language Models},
  author={Patel, Pratham and Jindal, Abhishek},
  journal={arXiv preprint arXiv:2409.12345},
  year={2024},
  institution={Dhirubhai Ambani Institute of Information and Communication Technology}
}`;

    navigator.clipboard.writeText(citationText).then(() => {
        const button = document.querySelector('.copy-citation');
        const originalText = button.textContent;
        button.textContent = '✅ Copied!';
        button.classList.add('copied');

        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(() => {
        // Fallback for browsers that don't support clipboard API
        const textArea = document.createElement('textarea');
        textArea.value = citationText;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            const button = document.querySelector('.copy-citation');
            const originalText = button.textContent;
            button.textContent = '✅ Copied!';
            button.classList.add('copied');

            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('copied');
            }, 2000);
        } catch (err) {
            console.error('Failed to copy citation:', err);
        }

        document.body.removeChild(textArea);
    });
}

// Intersection Observer for Fade-in Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-up');
            fadeObserver.unobserve(entry.target); // Only animate once
        }
    });
}, observerOptions);

// Observe elements for fade-in animation
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        document.querySelectorAll('.paper-section, .results-table, .figure, .citation-box, .author').forEach(el => {
            fadeObserver.observe(el);
        });
    }, 100);
});

// Print Optimization
window.addEventListener('beforeprint', () => {
    // Expand all collapsible sections for printing
    document.querySelectorAll('details').forEach(details => {
        details.open = true;
    });
});

// Performance and Error Monitoring
window.addEventListener('load', () => {
    const loadTime = performance.now();
    console.log(`📊 Page loaded in ${Math.round(loadTime)}ms`);

    // Monitor image loading errors
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', (e) => {
            console.warn(`📷 Failed to load image: ${e.target.src}`);
            // Replace with placeholder
            e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzZiNzI4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkZpZ3VyZSBOb3QgQXZhaWxhYmxlPC90ZXh0Pjwvc3ZnPg==';
            e.target.alt = 'Figure not available';
        });
    });
});