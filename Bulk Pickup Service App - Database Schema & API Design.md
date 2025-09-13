# Bulk Pickup Service App - Database Schema & API Design

**Author:** Manus AI  
**Date:** September 12, 2025  
**Version:** 1.0

## Overview

This document provides comprehensive specifications for the database schema and RESTful API design for the Bulk Pickup Service mobile application. The design follows microservices architecture principles with dedicated databases for each service domain, ensuring scalability, data isolation, and optimal performance.

## Database Architecture Strategy

### Multi-Database Approach

The application employs a polyglot persistence strategy, utilizing different database technologies optimized for specific data types and access patterns:

**PostgreSQL Databases:**
- Primary choice for transactional data requiring ACID compliance
- Excellent support for complex queries and relationships
- Strong consistency guarantees for critical business data

**MongoDB Databases:**
- Document storage for flexible, evolving data structures
- Geospatial indexing for location-based queries
- Horizontal scaling capabilities for large datasets

**Redis Cache:**
- In-memory storage for session management
- Real-time data caching for improved performance
- Pub/Sub messaging for notifications

### Database Distribution by Service

Each microservice maintains its own database to ensure service independence and data encapsulation:

1. **User Service Database** (PostgreSQL)
2. **Location Service Database** (MongoDB)
3. **Schedule Service Database** (PostgreSQL)
4. **Business Service Database** (PostgreSQL)
5. **Booking Service Database** (PostgreSQL)
6. **Notification Service Cache** (Redis)

## Detailed Database Schemas

### 1. User Service Database (PostgreSQL)

The User Service manages all user-related data including authentication, profiles, and account settings.

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('resident', 'business', 'admin')),
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    profile_image_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language_preference VARCHAR(10) DEFAULT 'en',
    notification_preferences JSONB DEFAULT '{"email": true, "push": true, "sms": false}'
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### User Authentication Table
```sql
CREATE TABLE user_auth_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('email', 'google', 'facebook', 'apple')),
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_auth_providers_user_id ON user_auth_providers(user_id);
CREATE INDEX idx_auth_providers_provider ON user_auth_providers(provider);
```

#### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
```

#### User Addresses Table
```sql
CREATE TABLE user_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    country VARCHAR(50) DEFAULT 'US',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    google_place_id VARCHAR(255),
    formatted_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_addresses_user_id ON user_addresses(user_id);
CREATE INDEX idx_addresses_coordinates ON user_addresses(latitude, longitude);
CREATE INDEX idx_addresses_zip_code ON user_addresses(zip_code);
```

### 2. Location Service Database (MongoDB)

The Location Service handles geospatial data, address lookups, and mapping functionality.

#### Addresses Collection
```javascript
{
  _id: ObjectId,
  googlePlaceId: String,
  formattedAddress: String,
  addressComponents: {
    streetNumber: String,
    route: String,
    locality: String,
    administrativeAreaLevel1: String,
    administrativeAreaLevel2: String,
    country: String,
    postalCode: String
  },
  geometry: {
    type: "Point",
    coordinates: [longitude, latitude] // GeoJSON format
  },
  placeTypes: [String],
  businessStatus: String,
  rating: Number,
  userRatingsTotal: Number,
  priceLevel: Number,
  photos: [{
    photoReference: String,
    height: Number,
    width: Number,
    htmlAttributions: [String]
  }],
  openingHours: {
    openNow: Boolean,
    periods: [{
      open: { day: Number, time: String },
      close: { day: Number, time: String }
    }],
    weekdayText: [String]
  },
  website: String,
  phoneNumber: String,
  internationalPhoneNumber: String,
  createdAt: Date,
  updatedAt: Date,
  lastVerified: Date
}

// Indexes
db.addresses.createIndex({ "geometry": "2dsphere" })
db.addresses.createIndex({ "googlePlaceId": 1 }, { unique: true })
db.addresses.createIndex({ "addressComponents.postalCode": 1 })
db.addresses.createIndex({ "formattedAddress": "text" })
```

#### Service Areas Collection
```javascript
{
  _id: ObjectId,
  businessId: String, // Reference to business in Business Service
  serviceAreaName: String,
  geometry: {
    type: "Polygon", // or "MultiPolygon"
    coordinates: [[[longitude, latitude]]] // GeoJSON format
  },
  serviceTypes: [String],
  isActive: Boolean,
  priority: Number,
  createdAt: Date,
  updatedAt: Date
}

