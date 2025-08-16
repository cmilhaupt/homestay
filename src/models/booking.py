from datetime import datetime, UTC
from ..database import db

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    def __repr__(self):
        return f'<Booking {self.guest_name} {self.start_date} to {self.end_date}>'
