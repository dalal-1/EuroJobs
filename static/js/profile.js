/**
 * Profile.js - JavaScript for user profile pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Profile image upload preview
    const profilePictureInput = document.getElementById('profile_picture');
    
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', function() {
            previewImage(this, 'profile-picture-preview');
        });
    }
    
    // Company logo upload preview
    const logoInput = document.getElementById('logo');
    
    if (logoInput) {
        logoInput.addEventListener('change', function() {
            previewImage(this, 'logo-preview');
        });
    }
    
    // CV file name display
    const cvFileInput = document.getElementById('cv_file');
    
    if (cvFileInput) {
        cvFileInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'No file chosen';
            const fileNameDisplay = document.createElement('div');
            fileNameDisplay.className = 'selected-file-name mt-2';
            fileNameDisplay.innerHTML = `<i class="fas fa-file-pdf me-2"></i>${fileName}`;
            
            // Remove any existing file name display
            const existingDisplay = this.parentElement.querySelector('.selected-file-name');
            if (existingDisplay) {
                existingDisplay.remove();
            }
            
            this.parentElement.appendChild(fileNameDisplay);
        });
    }
    
    // Skill level slider interactivity
    const skillLevelInput = document.getElementById('level');
    const skillLevelValue = document.getElementById('skill-level-value');
    
    if (skillLevelInput && skillLevelValue) {
        skillLevelInput.addEventListener('input', function() {
            skillLevelValue.textContent = this.value;
            
            // Update color based on level
            const levelPercentage = (this.value / 5) * 100;
            let color;
            
            if (levelPercentage <= 20) {
                color = '#e74a3b'; // Red for level 1
            } else if (levelPercentage <= 40) {
                color = '#f6c23e'; // Yellow for level 2
            } else if (levelPercentage <= 60) {
                color = '#4e73df'; // Blue for level 3
            } else if (levelPercentage <= 80) {
                color = '#36b9cc'; // Cyan for level 4
            } else {
                color = '#1cc88a'; // Green for level 5
            }
            
            skillLevelInput.style.accentColor = color;
        });
        
        // Set initial value
        skillLevelValue.textContent = skillLevelInput.value;
    }
    
    // Application status filter
    const filterButtons = document.querySelectorAll('.filter-btn');
    const applicationRows = document.querySelectorAll('.application-table tbody tr');
    
    if (filterButtons.length > 0 && applicationRows.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filter = this.getAttribute('data-filter');
                
                // Toggle active class on buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Filter table rows
                applicationRows.forEach(row => {
                    const status = row.getAttribute('data-status');
                    
                    if (filter === 'all' || status === filter) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // Company job listing interactions
    const jobCards = document.querySelectorAll('.job-card');
    
    jobCards.forEach(card => {
        // Add subtle hover animation
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.05)';
        });
    });
    
    // Skills animation
    const skillCards = document.querySelectorAll('.skill-card');
    
    skillCards.forEach((card, index) => {
        card.style.opacity = 0;
        card.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = 1;
            card.style.transform = 'translateX(0)';
        }, 100 * index);
    });
    
    // Profile sections animation
    const profileSections = document.querySelectorAll('.profile-section');
    
    profileSections.forEach((section, index) => {
        section.style.opacity = 0;
        section.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            section.style.transition = 'all 0.5s ease';
            section.style.opacity = 1;
            section.style.transform = 'translateY(0)';
        }, 200 * (index + 1));
    });
    
    // Job post form validations
    const jobPostForm = document.querySelector('form[action*="job"]');
    
    if (jobPostForm) {
        jobPostForm.addEventListener('submit', function(e) {
            const title = document.getElementById('title');
            const description = document.getElementById('description');
            const salaryMin = document.getElementById('salary_min');
            const salaryMax = document.getElementById('salary_max');
            
            if (salaryMin && salaryMax && salaryMin.value && salaryMax.value) {
                if (parseFloat(salaryMin.value) > parseFloat(salaryMax.value)) {
                    e.preventDefault();
                    alert('Minimum salary cannot be greater than maximum salary');
                    return false;
                }
            }
        });
    }
});

/**
 * Preview an image before upload
 * @param {HTMLInputElement} input - The file input element
 * @param {string} previewId - The ID of the preview container (optional)
 */
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            // Create preview element if it doesn't exist
            let previewContainer = document.getElementById(previewId);
            
            if (!previewContainer) {
                previewContainer = document.createElement('div');
                previewContainer.id = previewId;
                previewContainer.className = 'image-preview mt-3';
                previewContainer.innerHTML = `
                    <img src="${e.target.result}" class="img-fluid img-thumbnail" alt="Preview">
                    <p class="text-center mt-2">Preview</p>
                `;
                
                // Insert after the file input
                input.parentNode.insertBefore(previewContainer, input.nextSibling);
            } else {
                // Update existing preview
                const previewImage = previewContainer.querySelector('img');
                previewImage.src = e.target.result;
            }
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}
