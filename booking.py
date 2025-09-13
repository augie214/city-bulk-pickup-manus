from flask import Blueprint, request, jsonify
from src.models.booking import db, ServiceRequest, ServiceQuote, Booking, Payment
from datetime import datetime, date, timedelta
import json
import random
import string

booking_bp = Blueprint('booking', __name__)

def generate_booking_reference():
    """Generate a unique booking reference"""
    year = datetime.now().year
    random_part = ''.join(random.choices(string.digits, k=6))
    return f'BK-{year}-{random_part}'

@booking_bp.route('/bookings/requests', methods=['POST'])
def create_service_request():
    """Create a new service request"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_JSON',
                    'message': 'Request body must be valid JSON'
                }
            }), 400
        
        required_fields = ['addressId', 'serviceCategory', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Field {field} is required'
                    }
                }), 400
        
        # Mock user ID - in real implementation, get from JWT token
        customer_user_id = 'user_123'
        
        # Parse dates and times
        preferred_date = None
        if data.get('preferredDate'):
            preferred_date = datetime.strptime(data['preferredDate'], '%Y-%m-%d').date()
        
        preferred_time_start = None
        if data.get('preferredTimeStart'):
            preferred_time_start = datetime.strptime(data['preferredTimeStart'], '%H:%M').time()
        
        preferred_time_end = None
        if data.get('preferredTimeEnd'):
            preferred_time_end = datetime.strptime(data['preferredTimeEnd'], '%H:%M').time()
        
        # Set expiration date (7 days from now)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        service_request = ServiceRequest(
            customer_user_id=customer_user_id,
            customer_address_id=data['addressId'],
            service_category=data['serviceCategory'],
            service_description=data['description'],
            preferred_date=preferred_date,
            preferred_time_start=preferred_time_start,
            preferred_time_end=preferred_time_end,
            urgency_level=data.get('urgencyLevel', 'normal'),
            estimated_budget=data.get('estimatedBudget'),
            special_instructions=data.get('specialInstructions'),
            photos=data.get('photos', []),
            expires_at=expires_at
        )
        
        db.session.add(service_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'request': service_request.to_dict()
            },
            'message': 'Service request created successfully',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_DATE_FORMAT',
                'message': 'Date must be in YYYY-MM-DD format, time in HH:MM format'
            }
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@booking_bp.route('/bookings/requests/<request_id>/quotes', methods=['GET'])
def get_request_quotes(request_id):
    """Get quotes for a service request"""
    try:
        # Mock data for demonstration
        mock_quotes = [
            {
                'id': 'quote_123',
                'businessId': 'business_456',
                'businessName': 'Green Cleanup Services',
                'amount': 175.00,
                'details': 'Removal of 3 furniture items and 2 appliances. Includes disposal fees.',
                'estimatedDuration': 2.5,
                'materialsIncluded': True,
                'disposalIncluded': True,
                'additionalFees': {
                    'disposal_fee': 25.00,
                    'fuel_surcharge': 10.00
                },
                'validUntil': (datetime.utcnow() + timedelta(days=3)).isoformat() + 'Z',
                'status': 'pending',
                'termsAndConditions': 'Standard terms apply. Payment due upon completion.',
                'createdAt': datetime.utcnow().isoformat() + 'Z'
            },
            {
                'id': 'quote_124',
                'businessId': 'business_457',
                'businessName': 'Rapid Trash Solutions',
                'amount': 195.00,
                'details': 'Complete furniture and appliance removal with same-day service.',
                'estimatedDuration': 2.0,
                'materialsIncluded': True,
                'disposalIncluded': True,
                'additionalFees': {
                    'same_day_fee': 30.00
                },
                'validUntil': (datetime.utcnow() + timedelta(days=2)).isoformat() + 'Z',
                'status': 'pending',
                'termsAndConditions': 'Same-day service available. Payment required upfront.',
                'createdAt': datetime.utcnow().isoformat() + 'Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'quotes': mock_quotes
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@booking_bp.route('/bookings/quotes/<quote_id>/accept', methods=['POST'])
def accept_quote(quote_id):
    """Accept a quote and create a booking"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_JSON',
                    'message': 'Request body must be valid JSON'
                }
            }), 400
        
        required_fields = ['scheduledDate', 'scheduledTimeStart']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Field {field} is required'
                    }
                }), 400
        
        # Mock user ID - in real implementation, get from JWT token
        customer_user_id = 'user_123'
        
        # Parse dates and times
        scheduled_date = datetime.strptime(data['scheduledDate'], '%Y-%m-%d').date()
        scheduled_time_start = datetime.strptime(data['scheduledTimeStart'], '%H:%M').time()
        scheduled_time_end = None
        if data.get('scheduledTimeEnd'):
            scheduled_time_end = datetime.strptime(data['scheduledTimeEnd'], '%H:%M').time()
        
        # Generate booking reference
        booking_reference = generate_booking_reference()
        
        # Mock quote data - in real implementation, fetch from database
        mock_quote = {
            'id': quote_id,
            'request_id': 'request_123',
            'business_id': 'business_456',
            'quote_amount': 175.00
        }
        
        booking = Booking(
            request_id=mock_quote['request_id'],
            quote_id=quote_id,
            customer_user_id=customer_user_id,
            business_id=mock_quote['business_id'],
            booking_reference=booking_reference,
            scheduled_date=scheduled_date,
            scheduled_time_start=scheduled_time_start,
            scheduled_time_end=scheduled_time_end,
            final_amount=mock_quote['quote_amount']
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'booking': booking.to_dict()
            },
            'message': 'Quote accepted and booking created successfully',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_DATE_FORMAT',
                'message': 'Date must be in YYYY-MM-DD format, time in HH:MM format'
            }
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@booking_bp.route('/bookings/history', methods=['GET'])
def get_booking_history():
    """Get user's booking history"""
    try:
        # Mock user ID - in real implementation, get from JWT token
        customer_user_id = 'user_123'
        
        status = request.args.get('status')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Mock data for demonstration
        mock_bookings = [
            {
                'id': 'booking_123',
                'reference': 'BK-2025-001234',
                'businessName': 'Green Cleanup Services',
                'serviceDescription': 'Furniture removal',
                'scheduledDate': '2025-10-20',
                'scheduledTimeStart': '10:00',
                'status': 'completed',
                'finalAmount': 175.00,
                'rating': 5,
                'createdAt': '2025-09-15T10:00:00Z',
                'completedAt': '2025-10-20T12:30:00Z'
            },
            {
                'id': 'booking_124',
                'reference': 'BK-2025-001235',
                'businessName': 'Rapid Trash Solutions',
                'serviceDescription': 'Appliance pickup',
                'scheduledDate': '2025-11-05',
                'scheduledTimeStart': '14:00',
                'status': 'confirmed',
                'finalAmount': 125.00,
                'rating': None,
                'createdAt': '2025-09-20T15:30:00Z',
                'completedAt': None
            }
        ]
        
        # Apply status filter
        if status:
            mock_bookings = [b for b in mock_bookings if b['status'] == status]
        
        # Apply pagination
        paginated_bookings = mock_bookings[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'data': {
                'bookings': paginated_bookings,
                'totalCount': len(mock_bookings),
                'limit': limit,
                'offset': offset
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@booking_bp.route('/bookings/<booking_id>', methods=['GET'])
def get_booking_details(booking_id):
    """Get detailed booking information"""
    try:
        # Mock data for demonstration
        mock_booking = {
            'id': booking_id,
            'reference': 'BK-2025-001234',
            'requestId': 'request_123',
            'quoteId': 'quote_123',
            'customerUserId': 'user_123',
            'businessId': 'business_456',
            'businessName': 'Green Cleanup Services',
            'businessPhone': '+1234567890',
            'serviceDescription': 'Removal of 3 furniture items and 2 appliances',
            'scheduledDate': '2025-10-20',
            'scheduledTimeStart': '10:00',
            'scheduledTimeEnd': '12:00',
            'actualStartTime': '2025-10-20T10:15:00Z',
            'actualEndTime': '2025-10-20T12:30:00Z',
            'finalAmount': 175.00,
            'paymentStatus': 'paid',
            'bookingStatus': 'completed',
            'completionNotes': 'All items removed successfully. Customer satisfied.',
            'beforePhotos': ['https://example.com/before1.jpg', 'https://example.com/before2.jpg'],
            'afterPhotos': ['https://example.com/after1.jpg', 'https://example.com/after2.jpg'],
            'createdAt': '2025-09-15T10:00:00Z',
            'completedAt': '2025-10-20T12:30:00Z'
        }
        
        return jsonify({
            'success': True,
            'data': {
                'booking': mock_booking
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@booking_bp.route('/bookings/<booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        data = request.get_json()
        
        # Mock user ID - in real implementation, get from JWT token
        customer_user_id = 'user_123'
        
        booking = Booking.query.filter_by(
            id=booking_id,
            customer_user_id=customer_user_id
        ).first()
        
        if not booking:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BOOKING_NOT_FOUND',
                    'message': 'Booking not found'
                }
            }), 404
        
        if booking.booking_status in ['completed', 'cancelled']:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BOOKING_CANNOT_BE_CANCELLED',
                    'message': f'Booking with status {booking.booking_status} cannot be cancelled'
                }
            }), 400
        
        booking.booking_status = 'cancelled'
        booking.cancellation_reason = data.get('reason', 'Customer requested cancellation')
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'booking': booking.to_dict()
            },
            'message': 'Booking cancelled successfully',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@booking_bp.route('/bookings/<booking_id>/complete', methods=['POST'])
def complete_booking(booking_id):
    """Mark a booking as completed (business users only)"""
    try:
        data = request.get_json()
        
        # Mock business user ID - in real implementation, get from JWT token and verify business ownership
        business_user_id = 'business_user_123'
        
        booking = Booking.query.filter_by(id=booking_id).first()
        
        if not booking:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BOOKING_NOT_FOUND',
                    'message': 'Booking not found'
                }
            }), 404
        
        if booking.booking_status != 'in_progress':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BOOKING_NOT_IN_PROGRESS',
                    'message': 'Only bookings in progress can be completed'
                }
            }), 400
        
        booking.booking_status = 'completed'
        booking.actual_end_time = datetime.utcnow()
        booking.completed_at = datetime.utcnow()
        booking.completion_notes = data.get('completionNotes')
        booking.after_photos = data.get('afterPhotos', [])
        booking.customer_signature = data.get('customerSignature')
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'booking': booking.to_dict()
            },
            'message': 'Booking completed successfully',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

