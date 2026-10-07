document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Logika Notifikasi Auto-Close (Hilang dalam 4 detik)
    let alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Cek apakah Bootstrap ada untuk menghindari error
            if (typeof bootstrap !== 'undefined') {
                let bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 4000);
    });

    // 2. Tambahkan class 'animate-up' ke elemen yang mau dianimasikan
    // Kita menargetkan kotak (card), judul besar, dan form
    const elementsToAnimate = document.querySelectorAll('.card, .display-4, .lead, table');
    
    elementsToAnimate.forEach((el, index) => {
        el.classList.add('animate-up');
        
        // Memberikan delay sedikit pada elemen agar munculnya berurutan (Staggered effect)
        el.style.transitionDelay = `${index * 0.1}s`;
    });

    // 3. Intersection Observer (Untuk mentrigger animasi saat elemen masuk ke layar)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1 // Animasi mulai saat 10% elemen terlihat
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Tambahkan class .visible untuk menjalankan animasi CSS
                entry.target.classList.add('visible');
                // Hentikan pantauan setelah animasi selesai agar tidak berulang terus
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Mulai memantau semua elemen yang sudah diberi class animate-up
    elementsToAnimate.forEach(el => observer.observe(el));

    // Logika Animasi Sliding Landing Page
    const signUpButton = document.getElementById('signUpBtn');
    const signInButton = document.getElementById('signInBtn');
    const containerSliding = document.getElementById('container-sliding');

    if (signUpButton && signInButton && containerSliding) {
        signUpButton.addEventListener('click', () => {
            containerSliding.classList.add("right-panel-active");
        });

        signInButton.addEventListener('click', () => {
            containerSliding.classList.remove("right-panel-active");
        });
    }
});