// Indexes
db.serviceAreas.createIndex({ "geometry": "2dsphere" })
db.serviceAreas.createIndex({ "businessId": 1 })
db.serviceAreas.createIndex({ "serviceTypes": 1 })
```

### 3. Schedule Service Database (PostgreSQL)

The Schedule Service manages bulk pickup schedules, recurring events, and notifications.

#### Pickup Schedules Table
```sql
CREATE TABLE pickup_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    municipality_id UUID NOT NULL,
    schedule_name VARCHAR(255) NOT NULL,
    schedule_type VARCHAR(50) NOT NULL CHECK (schedule_type IN ('bulk', 'yard_waste', 'recycling', 'special')),
    description TEXT,
    frequency VARCHAR(50) NOT NULL CHECK (frequency IN ('weekly', 'biweekly', 'monthly', 'quarterly', 'annual', 'on_demand')),
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    rules JSONB -- Stores complex scheduling rules
);

CREATE INDEX idx_schedules_municipality ON pickup_schedules(municipality_id);
CREATE INDEX idx_schedules_type ON pickup_schedules(schedule_type);
CREATE INDEX idx_schedules_dates ON pickup_schedules(start_date, end_date);
```

#### Schedule Zones Table
```sql
CREATE TABLE schedule_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID NOT NULL REFERENCES pickup_schedules(id) ON DELETE CASCADE,
    zone_name VARCHAR(255) NOT NULL,
    zone_description TEXT,
    pickup_day VARCHAR(20) NOT NULL CHECK (pickup_day IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')),
    pickup_time_start TIME,
    pickup_time_end TIME,
    special_instructions TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_zones_schedule_id ON schedule_zones(schedule_id);
CREATE INDEX idx_zones_pickup_day ON schedule_zones(pickup_day);
```

#### Zone Coverage Areas Table
```sql
CREATE TABLE zone_coverage_areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID NOT NULL REFERENCES schedule_zones(id) ON DELETE CASCADE,
    coverage_type VARCHAR(50) NOT NULL CHECK (coverage_type IN ('zip_code', 'street_range', 'polygon', 'address_list')),
    coverage_data JSONB NOT NULL, -- Flexible storage for different coverage types
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coverage_zone_id ON zone_coverage_areas(zone_id);
CREATE INDEX idx_coverage_type ON zone_coverage_areas(coverage_type);
CREATE INDEX idx_coverage_data_gin ON zone_coverage_areas USING GIN (coverage_data);
```

#### Pickup Events Table
```sql
CREATE TABLE pickup_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID NOT NULL REFERENCES pickup_schedules(id),
    zone_id UUID REFERENCES schedule_zones(id),
    event_date DATE NOT NULL,
    event_time_start TIME,
    event_time_end TIME,
    status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled')),
    weather_conditions VARCHAR(100),
    crew_assigned VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_events_schedule_id ON pickup_events(schedule_id);
CREATE INDEX idx_events_date ON pickup_events(event_date);
CREATE INDEX idx_events_status ON pickup_events(status);
```

#### User Schedule Subscriptions Table
```sql
CREATE TABLE user_schedule_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    address_id UUID NOT NULL,
    schedule_id UUID NOT NULL REFERENCES pickup_schedules(id),
    zone_id UUID REFERENCES schedule_zones(id),
    notification_preferences JSONB DEFAULT '{"email": true, "push": true, "sms": false, "advance_days": [1, 7]}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, address_id, schedule_id)
);

