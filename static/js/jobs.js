/**
 * Jobs.js - JavaScript for job listings and details
 */

document.addEventListener('DOMContentLoaded', function() {
    // Job filters
    const filterForm = document.getElementById('job-filter-form');
    const searchForm = document.getElementById('search-form');
    const resetFilterButton = document.getElementById('reset-filters');
    
    if (filterForm) {
        filterForm.addEventListener('change', function() {
            this.submit();
        });
    }
    
    if (resetFilterButton) {
        resetFilterButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Reset all form fields
            filterForm.querySelectorAll('input, select').forEach(field => {
                if (field.type === 'checkbox' || field.type === 'radio') {
                    field.checked = false;
                } else {
                    field.value = '';
                }
            });
            
            // Submit the form to refresh the results
            filterForm.submit();
        });
    }
    
    // Job card animations
    const jobCards = document.querySelectorAll('.job-card');
    
    jobCards.forEach((card, index) => {
        // Add a slight delay to each card for a cascading effect
        card.style.opacity = 0;
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = 1;
            card.style.transform = 'translateY(0)';
        }, 100 * index);
        
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.1)';
            this.style.borderLeftColor = 'var(--primary-color)';
            this.style.borderLeftWidth = '5px';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.05)';
            this.style.borderLeftColor = 'transparent';
        });
    });
    
    // Job detail page - Sticky sidebar
    const jobSidebar = document.querySelector('.job-detail-sidebar');
    
    if (jobSidebar) {
        const initialTopOffset = jobSidebar.getBoundingClientRect().top + window.scrollY;
        
        window.addEventListener('scroll', function() {
            if (window.innerWidth >= 992) { // Only on desktop
                const scrollPosition = window.scrollY;
                
                if (scrollPosition > initialTopOffset - 100) {
                    jobSidebar.style.position = 'sticky';
                    jobSidebar.style.top = '100px';
                } else {
                    jobSidebar.style.position = 'static';
                }
            }
        });
    }
    
    // Application form validation
    const applicationForm = document.getElementById('application-form');
    
    if (applicationForm) {
        applicationForm.addEventListener('submit', function(e) {
            const coverLetter = document.getElementById('cover_letter');
            
            if (coverLetter && coverLetter.value.trim().length < 50) {
                e.preventDefault();
                alert('Please provide a more detailed cover letter (at least 50 characters).');
                return false;
            }
        });
    }
    
    // Salary range slider
    const salaryMinInput = document.getElementById('salary_min');
    const salaryMaxInput = document.getElementById('salary_max');
    const salaryRangeDisplay = document.getElementById('salary-range-display');
    
    if (salaryMinInput && salaryMaxInput && salaryRangeDisplay) {
        function updateSalaryDisplay() {
            const min = salaryMinInput.value || '0';
            const max = salaryMaxInput.value || '∞';
            salaryRangeDisplay.textContent = `$${min} - $${max}`;
        }
        
        salaryMinInput.addEventListener('input', updateSalaryDisplay);
        salaryMaxInput.addEventListener('input', updateSalaryDisplay);
        
        // Initial display
        updateSalaryDisplay();
    }
    
    // Job search form animation
    const searchFormInputs = document.querySelectorAll('#search-form .form-control, #search-form .btn');
    
    searchFormInputs.forEach((input, index) => {
        input.style.transition = 'all 0.3s ease';
        
        // Focus effect
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.03)';
            this.style.boxShadow = '0 0 0 0.25rem rgba(78, 115, 223, 0.25)';
        });
        
        input.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        });
    });
    
    // Animate job descriptions in detail view
    const jobDescription = document.querySelector('.job-description');
    
    if (jobDescription) {
        // Split text into elements for staggered animation
        const paragraphs = jobDescription.querySelectorAll('p, ul, h3');
        
        paragraphs.forEach((element, index) => {
            element.style.opacity = 0;
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.5s ease';
                element.style.opacity = 1;
                element.style.transform = 'translateY(0)';
            }, 100 * (index + 1));
        });
    }
});
