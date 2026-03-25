import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default icon issue with webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const getDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Radius of the earth in km
  const dLat = deg2rad(lat2 - lat1);
  const dLon = deg2rad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const d = R * c; // Distance in km
  return d.toFixed(2);
}

const deg2rad = (deg) => {
  return deg * (Math.PI / 180);
}


const LocationResult = ({ data, userLocation }) => {
  const { name, city, history, latitude, longitude } = data;
  const position = [latitude, longitude];
  const mapCenter = userLocation ? [userLocation.latitude, userLocation.longitude] : position;
  const distance = userLocation ? getDistance(userLocation.latitude, userLocation.longitude, latitude, longitude) : null;

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h5" component="div">
          {name}
        </Typography>
        <Typography sx={{ mb: 1.5 }} color="text.secondary">
          {city}
        </Typography>
        {distance && (
          <Typography variant="body2" sx={{ mb: 1 }}>
            Distance from you: {distance} km
          </Typography>
        )}
        <Typography variant="body2" sx={{ mb: 2 }}>
          {history}
        </Typography>
        {latitude && longitude && (
          <MapContainer center={mapCenter} zoom={13} scrollWheelZoom={false}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker position={position}>
              <Popup>{name}</Popup>
            </Marker>
            {userLocation && (
              <CircleMarker
                center={[userLocation.latitude, userLocation.longitude]}
                pathOptions={{ color: 'blue' }}
                radius={8}>
                <Popup>Your Location</Popup>
              </CircleMarker>
            )}
          </MapContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default LocationResult;
