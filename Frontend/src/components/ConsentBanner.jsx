import React, { useState, useEffect } from 'react';
import trackingService from '../services/tracking';

const ConsentBanner = () => {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Check if user has already given consent
    const hasConsent = localStorage.getItem('tracking_consent');
    if (hasConsent === null) {
      // Show banner after a short delay
      setTimeout(() => setShowBanner(true), 2000);
    }
  }, []);

  const handleAccept = () => {
    trackingService.setTrackingConsent(true);
    setShowBanner(false);
    console.log('✅ User consented to tracking');
  };

  const handleDecline = () => {
    trackingService.setTrackingConsent(false);
    setShowBanner(false);
    console.log('❌ User declined tracking');
  };

  if (!showBanner) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      zIndex: 1000,
      background: '#1C1A17',
      color: 'white',
      padding: '20px',
      boxShadow: '0 -4px 20px rgba(0,0,0,0.3)',
      borderTop: '1px solid rgba(255,255,255,0.1)'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '20px',
        flexWrap: 'wrap'
      }}>
        <div style={{ flex: 1, minWidth: '300px' }}>
          <p style={{
            fontSize: '0.9rem',
            lineHeight: 1.6,
            marginBottom: '8px',
            fontWeight: 500
          }}>
            🍪 We use tracking to improve your experience
          </p>
          <p style={{
            fontSize: '0.8rem',
            color: 'rgba(255,255,255,0.8)',
            lineHeight: 1.5
          }}>
            We track your travel behavior to provide personalized recommendations and improve our services. 
            Your data is anonymized and never shared with third parties.
          </p>
        </div>
        
        <div style={{
          display: 'flex',
          gap: '12px',
          alignItems: 'center'
        }}>
          <button
            onClick={handleDecline}
            style={{
              background: 'transparent',
              border: '1px solid rgba(255,255,255,0.3)',
              color: 'rgba(255,255,255,0.8)',
              padding: '10px 20px',
              borderRadius: '6px',
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              fontFamily: 'inherit'
            }}
            onMouseOver={e => {
              e.currentTarget.style.borderColor = 'rgba(255,255,255,0.5)';
              e.currentTarget.style.color = 'white';
            }}
            onMouseOut={e => {
              e.currentTarget.style.borderColor = 'rgba(255,255,255,0.3)';
              e.currentTarget.style.color = 'rgba(255,255,255,0.8)';
            }}
          >
            Decline
          </button>
          
          <button
            onClick={handleAccept}
            style={{
              background: '#B5451B',
              border: 'none',
              color: 'white',
              padding: '10px 24px',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background 0.2s',
              fontFamily: 'inherit'
            }}
            onMouseOver={e => e.currentTarget.style.background = '#D4603A'}
            onMouseOut={e => e.currentTarget.style.background = '#B5451B'}
          >
            Accept & Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConsentBanner;