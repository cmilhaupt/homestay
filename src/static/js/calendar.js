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
            eventColor: '#EF4444',
            eventContent: function(arg) {
                return {
                    html: `
                        <div class="p-2">
                            <div class="font-semibold">${arg.event.extendedProps.guest_name || 'Booked'}</div>
                            <div class="text-xs">${arg.event.extendedProps.guest_email || ''}</div>
                        </div>
                    `
                };
            },
            eventDidMount: function(info) {
                // Add tooltip showing booking details
                const startDate = info.event.start.toLocaleDateString();
                const endDate = info.event.end.toLocaleDateString();
                const guestName = info.event.extendedProps.guest_name || 'Guest';
                info.el.title = `${guestName}: ${startDate} to ${endDate}`;
            }
        });
    } else {
        initializeCalendar('calendar');
    }
});
