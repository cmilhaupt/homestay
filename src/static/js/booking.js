function showBookingModal() {
    document.getElementById('bookingModal').classList.remove('hidden');
    document.getElementById('bookingError').classList.add('hidden');
}

function hideBookingModal() {
    document.getElementById('bookingModal').classList.add('hidden');
    document.getElementById('bookingError').classList.add('hidden');
    // Reset form
    document.getElementById('bookingForm').reset();
}

function initializeBookingForm() {
    document.getElementById('bookingForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading spinner and disable submit button
        const submitButton = this.querySelector('button[type="submit"]');
        const buttonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<div class="spinner"></div>';
        
        const formData = {
            guest_name: document.getElementById('guestName').value,
            guest_email: document.getElementById('guestEmail').value,
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value
        };

        try {
            const response = await fetch('/api/bookings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                hideBookingModal();
                window.location.reload();
            } else {
                const data = await response.json();
                const errorDiv = document.getElementById('bookingError');
                errorDiv.textContent = data.error || 'Booking failed. Please try again.';
                errorDiv.classList.remove('hidden');
                
                // Reset button on error
                submitButton.disabled = false;
                submitButton.innerHTML = buttonText;
                return; // Don't hide modal or reload on error
            }
        } catch (error) {
            // Reset button on error
            submitButton.disabled = false;
            submitButton.innerHTML = buttonText;
            alert('An error occurred. Please try again.');
        }
    });
}