CREATE INDEX idx_subscriptions_user_id ON user_schedule_subscriptions(user_id);
CREATE INDEX idx_subscriptions_schedule_id ON user_schedule_subscriptions(schedule_id);
```

### 4. Business Service Database (PostgreSQL)

The Business Service manages service provider profiles, capabilities, and business logic.

#### Businesses Table
```sql
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- References users table in User Service
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100) NOT NULL,
    description TEXT,
    website_url VARCHAR(500),
    business_phone VARCHAR(20),
    business_email VARCHAR(255),
    license_number VARCHAR(100),
    insurance_policy_number VARCHAR(100),
    insurance_expiry_date DATE,
    tax_id VARCHAR(50),
    business_address JSONB,
    service_radius_miles INTEGER DEFAULT 25,
    minimum_job_value DECIMAL(10, 2),
    maximum_job_value DECIMAL(10, 2),
    response_time_hours INTEGER DEFAULT 24,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR(50) DEFAULT 'basic' CHECK (subscription_tier IN ('basic', 'premium', 'enterprise')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    rating_average DECIMAL(3, 2) DEFAULT 0.00,
    rating_count INTEGER DEFAULT 0,
    total_jobs_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_businesses_user_id ON businesses(user_id);
CREATE INDEX idx_businesses_type ON businesses(business_type);
CREATE INDEX idx_businesses_verified ON businesses(is_verified);
CREATE INDEX idx_businesses_rating ON businesses(rating_average);
```

#### Business Services Table
```sql
CREATE TABLE business_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_category VARCHAR(100) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    service_description TEXT,
    base_price DECIMAL(10, 2),
    price_unit VARCHAR(50), -- 'per_hour', 'per_item', 'per_load', 'flat_rate'
    minimum_charge DECIMAL(10, 2),
    is_available BOOLEAN DEFAULT TRUE,
    requires_estimate BOOLEAN DEFAULT FALSE,
    estimated_duration_hours DECIMAL(4, 2),
    special_requirements TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_services_business_id ON business_services(business_id);
CREATE INDEX idx_services_category ON business_services(service_category);
CREATE INDEX idx_services_available ON business_services(is_available);
```

#### Business Photos Table
```sql
CREATE TABLE business_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    photo_url VARCHAR(500) NOT NULL,
    photo_type VARCHAR(50) CHECK (photo_type IN ('profile', 'gallery', 'before_after', 'equipment', 'team')),
    caption TEXT,
    display_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_photos_business_id ON business_photos(business_id);
CREATE INDEX idx_photos_type ON business_photos(photo_type);
```

#### Business Reviews Table
```sql
CREATE TABLE business_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    reviewer_user_id UUID NOT NULL,
    booking_id UUID, -- Optional reference to booking
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_title VARCHAR(255),
    review_text TEXT,
    response_text TEXT, -- Business response to review
    response_date TIMESTAMP WITH TIME ZONE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_business_id ON business_reviews(business_id);
CREATE INDEX idx_reviews_rating ON business_reviews(rating);
CREATE INDEX idx_reviews_created_at ON business_reviews(created_at);
```

### 5. Booking Service Database (PostgreSQL)

The Booking Service handles service requests, quotes, bookings, and transactions.

#### Service Requests Table
```sql
CREATE TABLE service_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_user_id UUID NOT NULL,
    customer_address_id UUID NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    service_description TEXT NOT NULL,
    preferred_date DATE,
    preferred_time_start TIME,
    preferred_time_end TIME,
    urgency_level VARCHAR(20) DEFAULT 'normal' CHECK (urgency_level IN ('low', 'normal', 'high', 'emergency')),
    estimated_budget DECIMAL(10, 2),
    special_instructions TEXT,
    photos JSONB, -- Array of photo URLs
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'quoted', 'booked', 'completed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_requests_customer_id ON service_requests(customer_user_id);
CREATE INDEX idx_requests_category ON service_requests(service_category);
CREATE INDEX idx_requests_status ON service_requests(status);
CREATE INDEX idx_requests_date ON service_requests(preferred_date);
```

#### Service Quotes Table
```sql
CREATE TABLE service_quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    business_id UUID NOT NULL,
    quote_amount DECIMAL(10, 2) NOT NULL,
    quote_details TEXT,
    estimated_duration_hours DECIMAL(4, 2),
    materials_included BOOLEAN DEFAULT TRUE,
    disposal_included BOOLEAN DEFAULT TRUE,
    additional_fees JSONB, -- Breakdown of additional costs
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'expired', 'withdrawn')),
    terms_and_conditions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quotes_request_id ON service_quotes(request_id);
