function updateEndDateMin(startDate) {
    const endDateInput = document.getElementById('endDate');
    
    if (startDate) {
        // Only update the minimum date constraint
        endDateInput.setAttribute('min', startDate);
        
        // Clear the end date if it's before the new start date
        if (endDateInput.value && endDateInput.value < startDate) {
            endDateInput.value = '';
        }
    }
}

function initializeCalendar(elementId, options = {}) {
    const calendarEl = document.getElementById(elementId);
    window.calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: '',
            center: '',
            right: ''
        },
        customButtons: {
            prevButton: {
                text: 'prev',
                click: function() {
                    calendar.prev();
                }
            },
            nextButton: {
                text: 'next',
                click: function() {
                    calendar.next();
                }
            }
        },
        titleFormat: { year: 'numeric', month: 'long' },
        events: '/api/bookings',
        eventDataTransform: function(event) {
            // Add data attributes and adjust end date
            event.allDay = true;
            event.display = 'block';
            event.start = new Date(event.start);
            event.end = new Date(new Date(event.end).getTime() + 24*60*60*1000);
            return event;
        },
        eventDisplay: 'block',
        eventColor: options.eventColor || '#3B82F6',
        eventContent: options.eventContent || function(arg) {
            return {
                html: '<div class="fc-content"><span>Booked</span></div>'
            };
        },
        eventDidMount: options.eventDidMount || function(info) {
            // Default event styling - no special handling needed for regular users
        },
        ...options
    });
    calendar.render();

    // Update title when the calendar view changes
    function updateTitle() {
        const title = calendar.view.title;
        document.getElementById('calendarTitle').textContent = title;
    }
    
    calendar.on('datesSet', updateTitle);
    updateTitle(); // Set initial title
}

document.addEventListener('DOMContentLoaded', function() {
    const calendarElement = document.getElementById('calendar') || document.getElementById('adminCalendar');
    if (!calendarElement) return;

    const isAdmin = document.getElementById('adminCalendar') !== null;
    
    initializeBookingForm();
    
    if (isAdmin) {
        initializeCalendar('adminCalendar', {
            eventContent: function(arg) {
                const isBlocked = arg.event.extendedProps.type === 'blocked';
                const isBooking = arg.event.extendedProps.type === 'booking';
                
                if (isBlocked) {
                    return {
                        html: `
                            <div class="p-2 bg-gray-500 text-white">
                                <div class="font-semibold">Blocked</div>
                                <div class="text-xs">${arg.event.extendedProps.reason || 'Owner unavailable'}</div>
                            </div>
                        `
                    };
                } else if (isBooking) {
                    return {
                        html: `
                            <div class="p-2 bg-red-500 text-white">
                                <div class="font-semibold">${arg.event.extendedProps.guest_name || 'Booked'}</div>
                                <div class="text-xs">${arg.event.extendedProps.guest_email || ''}</div>
                            </div>
                        `
                    };
                }
                
                return {
                    html: '<div class="p-2"><div class="font-semibold">Booked</div></div>'
                };
            },
            eventDidMount: function(info) {
                const isBlocked = info.event.extendedProps.type === 'blocked';
                const isBooking = info.event.extendedProps.type === 'booking';
                
                if (isBlocked) {
                    const startDate = info.event.start.toLocaleDateString();
                    const endDate = info.event.end.toLocaleDateString();
                    const reason = info.event.extendedProps.reason || 'Owner unavailable';
                    info.el.title = `Blocked: ${reason} (${startDate} to ${endDate})`;
                    info.el.style.backgroundColor = '#6B7280';
                    info.el.style.borderColor = '#6B7280';
                } else if (isBooking) {
                    const startDate = info.event.start.toLocaleDateString();
                    const endDate = info.event.end.toLocaleDateString();
                    const guestName = info.event.extendedProps.guest_name || 'Guest';
                    info.el.title = `${guestName}: ${startDate} to ${endDate}`;
                    info.el.style.backgroundColor = '#EF4444';
                    info.el.style.borderColor = '#EF4444';
                }
            }
        });
    } else {
        initializeCalendar('calendar');
    }
});
