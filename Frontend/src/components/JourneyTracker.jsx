import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  LinearProgress
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  LocationOn,
  Notifications,
  Close,
  Route,
  Timer,
  MyLocation
} from '@mui/icons-material';
import trackingService from '../services/tracking';

// Predefined tourist locations in Morocco (example data)
const TOURIST_LOCATIONS = [
  {
    id: 1,
    name: "Hassan II Mosque",
    latitude: 33.6084,
    longitude: -7.6324,
    city: "Casablanca",
    type: "mosque",
    description: "One of the largest mosques in the world"
  },
  {
    id: 2,
    name: "Jemaa el-Fnaa",
    latitude: 31.6260,
    longitude: -7.9890,
    city: "Marrakech",
    type: "square",
    description: "Famous market square and UNESCO World Heritage site"
  },
  {
    id: 3,
    name: "Koutoubia Mosque",
    latitude: 31.6236,
    longitude: -7.9993,
    city: "Marrakech",
    type: "mosque",
    description: "Iconic minaret and mosque in Marrakech"
  },
  {
    id: 4,
    name: "Majorelle Garden",
    latitude: 31.6417,
    longitude: -7.9930,
    city: "Marrakech",
    type: "garden",
    description: "Beautiful botanical garden designed by Jacques Majorelle"
  },
  {
    id: 5,
    name: "Chefchaouen Blue City",
    latitude: 35.1689,
    longitude: -5.2636,
    city: "Chefchaouen",
    type: "city",
    description: "Famous blue-painted city in the mountains"
  },
  {
    id: 6,
    name: "Ait Benhaddou",
    latitude: 31.0472,
    longitude: -7.1318,
    city: "Ouarzazate",
    type: "kasbah",
    description: "UNESCO World Heritage fortified village"
  }
];