CREATE INDEX idx_quotes_business_id ON service_quotes(business_id);
CREATE INDEX idx_quotes_status ON service_quotes(status);
```

#### Bookings Table
```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES service_requests(id),
    quote_id UUID NOT NULL REFERENCES service_quotes(id),
    customer_user_id UUID NOT NULL,
    business_id UUID NOT NULL,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_time_start TIME NOT NULL,
    scheduled_time_end TIME,
    actual_start_time TIMESTAMP WITH TIME ZONE,
    actual_end_time TIMESTAMP WITH TIME ZONE,
    final_amount DECIMAL(10, 2),
    payment_status VARCHAR(50) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'partial', 'refunded', 'failed')),
    booking_status VARCHAR(50) DEFAULT 'confirmed' CHECK (booking_status IN ('confirmed', 'in_progress', 'completed', 'cancelled', 'rescheduled')),
    cancellation_reason TEXT,
    completion_notes TEXT,
    customer_signature TEXT, -- Base64 encoded signature
    before_photos JSONB,
    after_photos JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_bookings_customer_id ON bookings(customer_user_id);
CREATE INDEX idx_bookings_business_id ON bookings(business_id);
CREATE INDEX idx_bookings_status ON bookings(booking_status);
CREATE INDEX idx_bookings_date ON bookings(scheduled_date);
CREATE INDEX idx_bookings_reference ON bookings(booking_reference);
```

#### Payments Table
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id),
    payment_intent_id VARCHAR(255), -- Stripe payment intent ID
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL CHECK (payment_status IN ('pending', 'processing', 'succeeded', 'failed', 'cancelled', 'refunded')),
    stripe_charge_id VARCHAR(255),
    failure_reason TEXT,
    refund_amount DECIMAL(10, 2) DEFAULT 0.00,
    refund_reason TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_booking_id ON payments(booking_id);
CREATE INDEX idx_payments_status ON payments(payment_status);
CREATE INDEX idx_payments_stripe_id ON payments(stripe_charge_id);
```

### 6. Notification Service (Redis)

The Notification Service uses Redis for temporary storage of notification data and real-time messaging.

#### Redis Data Structures

**User Notification Preferences:**
```
Key: user:notifications:{user_id}
Type: Hash
Fields:
- email_enabled: "true"/"false"
- push_enabled: "true"/"false"
- sms_enabled: "true"/"false"
- pickup_reminders: "1,7" (days before)
- business_leads: "true"/"false"
- booking_updates: "true"/"false"
```

**Push Notification Tokens:**
```
Key: user:push_tokens:{user_id}
Type: Set
Members: FCM tokens for user's devices
```

**Notification Queue:**
```
Key: notifications:queue:{priority}
Type: List
Values: JSON notification objects
```

**Notification History:**
```
Key: user:notification_history:{user_id}
Type: Sorted Set
Score: timestamp
Member: notification_id
```

## RESTful API Design

### API Architecture Principles

The API follows RESTful design principles with consistent patterns across all endpoints:

**Base URL Structure:**
```
https://api.bulkpickupapp.com/v1/{service}/{resource}
```

**Standard HTTP Methods:**
- GET: Retrieve resources
- POST: Create new resources
- PUT: Update entire resources
- PATCH: Partial resource updates
- DELETE: Remove resources

**Response Format:**
All API responses follow a consistent JSON structure:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-09-12T10:30:00Z",
  "requestId": "req_123456789"
}
```

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "timestamp": "2025-09-12T10:30:00Z",
  "requestId": "req_123456789"
}
```

### Authentication API Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "firstName": "John",
  "lastName": "Doe",
  "userType": "resident",
  "phoneNumber": "+1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "userType": "resident",
      "emailVerified": false
    },
    "tokens": {
      "accessToken": "jwt_access_token",
      "refreshToken": "jwt_refresh_token",
      "expiresIn": 3600
    }
  }
}
```

#### POST /auth/login
Authenticate user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "deviceInfo": {
    "platform": "ios",
    "version": "15.0",
    "deviceId": "device_123"
  }
}
```

