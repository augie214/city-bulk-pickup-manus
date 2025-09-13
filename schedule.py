from flask import Blueprint, request, jsonify
from src.models.schedule import db, PickupSchedule, ScheduleZone, PickupEvent, UserScheduleSubscription
from datetime import datetime, date
import json

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/schedules/lookup', methods=['GET'])
def lookup_schedules():
    """Look up pickup schedules for a specific address"""
    try:
        # Get query parameters
        address = request.args.get('address')
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        zip_code = request.args.get('zipCode')
        
        if not any([address, (lat and lng), zip_code]):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETERS',
                    'message': 'Address, coordinates, or ZIP code is required'
                }
            }), 400
        
        # Mock data for demonstration - in real implementation, this would query based on location
        mock_schedules = [
            {
                'id': 'schedule_123',
                'name': 'Springfield Bulk Pickup',
                'type': 'bulk',
                'frequency': 'monthly',
                'nextPickupDate': '2025-10-15',
                'zone': {
                    'id': 'zone_456',
                    'name': 'Zone A',
                    'pickupDay': 'tuesday'
                }
            },
            {
                'id': 'schedule_124',
                'name': 'Springfield Yard Waste',
                'type': 'yard_waste',
                'frequency': 'weekly',
                'nextPickupDate': '2025-10-18',
                'zone': {
                    'id': 'zone_456',
                    'name': 'Zone A',
                    'pickupDay': 'friday'
                }
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'schedules': mock_schedules
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

@schedule_bp.route('/schedules/<schedule_id>/events', methods=['GET'])
def get_schedule_events(schedule_id):
    """Get upcoming pickup events for a schedule"""
    try:
        # Get query parameters
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        limit = request.args.get('limit', 20, type=int)
        
        # Mock data for demonstration
        mock_events = [
            {
                'id': 'event_789',
                'date': '2025-10-15',
                'timeStart': '08:00',
                'timeEnd': '17:00',
                'status': 'scheduled',
                'zone': {
                    'id': 'zone_456',
                    'name': 'Zone A'
                }
            },
            {
                'id': 'event_790',
                'date': '2025-11-15',
                'timeStart': '08:00',
                'timeEnd': '17:00',
                'status': 'scheduled',
                'zone': {
                    'id': 'zone_456',
                    'name': 'Zone A'
                }
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'events': mock_events[:limit]
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

@schedule_bp.route('/schedules/subscriptions', methods=['POST'])
def create_subscription():
    """Subscribe to pickup schedule notifications"""
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
        
        required_fields = ['scheduleId', 'addressId']
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
        user_id = 'user_123'
        
        # Create subscription
        subscription = UserScheduleSubscription(
            user_id=user_id,
            address_id=data['addressId'],
            schedule_id=data['scheduleId'],
            notification_preferences=data.get('notificationPreferences', {
                'email': True,
                'push': True,
                'sms': False,
                'advance_days': [1, 7]
            })
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'subscription': subscription.to_dict()
            },
            'message': 'Subscription created successfully',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        }), 201
        
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

@schedule_bp.route('/schedules/subscriptions', methods=['GET'])
def get_user_subscriptions():
    """Get user's schedule subscriptions"""
    try:
        # Mock user ID - in real implementation, get from JWT token
        user_id = 'user_123'
        
        subscriptions = UserScheduleSubscription.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'success': True,
            'data': {
                'subscriptions': [sub.to_dict() for sub in subscriptions]
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

@schedule_bp.route('/schedules/subscriptions/<subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    """Delete a schedule subscription"""
    try:
        # Mock user ID - in real implementation, get from JWT token
        user_id = 'user_123'
        
        subscription = UserScheduleSubscription.query.filter_by(
            id=subscription_id,
            user_id=user_id
        ).first()
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SUBSCRIPTION_NOT_FOUND',
                    'message': 'Subscription not found'
                }
            }), 404
        
        db.session.delete(subscription)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscription deleted successfully',
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

@schedule_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """Get all pickup schedules"""
    try:
        schedules = PickupSchedule.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'data': {
                'schedules': [schedule.to_dict() for schedule in schedules]
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

@schedule_bp.route('/schedules', methods=['POST'])
def create_schedule():
    """Create a new pickup schedule (admin only)"""
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
        
        required_fields = ['municipality_id', 'schedule_name', 'schedule_type', 'frequency', 'start_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Field {field} is required'
                    }
                }), 400
        
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = None
        if data.get('end_date'):
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        schedule = PickupSchedule(
            municipality_id=data['municipality_id'],
            schedule_name=data['schedule_name'],
            schedule_type=data['schedule_type'],
            description=data.get('description'),
            frequency=data['frequency'],
            start_date=start_date,
            end_date=end_date,
            rules=data.get('rules')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'schedule': schedule.to_dict()
            },
            'message': 'Schedule created successfully',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'requestId': f'req_{datetime.utcnow().timestamp()}'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_DATE_FORMAT',
                'message': 'Date must be in YYYY-MM-DD format'
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

