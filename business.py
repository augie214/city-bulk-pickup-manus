from flask import Blueprint, request, jsonify
from src.models.business import db, Business, BusinessService, BusinessPhoto, BusinessReview
from datetime import datetime
import json

business_bp = Blueprint('business', __name__)

@business_bp.route('/businesses/search', methods=['GET'])
def search_businesses():
    """Search for service businesses"""
    try:
        # Get query parameters
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', 10, type=int)
        service_category = request.args.get('serviceCategory')
        min_rating = request.args.get('minRating', type=float)
        sort_by = request.args.get('sortBy', 'distance')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Mock data for demonstration
        mock_businesses = [
            {
                'id': 'business_123',
                'name': 'Green Cleanup Services',
                'rating': 4.8,
                'ratingCount': 127,
                'distance': 2.3,
                'services': ['junk_removal', 'yard_cleanup'],
                'priceRange': '$$',
                'profileImageUrl': 'https://example.com/profile1.jpg',
                'responseTime': 'within 2 hours',
                'isVerified': True,
                'totalJobsCompleted': 1250
            },
            {
                'id': 'business_124',
                'name': 'Rapid Trash Solutions',
                'rating': 4.7,
                'ratingCount': 89,
                'distance': 3.1,
                'services': ['furniture_removal', 'appliance_pickup'],
                'priceRange': '$$$',
                'profileImageUrl': 'https://example.com/profile2.jpg',
                'responseTime': 'within 4 hours',
                'isVerified': True,
                'totalJobsCompleted': 856
            },
            {
                'id': 'business_125',
                'name': 'EcoWaste Pros',
                'rating': 4.6,
                'ratingCount': 156,
                'distance': 4.2,
                'services': ['recycling', 'hazardous_waste'],
                'priceRange': '$',
                'profileImageUrl': 'https://example.com/profile3.jpg',
                'responseTime': 'same day',
                'isVerified': False,
                'totalJobsCompleted': 2100
            }
        ]
        
        # Apply filters
        filtered_businesses = mock_businesses
        
        if service_category:
            filtered_businesses = [b for b in filtered_businesses if service_category in b['services']]
        
        if min_rating:
            filtered_businesses = [b for b in filtered_businesses if b['rating'] >= min_rating]
        
        # Apply sorting
        if sort_by == 'distance':
            filtered_businesses.sort(key=lambda x: x['distance'])
        elif sort_by == 'rating':
            filtered_businesses.sort(key=lambda x: x['rating'], reverse=True)
        elif sort_by == 'price':
            price_order = {'$': 1, '$$': 2, '$$$': 3}
            filtered_businesses.sort(key=lambda x: price_order.get(x['priceRange'], 2))
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_businesses = filtered_businesses[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'data': {
                'businesses': paginated_businesses,
                'totalCount': len(filtered_businesses),
                'page': page,
                'limit': limit
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

@business_bp.route('/businesses/<business_id>', methods=['GET'])
def get_business_profile(business_id):
    """Get detailed business profile"""
    try:
        # Mock data for demonstration
        mock_business = {
            'id': business_id,
            'name': 'Green Cleanup Services',
            'description': 'Professional junk removal and cleanup services with over 10 years of experience. We handle everything from furniture removal to complete property cleanouts.',
            'rating': 4.8,
            'ratingCount': 127,
            'totalJobsCompleted': 1250,
            'isVerified': True,
            'businessType': 'junk_removal',
            'websiteUrl': 'https://greencleanup.com',
            'businessPhone': '+1234567890',
            'businessEmail': 'info@greencleanup.com',
            'serviceRadiusMiles': 25,
            'responseTimeHours': 2,
            'subscriptionTier': 'premium',
            'services': [
                {
                    'id': 'service_456',
                    'name': 'Furniture Removal',
                    'category': 'junk_removal',
                    'description': 'Safe and efficient removal of furniture items',
                    'basePrice': 75.00,
                    'priceUnit': 'per_item',
                    'minimumCharge': 50.00,
                    'estimatedDurationHours': 1.5
                },
                {
                    'id': 'service_457',
                    'name': 'Appliance Pickup',
                    'category': 'junk_removal',
                    'description': 'Removal and disposal of large appliances',
                    'basePrice': 100.00,
                    'priceUnit': 'per_item',
                    'minimumCharge': 75.00,
                    'estimatedDurationHours': 2.0
                }
            ],
            'photos': [
                {
                    'url': 'https://example.com/photo1.jpg',
                    'type': 'gallery',
                    'caption': 'Before and after cleanup'
                },
                {
                    'url': 'https://example.com/photo2.jpg',
                    'type': 'equipment',
                    'caption': 'Our professional equipment'
                }
            ],
            'reviews': [
                {
                    'id': 'review_789',
                    'rating': 5,
                    'title': 'Excellent service!',
                    'text': 'Very professional and efficient. They arrived on time and completed the job quickly.',
                    'reviewerName': 'John D.',
                    'createdAt': '2025-09-01T10:00:00Z',
                    'isVerified': True
                },
                {
                    'id': 'review_790',
                    'rating': 4,
                    'title': 'Good value',
                    'text': 'Fair pricing and good service. Would recommend.',
                    'reviewerName': 'Sarah M.',
                    'createdAt': '2025-08-15T14:30:00Z',
                    'isVerified': True
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'data': mock_business,
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

@business_bp.route('/businesses/profile', methods=['POST'])
def create_business_profile():
    """Create or update business profile (business users only)"""
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
        
        required_fields = ['businessName', 'businessType']
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
        
        # Check if business profile already exists
        existing_business = Business.query.filter_by(user_id=user_id).first()
        
        if existing_business:
            # Update existing business
            existing_business.business_name = data['businessName']
            existing_business.business_type = data['businessType']
            existing_business.description = data.get('description')
            existing_business.website_url = data.get('websiteUrl')
            existing_business.business_phone = data.get('businessPhone')
            existing_business.business_email = data.get('businessEmail')
            existing_business.license_number = data.get('licenseNumber')
            existing_business.service_radius_miles = data.get('serviceRadiusMiles', 25)
            existing_business.updated_at = datetime.utcnow()
            
            business = existing_business
        else:
            # Create new business
            business = Business(
                user_id=user_id,
                business_name=data['businessName'],
                business_type=data['businessType'],
                description=data.get('description'),
                website_url=data.get('websiteUrl'),
                business_phone=data.get('businessPhone'),
                business_email=data.get('businessEmail'),
                license_number=data.get('licenseNumber'),
                service_radius_miles=data.get('serviceRadiusMiles', 25)
            )
            db.session.add(business)
        
        # Handle services
        if 'services' in data:
            # Remove existing services
            BusinessService.query.filter_by(business_id=business.id).delete()
            
            # Add new services
            for service_data in data['services']:
                service = BusinessService(
                    business_id=business.id,
                    service_category=service_data['category'],
                    service_name=service_data['name'],
                    service_description=service_data.get('description'),
                    base_price=service_data.get('basePrice'),
                    price_unit=service_data.get('priceUnit'),
                    minimum_charge=service_data.get('minimumCharge')
                )
                db.session.add(service)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'business': business.to_dict()
            },
            'message': 'Business profile updated successfully',
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

@business_bp.route('/businesses/profile', methods=['GET'])
def get_business_profile_current():
    """Get current user's business profile"""
    try:
        # Mock user ID - in real implementation, get from JWT token
        user_id = 'user_123'
        
        business = Business.query.filter_by(user_id=user_id).first()
        
        if not business:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BUSINESS_NOT_FOUND',
                    'message': 'Business profile not found'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'business': business.to_dict()
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

@business_bp.route('/businesses/<business_id>/reviews', methods=['POST'])
def create_business_review(business_id):
    """Create a review for a business"""
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
        
        required_fields = ['rating']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Field {field} is required'
                    }
                }), 400
        
        if not (1 <= data['rating'] <= 5):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_RATING',
                    'message': 'Rating must be between 1 and 5'
                }
            }), 400
        
        # Mock user ID - in real implementation, get from JWT token
        reviewer_user_id = 'user_456'
        
        review = BusinessReview(
            business_id=business_id,
            reviewer_user_id=reviewer_user_id,
            booking_id=data.get('bookingId'),
            rating=data['rating'],
            review_title=data.get('reviewTitle'),
            review_text=data.get('reviewText')
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'review': review.to_dict()
            },
            'message': 'Review created successfully',
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

@business_bp.route('/businesses/<business_id>/reviews', methods=['GET'])
def get_business_reviews(business_id):
    """Get reviews for a business"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        reviews = BusinessReview.query.filter_by(
            business_id=business_id,
            is_public=True
        ).order_by(BusinessReview.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'reviews': [review.to_dict() for review in reviews.items],
                'totalCount': reviews.total,
                'page': page,
                'limit': limit,
                'hasNext': reviews.has_next,
                'hasPrev': reviews.has_prev
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