#### POST /auth/social/google
Authenticate user with Google Sign-In.

**Request Body:**
```json
{
  "idToken": "google_id_token",
  "accessToken": "google_access_token",
  "userType": "resident"
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refreshToken": "jwt_refresh_token"
}
```

#### POST /auth/logout
Logout user and invalidate tokens.

**Headers:**
```
Authorization: Bearer jwt_access_token
```

### User Management API Endpoints

#### GET /users/profile
Get current user profile information.

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phoneNumber": "+1234567890",
    "userType": "resident",
    "profileImageUrl": "https://...",
    "emailVerified": true,
    "phoneVerified": false,
    "notificationPreferences": {
      "email": true,
      "push": true,
      "sms": false
    }
  }
}
```

#### PUT /users/profile
Update user profile information.

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Smith",
  "phoneNumber": "+1234567890",
  "notificationPreferences": {
    "email": true,
    "push": true,
    "sms": true
  }
}
```

#### GET /users/addresses
Get user's saved addresses.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "addr_123",
      "addressLine1": "123 Main St",
      "addressLine2": "Apt 4B",
      "city": "Springfield",
      "state": "IL",
      "zipCode": "62701",
      "isPrimary": true,
      "isVerified": true,
      "formattedAddress": "123 Main St, Apt 4B, Springfield, IL 62701"
    }
  ]
}
```

#### POST /users/addresses
Add a new address for the user.

**Request Body:**
```json
{
  "addressLine1": "456 Oak Ave",
  "addressLine2": "",
  "city": "Springfield",
  "state": "IL",
  "zipCode": "62702",
  "isPrimary": false,
  "googlePlaceId": "ChIJ..."
}
```

### Location API Endpoints

#### GET /locations/autocomplete
Get address suggestions based on input text.

**Query Parameters:**
- `input`: Search text
- `types`: Address types (optional)
- `location`: Bias location (lat,lng)
- `radius`: Search radius in meters

**Response:**
```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "placeId": "ChIJ...",
        "description": "123 Main St, Springfield, IL, USA",
        "structuredFormatting": {
          "mainText": "123 Main St",
          "secondaryText": "Springfield, IL, USA"
        }
      }
    ]
  }
}
```

#### GET /locations/details/{placeId}
Get detailed information for a specific place.

**Response:**
```json
{
  "success": true,
  "data": {
    "placeId": "ChIJ...",
    "formattedAddress": "123 Main St, Springfield, IL 62701, USA",
    "geometry": {
      "location": {
        "lat": 39.7817,
        "lng": -89.6501
      }
    },
    "addressComponents": [
      {
        "longName": "123",
        "shortName": "123",
        "types": ["street_number"]
      }
    ]
  }
}
```

### Schedule API Endpoints

#### GET /schedules/lookup
Look up pickup schedules for a specific address.

**Query Parameters:**
- `address`: Full address string
- `lat`: Latitude
- `lng`: Longitude
- `zipCode`: ZIP code

**Response:**
```json
{
  "success": true,
  "data": {
    "schedules": [
      {
        "id": "schedule_123",
        "name": "Springfield Bulk Pickup",
        "type": "bulk",
        "frequency": "monthly",
        "nextPickupDate": "2025-10-15",
        "zone": {
          "id": "zone_456",
          "name": "Zone A",
          "pickupDay": "tuesday"
        }
      }
    ]
  }
}
```

#### GET /schedules/{scheduleId}/events
Get upcoming pickup events for a schedule.

**Query Parameters:**
- `startDate`: Start date (YYYY-MM-DD)
- `endDate`: End date (YYYY-MM-DD)
- `limit`: Maximum number of events

**Response:**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": "event_789",
        "date": "2025-10-15",
        "timeStart": "08:00",
        "timeEnd": "17:00",
        "status": "scheduled",
        "zone": {
          "id": "zone_456",
          "name": "Zone A"
        }
      }
    ]
  }
}
```

#### POST /schedules/subscriptions
Subscribe to pickup schedule notifications.

**Request Body:**
```json
{
  "scheduleId": "schedule_123",
  "addressId": "addr_123",
  "notificationPreferences": {
    "email": true,
    "push": true,
    "sms": false,
    "advanceDays": [1, 7]
  }
}
```

