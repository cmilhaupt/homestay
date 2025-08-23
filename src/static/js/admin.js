let deleteBookingId = null;
let deleteBlockedId = null;

function confirmDelete(bookingId, guestName) {
    deleteBookingId = bookingId;
    deleteBlockedId = null;
    document.getElementById('deleteConfirmText').textContent = 
        `Are you sure you want to delete the booking for ${guestName}?`;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function confirmDeleteBlocked(blockedId, reason) {
    deleteBlockedId = blockedId;
    deleteBookingId = null;
    document.getElementById('deleteConfirmText').textContent = 
        `Are you sure you want to delete the blocked period: ${reason || 'Owner unavailable'}?`;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function hideDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    deleteBookingId = null;
    deleteBlockedId = null;
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
    if (!deleteBookingId && !deleteBlockedId) return;
    
    try {
        let response;
        if (deleteBookingId) {
            response = await fetch(`/api/bookings/${deleteBookingId}`, {
                method: 'DELETE',
            });
        } else if (deleteBlockedId) {
            response = await fetch(`/api/blocked-dates/${deleteBlockedId}`, {
                method: 'DELETE',
            });
        }

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

function showBlockModal() {
    document.getElementById('blockModal').classList.remove('hidden');
    document.getElementById('blockError').classList.add('hidden');
}

function hideBlockModal() {
    document.getElementById('blockModal').classList.add('hidden');
    document.getElementById('blockError').classList.add('hidden');
    // Reset form
    document.getElementById('blockForm').reset();
}

async function createBlockedDate() {
    const startDate = document.getElementById('blockStartDate').value;
    const endDate = document.getElementById('blockEndDate').value;
    const reason = document.getElementById('blockReason').value;
    
    if (!startDate || !endDate) {
        document.getElementById('blockError').textContent = 'Please select both start and end dates';
        document.getElementById('blockError').classList.remove('hidden');
        return;
    }
    
    if (endDate <= startDate) {
        document.getElementById('blockError').textContent = 'End date must be after start date';
        document.getElementById('blockError').classList.remove('hidden');
        return;
    }
    
    document.getElementById('blockError').classList.add('hidden');
    
    try {
        const response = await fetch('/api/blocked-dates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                start_date: startDate,
                end_date: endDate,
                reason: reason
            })
        });

        if (response.ok) {
            hideBlockModal();
            window.location.reload();
        } else {
            const data = await response.json();
            document.getElementById('blockError').textContent = data.error || 'Failed to block dates. Please try again.';
            document.getElementById('blockError').classList.remove('hidden');
        }
    } catch (error) {
        document.getElementById('blockError').textContent = 'An error occurred. Please try again.';
        document.getElementById('blockError').classList.remove('hidden');
    }
}
