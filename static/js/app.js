// static/app.js
// Live animated background with bouncing points
// Remove the bouncing balls/canvas background code

function showLinks(link1, link2) {
  const linksDiv = document.getElementById('links');
  if (linksDiv) {
    let linksHTML = '<div class="external-links">';
    if (link1 && link1 !== 'null') {
      linksHTML += `<a href="${link1}" target="_blank" class="external-link">IMDB</a>`;
    }
    if (link2 && link2 !== 'null') {
      linksHTML += `<a href="${link2}" target="_blank" class="external-link">TMDB</a>`;
    }
    linksHTML += '</div>';
    linksDiv.innerHTML = linksHTML;
  }
}

// Add click functionality to sample ID items
document.addEventListener('DOMContentLoaded', function() {
    // Make sample ID items clickable
    const idItems = document.querySelectorAll('.id-item');
    idItems.forEach(item => {
        item.addEventListener('click', function() {
            const userId = this.textContent;
            const input = document.querySelector('input[name="user_id"]');
            if (input) {
                input.value = userId;
            }
        });
    });

    // Add smooth scrolling for better UX
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states for other forms
    const forms = document.querySelectorAll('form:not(#userForm)');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Loading...';
                submitBtn.disabled = true;
            }
        });
    });

    // Add hover effects for movie cards
    const movieCards = document.querySelectorAll('.movie-card');
    movieCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});