### Business API Endpoints

#### GET /businesses/search
Search for service businesses.

**Query Parameters:**
- `lat`: Latitude
- `lng`: Longitude
- `radius`: Search radius in miles
- `serviceCategory`: Service category filter
- `minRating`: Minimum rating filter
- `sortBy`: Sort criteria (distance, rating, price)

**Response:**
```json
{
  "success": true,
  "data": {
    "businesses": [
      {
        "id": "business_123",
        "name": "Green Cleanup Services",
        "rating": 4.8,
        "ratingCount": 127,
        "distance": 2.3,
        "services": ["junk_removal", "yard_cleanup"],
        "priceRange": "$$",
        "profileImageUrl": "https://...",
        "responseTime": "within 2 hours"
      }
    ],
    "totalCount": 15,
    "page": 1,
    "limit": 10
  }
}
```

#### GET /businesses/{businessId}
Get detailed business profile.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "business_123",
    "name": "Green Cleanup Services",
    "description": "Professional junk removal and cleanup services...",
    "rating": 4.8,
    "ratingCount": 127,
    "totalJobsCompleted": 1250,
    "isVerified": true,
    "services": [
      {
        "id": "service_456",
        "name": "Furniture Removal",
        "category": "junk_removal",
        "basePrice": 75.00,
        "priceUnit": "per_item"
      }
    ],
    "photos": [
      {
        "url": "https://...",
        "type": "gallery",
        "caption": "Before and after cleanup"
      }
    ],
    "reviews": [
      {
        "id": "review_789",
        "rating": 5,
        "title": "Excellent service!",
        "text": "Very professional and efficient...",
        "reviewerName": "John D.",
        "createdAt": "2025-09-01T10:00:00Z"
      }
    ]
  }
}
```

#### POST /businesses/profile
Create or update business profile (business users only).

**Request Body:**
```json
{
  "businessName": "Green Cleanup Services",
  "businessType": "junk_removal",
  "description": "Professional cleanup services...",
  "websiteUrl": "https://greencleanup.com",
  "businessPhone": "+1234567890",
  "licenseNumber": "LIC123456",
  "serviceRadiusMiles": 25,
  "services": [
    {
      "category": "junk_removal",
      "name": "Furniture Removal",
      "basePrice": 75.00,
      "priceUnit": "per_item"
    }
  ]
}
```

### Booking API Endpoints

#### POST /bookings/requests
Create a new service request.

**Request Body:**
```json
{
  "addressId": "addr_123",
  "serviceCategory": "junk_removal",
  "description": "Need to remove old furniture and appliances",
  "preferredDate": "2025-10-20",
  "preferredTimeStart": "09:00",
  "preferredTimeEnd": "12:00",
  "estimatedBudget": 200.00,
  "photos": ["https://photo1.jpg", "https://photo2.jpg"]
}
```

#### GET /bookings/requests/{requestId}/quotes
Get quotes for a service request.

**Response:**
```json
{
  "success": true,
  "data": {
    "quotes": [
      {
        "id": "quote_123",
        "businessId": "business_456",
        "businessName": "Green Cleanup Services",
        "amount": 175.00,
        "details": "Removal of 3 furniture items and 2 appliances",
        "estimatedDuration": 2.5,
        "validUntil": "2025-10-18T23:59:59Z",
        "status": "pending"
      }
    ]
  }
}
```

#### POST /bookings/quotes/{quoteId}/accept
Accept a quote and create a booking.

**Request Body:**
```json
{
  "scheduledDate": "2025-10-20",
  "scheduledTimeStart": "10:00",
  "paymentMethodId": "pm_stripe_123"
}
```

#### GET /bookings/history
Get user's booking history.

**Query Parameters:**
- `status`: Filter by booking status
- `limit`: Number of results
- `offset`: Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "bookings": [
      {
        "id": "booking_123",
        "reference": "BK-2025-001234",
        "businessName": "Green Cleanup Services",
        "serviceDescription": "Furniture removal",
        "scheduledDate": "2025-10-20",
        "status": "completed",
        "finalAmount": 175.00,
        "rating": 5
      }
    ]
  }
}
```

