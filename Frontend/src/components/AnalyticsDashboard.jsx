import React, { useState, useEffect } from 'react';
import trackingService from '../services/tracking';

const AnalyticsDashboard = () => {
  const [journeyData, setJourneyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadJourneyData();
  }, []);

  const loadJourneyData = async () => {
    try {
      setLoading(true);
      const data = await trackingService.getUserJourney();
      setJourneyData(data);
    } catch (err) {
      setError('Failed to load journey data');
      console.error('Journey data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatRating = (rating) => {
    if (!rating) return 'N/A';
    return `${rating.toFixed(1)} ⭐`;
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '400px',
        background: '#F5F0E8',
        borderRadius: '12px',
        margin: '20px'
      }}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid rgba(181,69,27,0.2)',
            borderTopColor: '#B5451B',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ color: '#5C5549', fontSize: '0.9rem' }}>Loading your journey data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        background: '#FEF2F2',
        border: '1px solid rgba(239,68,68,0.2)',
        borderRadius: '12px',
        padding: '24px',
        margin: '20px',
        textAlign: 'center'
      }}>
        <p style={{ color: '#DC2626', fontSize: '0.9rem', marginBottom: '12px' }}>⚠️ {error}</p>
        <button
          onClick={loadJourneyData}
          style={{
            background: '#DC2626',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            fontSize: '0.8rem',
            cursor: 'pointer'
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!journeyData) {
    return (
      <div style={{
        background: '#F5F0E8',
        borderRadius: '12px',
        padding: '40px',
        margin: '20px',
        textAlign: 'center'
      }}>
        <p style={{ color: '#5C5549', fontSize: '0.9rem' }}>No journey data available</p>
      </div>
    );
  }

  return (
    <div style={{
      background: '#F5F0E8',
      minHeight: '100vh',
      padding: '20px',
      fontFamily: "'Jost', sans-serif"
    }}>
      {/* Header */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '24px 32px',
        marginBottom: '24px',
        border: '1px solid rgba(28,26,23,0.09)'
      }}>
        <h1 style={{
          fontFamily: "'Cormorant Garamond', serif",
          fontSize: '2.2rem',
          fontWeight: 300,
          color: '#1C1A17',
          marginBottom: '8px'
        }}>
          Your Marrakech Journey 🧭
        </h1>
        <p style={{
          color: '#5C5549',
          fontSize: '0.9rem',
          lineHeight: 1.6
        }}>
          Track your exploration of the souks and monuments. Your data helps us provide better recommendations.
        </p>
      </div>

      {/* Stats Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '24px'
      }}>
        {/* Total Activity */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid rgba(28,26,23,0.09)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            background: 'rgba(181,69,27,0.1)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            fontSize: '1.5rem'
          }}>
            📊
          </div>
          <h3 style={{
            fontSize: '2rem',
            fontWeight: 300,
            color: '#B5451B',
            marginBottom: '4px',
            fontFamily: "'Cormorant Garamond', serif"
          }}>
            {journeyData.total_scans}
          </h3>
          <p style={{ color: '#5C5549', fontSize: '0.85rem' }}>Total Scans</p>
        </div>

        {/* Sessions */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid rgba(28,26,23,0.09)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            background: 'rgba(34,197,94,0.1)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            fontSize: '1.5rem'
          }}>
            🔄
          </div>
          <h3 style={{
            fontSize: '2rem',
            fontWeight: 300,
            color: '#16A34A',
            marginBottom: '4px',
            fontFamily: "'Cormorant Garamond', serif"
          }}>
            {journeyData.total_sessions}
          </h3>
          <p style={{ color: '#5C5549', fontSize: '0.85rem' }}>Sessions</p>
        </div>

        {/* Location Scans */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid rgba(28,26,23,0.09)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            background: 'rgba(59,130,246,0.1)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            fontSize: '1.5rem'
          }}>
            📍
          </div>
          <h3 style={{
            fontSize: '2rem',
            fontWeight: 300,
            color: '#3B82F6',
            marginBottom: '4px',
            fontFamily: "'Cormorant Garamond', serif"
          }}>
            {journeyData.location_scans_count}
          </h3>
          <p style={{ color: '#5C5549', fontSize: '0.85rem' }}>Places Visited</p>
        </div>

        {/* Price Scans */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid rgba(28,26,23,0.09)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            background: 'rgba(245,158,11,0.1)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            fontSize: '1.5rem'
          }}>
            💰
          </div>
          <h3 style={{
            fontSize: '2rem',
            fontWeight: 300,
            color: '#F59E0B',
            marginBottom: '4px',
            fontFamily: "'Cormorant Garamond', serif"
          }}>
            {journeyData.price_scans_count}
          </h3>
          <p style={{ color: '#5C5549', fontSize: '0.85rem' }}>Price Checks</p>
        </div>
      </div>

      {/* Detailed Info */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '24px',
        marginBottom: '24px'
      }}>
        {/* User Profile */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid rgba(28,26,23,0.09)'
        }}>
          <h3 style={{
            fontSize: '1.2rem',
            fontWeight: 500,
            color: '#1C1A17',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            👤 Profile Information
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#5C5549', fontSize: '0.85rem' }}>User ID:</span>
              <span style={{ color: '#1C1A17', fontSize: '0.85rem', fontFamily: 'monospace' }}>
                {journeyData.user_id.slice(0, 8)}...
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#5C5549', fontSize: '0.85rem' }}>Traveler Type:</span>
              <span style={{ color: '#1C1A17', fontSize: '0.85rem', textTransform: 'capitalize' }}>
                {journeyData.traveler_type || 'Not specified'}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#5C5549', fontSize: '0.85rem' }}>Member Since:</span>
              <span style={{ color: '#1C1A17', fontSize: '0.85rem' }}>
                {formatDate(journeyData.created_at)}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#5C5549', fontSize: '0.85rem' }}>Last Active:</span>
              <span style={{ color: '#1C1A17', fontSize: '0.85rem' }}>
                {formatDate(journeyData.last_active)}
              </span>
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid rgba(28,26,23,0.09)'
        }}>
          <h3 style={{
            fontSize: '1.2rem',
            fontWeight: 500,
            color: '#1C1A17',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            ⭐ Your Preferences
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#5C5549', fontSize: '0.85rem' }}>Favorite Product:</span>
              <span style={{ color: '#1C1A17', fontSize: '0.85rem' }}>
                {journeyData.most_searched_product_category || 'None yet'}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#5C5549', fontSize: '0.85rem' }}>Favorite Place:</span>
              <span style={{ color: '#1C1A17', fontSize: '0.85rem' }}>
                {journeyData.most_visited_monument_type || 'None yet'}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#5C5549', fontSize: '0.85rem' }}>Avg Location Rating:</span>
              <span style={{ color: '#1C1A17', fontSize: '0.85rem' }}>
                {formatRating(journeyData.avg_location_rating)}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#5C5549', fontSize: '0.85rem' }}>Avg Price Rating:</span>
              <span style={{ color: '#1C1A17', fontSize: '0.85rem' }}>
                {formatRating(journeyData.avg_price_rating)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Privacy Notice */}
      <div style={{
        background: '#1C1A17',
        borderRadius: '12px',
        padding: '24px',
        color: 'white'
      }}>
        <h3 style={{
          fontSize: '1.1rem',
          fontWeight: 500,
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          🔒 Privacy & Data
        </h3>
        
        <p style={{
          color: 'rgba(255,255,255,0.8)',
          fontSize: '0.85rem',
          lineHeight: 1.6,
          marginBottom: '16px'
        }}>
          Your data is stored locally and used only to improve your experience. We never share your information with third parties.
        </p>
        
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={() => {
              if (confirm('Are you sure you want to clear all your data? This cannot be undone.')) {
                trackingService.clearUserData();
                window.location.reload();
              }
            }}
            style={{
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.3)',
              color: '#EF4444',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '0.8rem',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={e => {
              e.currentTarget.style.background = 'rgba(239,68,68,0.2)';
            }}
            onMouseOut={e => {
              e.currentTarget.style.background = 'rgba(239,68,68,0.1)';
            }}
          >
            Clear All Data
          </button>
          
          <button
            onClick={loadJourneyData}
            style={{
              background: '#B5451B',
              border: 'none',
              color: 'white',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '0.8rem',
              cursor: 'pointer',
              transition: 'background 0.2s'
            }}
            onMouseOver={e => e.currentTarget.style.background = '#D4603A'}
            onMouseOut={e => e.currentTarget.style.background = '#B5451B'}
          >
            Refresh Data
          </button>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AnalyticsDashboard;