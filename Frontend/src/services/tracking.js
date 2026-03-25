// Tracking service for user behavior analytics
const API_BASE_URL = 'http://localhost:8000';

class TrackingService {
  constructor() {
    this.userId = this.getUserId();
    this.sessionId = this.getSessionId();
    this.deviceType = this.getDeviceType();
  }

  getUserId() {
    // For now, use a simple localStorage-based user ID
    let userId = localStorage.getItem('user_id');
    if (!userId) {
      userId = 'user_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('user_id', userId);
    }
    return userId;
  }

  getSessionId() {
    // Create session ID that expires after 30 minutes of inactivity
    const sessionKey = 'session_id';
    const sessionTimeKey = 'session_time';
    const now = Date.now();
    const thirtyMinutes = 30 * 60 * 1000;

    const lastSessionTime = localStorage.getItem(sessionTimeKey);
    const sessionId = localStorage.getItem(sessionKey);

    if (sessionId && lastSessionTime && (now - parseInt(lastSessionTime)) < thirtyMinutes) {
      // Update session time
      localStorage.setItem(sessionTimeKey, now.toString());
      return sessionId;
    }

    // Create new session
    const newSessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem(sessionKey, newSessionId);
    localStorage.setItem(sessionTimeKey, now.toString());
    return newSessionId;
  }

  getDeviceType() {
    const userAgent = navigator.userAgent;
    if (/tablet|ipad|playbook|silk/i.test(userAgent)) {
      return 'tablet';
    }
    if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\sce|palm|smartphone|iemobile/i.test(userAgent)) {
      return 'mobile';
    }
    return 'desktop';
  }

  async sendTrackingData(endpoint, data) {
    try {
      const response = await fetch(`${API_BASE_URL}/track/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...data,
          user_id: this.userId,
          device_type: this.deviceType,
          ip_address: '127.0.0.1' // Will be handled by backend
        })
      });

      if (!response.ok) {
        console.warn('Tracking request failed:', response.status);
        return null;
      }

      return await response.json();
    } catch (error) {
      console.warn('Tracking error:', error);
      return null;
    }
  }

  // Location Helper tracking methods
  async trackLocationScan(monumentName, latitude, longitude, wasGuided = false, rating = null) {
    return await this.sendTrackingData('location-scan', {
      monument_name: monumentName,
      latitude,
      longitude,
      was_guided: wasGuided,
      rating
    });
  }

  // Price Helper tracking methods
  async trackPriceScan(productName, productCategory, detectedPrice, ownerAskingPrice = null, location = 'Marrakech Souks') {
    return await this.sendTrackingData('price-scan', {
      product_name: productName,
      product_category: productCategory,
      detected_price: detectedPrice,
      owner_asking_price: ownerAskingPrice,
      location
    });
  }

  async trackPriceRating(scanId, actualPricePaid = null, priceFairnessRating, purchaseMade = false) {
    return await this.sendTrackingData('price-rating', {
      scan_id: scanId,
      actual_price_paid: actualPricePaid,
      price_fairness_rating: priceFairnessRating,
      purchase_made: purchaseMade
    });
  }

  // Hotel tracking methods
  async trackHotelStay(hotelName, checkInDate, checkOutDate, rating, reviewText = null, pricePerNight = null, location = 'Marrakech') {
    return await this.sendTrackingData('hotel-stay', {
      hotel_name: hotelName,
      check_in_date: checkInDate,
      check_out_date: checkOutDate,
      rating,
      review_text: reviewText,
      price_per_night: pricePerNight,
      location
    });
  }

  // Journey tracking methods
  async trackJourneyStart(startLocation = null) {
    return await this.sendTrackingData('journey/start', {
      user_id: this.userId,
      start_location: startLocation
    });
  }

  async trackLocationVisit(journeyId, locationName, latitude, longitude, distanceKm) {
    return await this.sendTrackingData('journey/visit', {
      user_id: this.userId,
      journey_id: journeyId,
      location_name: locationName,
      latitude,
      longitude,
      distance_km: distanceKm,
      visit_timestamp: new Date().toISOString()
    });
  }

  async trackJourneyEnd(journeyId, totalDurationSeconds, locationsVisited, endLocation = null) {
    return await this.sendTrackingData('journey/end', {
      user_id: this.userId,
      journey_id: journeyId,
      end_location: endLocation,
      total_duration_seconds: totalDurationSeconds,
      locations_visited: locationsVisited
    });
  }

  async getJourneyHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/journey/history/${this.userId}`);
      if (!response.ok) {
        console.warn('Journey history request failed:', response.status);
        return null;
      }
      return await response.json();
    } catch (error) {
      console.warn('Journey history error:', error);
      return null;
    }
  }

  async getNearbyLocations(latitude, longitude, radiusKm = 1.0) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/journey/locations/nearby?lat=${latitude}&lon=${longitude}&radius_km=${radiusKm}`);
      if (!response.ok) {
        console.warn('Nearby locations request failed:', response.status);
        return null;
      }
      return await response.json();
    } catch (error) {
      console.warn('Nearby locations error:', error);
      return null;
    }
  }

  // Get user journey data
  async getUserJourney() {
    try {
      const response = await fetch(`${API_BASE_URL}/track/user/journey/${this.userId}`);
      if (!response.ok) {
        console.warn('Journey request failed:', response.status);
        return null;
      }
      return await response.json();
    } catch (error) {
      console.warn('Journey error:', error);
      return null;
    }
  }

  // Utility methods for automatic tracking
  trackPageView(pageName) {
    console.log(`📄 Page View: ${pageName} - User: ${this.userId}, Session: ${this.sessionId}`);
  }

  trackUserAction(action, details = {}) {
    console.log(`🎯 User Action: ${action}`, {
      user_id: this.userId,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      ...details
    });
  }

  // Privacy compliance
  hasTrackingConsent() {
    return localStorage.getItem('tracking_consent') === 'true';
  }

  setTrackingConsent(consent) {
    localStorage.setItem('tracking_consent', consent.toString());
  }

  clearUserData() {
    localStorage.removeItem('user_id');
    localStorage.removeItem('session_id');
    localStorage.removeItem('session_time');
    localStorage.removeItem('tracking_consent');
  }
}

// Create singleton instance
const trackingService = new TrackingService();

export default trackingService;