const JourneyTracker = ({ destination, userPosition, onClose, onJourneyStart, onJourneyEnd, onJourneyUpdate, existingJourneyData }) => {
  const [isTracking, setIsTracking] = useState(false);
  const [currentPosition, setCurrentPosition] = useState(null);
  const [visitedLocations, setVisitedLocations] = useState([]);
  const [nearbyLocations, setNearbyLocations] = useState([]);
  const [journeyStartTime, setJourneyStartTime] = useState(null);
  const [journeyDuration, setJourneyDuration] = useState(0);
  const [notification, setNotification] = useState(null);
  const [permissionStatus, setPermissionStatus] = useState('prompt');
  const [error, setError] = useState(null);
  
  const watchIdRef = useRef(null);
  const journeyIdRef = useRef(null);
  const timerRef = useRef(null);

  // Request location permission
  const requestLocationPermission = async () => {
    try {
      if (!navigator.geolocation) {
        throw new Error('Geolocation is not supported by this browser');
      }

      const permission = await navigator.permissions.query({ name: 'geolocation' });
      setPermissionStatus(permission.state);
      
      if (permission.state === 'denied') {
        throw new Error('Location permission denied. Please enable location access in your browser settings.');
      }

      return permission.state === 'granted' || permission.state === 'prompt';
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  // Calculate distance between two coordinates (Haversine formula)
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; // Distance in kilometers
  };

  // Check for nearby tourist locations
  const checkNearbyLocations = (position) => {
    const nearby = [];
    const visited = [];

    TOURIST_LOCATIONS.forEach(location => {
      const distance = calculateDistance(
        position.latitude,
        position.longitude,
        location.latitude,
        location.longitude
      );

      if (distance <= 1.0) { // Within 1km
        nearby.push({ ...location, distance: distance.toFixed(2) });
        
        // Check if this is a new visit
        const alreadyVisited = visitedLocations.some(v => v.id === location.id);
        if (!alreadyVisited) {
          visited.push({ ...location, distance: distance.toFixed(2), timestamp: new Date() });
          showLocationNotification(location, distance);
          
          // Track the location visit
          trackingService.trackLocationScan(
            location.name,
            location.latitude,
            location.longitude,
            true, // was_guided = true for journey tracking
            null  // rating will be added later
          );
        }
      }
    });

    setNearbyLocations(nearby);
    
    if (visited.length > 0) {
      setVisitedLocations(prev => [...prev, ...visited]);
    }
  };

  // Show notification when near a location
  const showLocationNotification = (location, distance) => {
    const notification = {
      id: Date.now(),
      location,
      distance: distance.toFixed(2),
      timestamp: new Date()
    };
    
    setNotification(notification);

    // Browser notification if permission granted
    if (Notification.permission === 'granted') {
      new Notification(`📍 You're near ${location.name}!`, {
        body: `${location.description} - ${distance.toFixed(2)}km away`,
        icon: '/favicon.ico',
        tag: `location-${location.id}`
      });
    }

    // Auto-hide notification after 10 seconds
    setTimeout(() => {
      setNotification(null);
    }, 10000);
  };

  // Start journey tracking
  const startJourney = async () => {
    // Use provided userPosition if available, otherwise request permission
    if (!userPosition) {
      const hasPermission = await requestLocationPermission();
      if (!hasPermission) return;
    } else {
      // Use the provided position
      setCurrentPosition({
        latitude: userPosition.lat,
        longitude: userPosition.lng,
        accuracy: 10, // Assume good accuracy
        timestamp: new Date()
      });
    }

    // Request notification permission
    if (Notification.permission === 'default') {
      await Notification.requestPermission();
    }

    setIsTracking(true);
    setJourneyStartTime(new Date());
    setError(null);
    setVisitedLocations([]);
    setNearbyLocations([]);
    
    // Generate journey ID
    journeyIdRef.current = `journey_${Date.now()}`;

    // Start location tracking
    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 30000 // 30 seconds
    };

    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        const pos = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date(position.timestamp)
        };
        
        setCurrentPosition(pos);
        checkNearbyLocations(pos);
        
        // Log position for journey tracking
        console.log('📍 Position update:', pos);
      },
      (error) => {
        console.error('Location error:', error);
        setError(`Location error: ${error.message}`);
      },
      options
    );

    // Start duration timer
    timerRef.current = setInterval(() => {
      setJourneyDuration(prev => prev + 1);
    }, 1000);

    // Track journey start
    await trackingService.trackUserAction('journey_started', {
      journey_id: journeyIdRef.current,
      start_time: new Date().toISOString()
    });
    
    // Call callback to notify parent component
    if (onJourneyStart) {
      onJourneyStart({
        journeyId: journeyIdRef.current,
        startTime: new Date(),
        destination: destination?.name || 'Unknown'
      });
    }
  };

  // Stop journey tracking
  const stopJourney = async () => {
    setIsTracking(false);
    
    if (watchIdRef.current) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // Track journey end
    await trackingService.trackUserAction('journey_ended', {
      journey_id: journeyIdRef.current,
      end_time: new Date().toISOString(),
      duration_seconds: journeyDuration,
      locations_visited: visitedLocations.length,
      total_distance: 'calculated' // You could calculate total distance
    });
    
    // Call callback to notify parent component
    if (onJourneyEnd) {
      onJourneyEnd();
    }

    // Reset states
    setJourneyDuration(0);
    setJourneyStartTime(null);
    journeyIdRef.current = null;
  };

  // Format duration
  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  useEffect(() => {
    if (existingJourneyData && !isTracking) {
      setIsTracking(existingJourneyData.isActive || false);
      setJourneyDuration(existingJourneyData.durationSeconds || 0);
      setVisitedLocations(existingJourneyData.visitedLocations || []);
      setCurrentPosition(existingJourneyData.currentPosition || null);
      setJourneyStartTime(existingJourneyData.startTime || null);
      journeyIdRef.current = existingJourneyData.journeyId || null;
      
      if (existingJourneyData.isActive && !timerRef.current) {
        timerRef.current = setInterval(() => {
          setJourneyDuration(prev => prev + 1);
        }, 1000);
      }
    }
  }, [existingJourneyData]);

  useEffect(() => {
    if (isTracking && onJourneyUpdate) {
      const updateInterval = setInterval(() => {
        onJourneyUpdate({
          duration: formatDuration(journeyDuration),
          durationSeconds: journeyDuration,
          visitedCount: visitedLocations.length,
          visitedLocations: visitedLocations,
          isActive: isTracking,
          currentPosition: currentPosition,
          startTime: journeyStartTime,
          journeyId: journeyIdRef.current
        });
      }, 1000); // Update every second
      
      return () => clearInterval(updateInterval);
    }
  }, [isTracking, journeyDuration, visitedLocations.length, currentPosition, onJourneyUpdate]);

  // Auto-start journey if destination is provided (but not if journey already exists)
  useEffect(() => {
    if (destination && userPosition && !isTracking && !existingJourneyData?.isActive) {
      // Auto-start the journey only for new journeys
      setTimeout(() => {
        startJourney();
      }, 1000); // Small delay to let the component render
    }
  }, [destination, userPosition]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (watchIdRef.current) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header with destination info */}
      {destination && (
        <Box sx={{ mb: 3, p: 2, bgcolor: 'primary.main', color: 'white', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            🎯 Journey to: {destination.name}
          </Typography>
          <Typography variant="body2">
            Coordinates: {destination.lat.toFixed(4)}, {destination.lng.toFixed(4)}
          </Typography>
        </Box>
      )}
      
      <Typography variant="h4" gutterBottom>
        🗺️ Journey Tracker
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Journey Control */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              Journey Control
            </Typography>
            <Chip 
              label={isTracking ? 'Tracking Active' : 'Tracking Stopped'} 
              color={isTracking ? 'success' : 'default'}
              icon={isTracking ? <MyLocation /> : <Stop />}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayArrow />}
              onClick={startJourney}
              disabled={isTracking}
              size="large"
            >
              Start Road Journey
            </Button>
            
            <Button
              variant="outlined"
              color="secondary"
              startIcon={<Stop />}
              onClick={stopJourney}
              disabled={!isTracking}
              size="large"
            >
              Stop Journey
            </Button>
            
            {onClose && (
              <Button
                variant="outlined"
                onClick={onClose}
                size="large"
                sx={{ ml: 1 }}
              >
                Close Tracker
              </Button>
            )}
          </Box>

          {isTracking && (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <Timer />
                <Typography variant="body1">
                  Duration: {formatDuration(journeyDuration)}
                </Typography>
              </Box>
              
              {currentPosition && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <LocationOn />
                  <Typography variant="body2" color="text.secondary">
                    Current: {currentPosition.latitude.toFixed(6)}, {currentPosition.longitude.toFixed(6)}
                    (±{currentPosition.accuracy?.toFixed(0)}m)
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Nearby Locations */}
      {nearbyLocations.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📍 Nearby Tourist Locations (within 1km)
            </Typography>
            <List>
              {nearbyLocations.map((location) => (
                <ListItem key={location.id}>
                  <ListItemIcon>
                    <LocationOn color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={location.name}
                    secondary={`${location.description} - ${location.distance}km away`}
                  />
                  <Chip label={location.city} size="small" />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Visited Locations */}
      {visitedLocations.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              ✅ Visited Locations ({visitedLocations.length})
            </Typography>
            <List>
              {visitedLocations.map((location, index) => (
                <ListItem key={`${location.id}-${index}`}>
                  <ListItemIcon>
                    <Route color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary={location.name}
                    secondary={`Visited at ${location.timestamp.toLocaleTimeString()} - ${location.distance}km`}
                  />
                  <Chip label={location.type} size="small" color="success" />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Location Notification Dialog */}
      <Dialog
        open={!!notification}
        onClose={() => setNotification(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Notifications color="primary" />
            <Typography variant="h6">Location Detected!</Typography>
          </Box>
          <IconButton onClick={() => setNotification(null)}>
            <Close />
          </IconButton>
        </DialogTitle>
        
        {notification && (
          <DialogContent>
            <Typography variant="h6" gutterBottom>
              📍 {notification.location.name}
            </Typography>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              {notification.location.description}
            </Typography>
            <Typography variant="body2">
              📏 Distance: {notification.distance}km away
            </Typography>
            <Typography variant="body2">
              🏙️ City: {notification.location.city}
            </Typography>
            <Typography variant="body2">
              ⏰ Detected at: {notification.timestamp.toLocaleTimeString()}
            </Typography>
          </DialogContent>
        )}
        
        <DialogActions>
          <Button onClick={() => setNotification(null)} color="primary">
            Got it!
          </Button>
        </DialogActions>
      </Dialog>

      {/* Journey Progress */}
      {isTracking && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📊 Journey Progress
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Tracking since: {journeyStartTime?.toLocaleTimeString()}
              </Typography>
              <LinearProgress 
                variant="indeterminate" 
                sx={{ mt: 1, height: 6, borderRadius: 3 }}
              />
            </Box>
            <Box sx={{ display: 'flex', gap: 4 }}>
              <Box>
                <Typography variant="h4" color="primary">
                  {visitedLocations.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Locations Visited
                </Typography>
              </Box>
              <Box>
                <Typography variant="h4" color="secondary">
                  {nearbyLocations.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Nearby Locations
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default JourneyTracker;