let deleteBookingId = null;

function confirmDelete(bookingId, guestName) {
    deleteBookingId = bookingId;
    document.getElementById('deleteConfirmText').textContent = 
        `Are you sure you want to delete the booking for ${guestName}?`;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function hideDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    deleteBookingId = null;
}

async function updateWelcomeTemplate() {
    const template = document.getElementById('welcomeTemplate').value;
    
    if (!template) {
        document.getElementById('welcomeTemplateError').classList.remove('hidden');
        document.getElementById('welcomeTemplateSuccess').classList.add('hidden');
        return;
    }
    
    document.getElementById('welcomeTemplateError').classList.add('hidden');
    
    try {
        const response = await fetch('/admin/welcome-template', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ template }),
        });

        if (response.ok) {
            document.getElementById('welcomeTemplateSuccess').classList.remove('hidden');
            setTimeout(() => {
                document.getElementById('welcomeTemplateSuccess').classList.add('hidden');
            }, 3000);
        } else {
            const data = await response.json();
            document.getElementById('welcomeTemplateError').textContent = data.error || 'Failed to update template';
            document.getElementById('welcomeTemplateError').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error updating welcome template:', error);
        document.getElementById('welcomeTemplateError').textContent = 'An error occurred';
        document.getElementById('welcomeTemplateError').classList.remove('hidden');
    }
}

async function executeDelete() {
    if (!deleteBookingId) return;
    
    try {
        const response = await fetch(`/api/bookings/${deleteBookingId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            alert(data.error || 'Deletion failed. Please try again.');
        }
    } catch (error) {
        alert('An error occurred. Please try again.');
    }
    
    hideDeleteModal();
}

async function updateAccessCode() {
    const newCode = document.getElementById('newCode').value;
    
    if (!newCode) {
        document.getElementById('accessCodeError').classList.remove('hidden');
        return;
    }
    document.getElementById('accessCodeError').classList.add('hidden');
    
    try {
        const response = await fetch('/api/access-code', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: newCode })
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            alert(data.error || 'Failed to update access code. Please try again.');
        }
    } catch (error) {
        alert('An error occurred. Please try again.');
    }
}