### Payment API Endpoints

#### POST /payments/setup-intent
Create a payment setup intent for saving payment methods.

**Response:**
```json
{
  "success": true,
  "data": {
    "clientSecret": "seti_stripe_client_secret",
    "setupIntentId": "seti_stripe_123"
  }
}
```

#### POST /payments/payment-intent
Create a payment intent for booking payment.

**Request Body:**
```json
{
  "bookingId": "booking_123",
  "amount": 175.00,
  "paymentMethodId": "pm_stripe_456"
}
```

#### GET /payments/methods
Get user's saved payment methods.

**Response:**
```json
{
  "success": true,
  "data": {
    "paymentMethods": [
      {
        "id": "pm_stripe_123",
        "type": "card",
        "card": {
          "brand": "visa",
          "last4": "4242",
          "expMonth": 12,
          "expYear": 2026
        },
        "isDefault": true
      }
    ]
  }
}
```

### Notification API Endpoints

#### POST /notifications/register-device
Register device for push notifications.

**Request Body:**
```json
{
  "token": "fcm_device_token",
  "platform": "ios",
  "deviceId": "device_unique_id"
}
```

#### GET /notifications/history
Get notification history for user.

**Query Parameters:**
- `limit`: Number of notifications
- `offset`: Pagination offset
- `type`: Filter by notification type

**Response:**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": "notif_123",
        "type": "pickup_reminder",
        "title": "Bulk Pickup Tomorrow",
        "message": "Don't forget your bulk pickup is scheduled for tomorrow",
        "isRead": false,
        "createdAt": "2025-09-11T18:00:00Z"
      }
    ]
  }
}
```

#### PUT /notifications/{notificationId}/read
Mark notification as read.

## API Security and Rate Limiting

### Authentication and Authorization

**JWT Token Structure:**
```json
{
  "sub": "user_123",
  "email": "user@example.com",
  "userType": "resident",
  "permissions": ["read:profile", "write:addresses"],
  "iat": 1694520000,
  "exp": 1694523600
}
```

**Rate Limiting:**
- Authentication endpoints: 5 requests per minute per IP
- General API endpoints: 100 requests per minute per user
- Search endpoints: 50 requests per minute per user
- File upload endpoints: 10 requests per minute per user

### Data Validation and Sanitization

All API endpoints implement comprehensive input validation:

**Email Validation:**
- RFC 5322 compliant email format
- Domain validation against known providers
- Disposable email detection

**Address Validation:**
- Google Places API verification
- Coordinate validation for latitude/longitude
- ZIP code format validation by country

**Business Data Validation:**
- License number format validation by state
- Phone number E.164 format validation
- URL format validation for websites

## Database Performance Optimization

### Indexing Strategy

**Primary Indexes:**
- All primary keys use UUID with B-tree indexes
- Foreign key relationships have corresponding indexes
- Frequently queried columns have dedicated indexes

**Composite Indexes:**
- Multi-column indexes for common query patterns
- Covering indexes for read-heavy operations
- Partial indexes for filtered queries

**Geospatial Indexes:**
- 2dsphere indexes for MongoDB location queries
- GiST indexes for PostgreSQL geometric data
- Spatial partitioning for large datasets

### Query Optimization

**Database Connection Pooling:**
- Connection pool size: 20-50 connections per service
- Connection timeout: 30 seconds
- Idle connection timeout: 10 minutes

**Query Performance:**
- Prepared statements for repeated queries
- Query result caching for static data
- Pagination for large result sets
- Lazy loading for related data

### Backup and Recovery

**Automated Backups:**
- Daily full backups with 30-day retention
- Hourly incremental backups during business hours
- Cross-region backup replication
- Point-in-time recovery capability

**Disaster Recovery:**
- Recovery Time Objective (RTO): 4 hours
- Recovery Point Objective (RPO): 1 hour
- Automated failover for critical services
- Regular disaster recovery testing

This comprehensive database schema and API design provides a robust foundation for the Bulk Pickup Service mobile application, ensuring scalability, security, and optimal performance while maintaining data integrity and consistency across all services.

