import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import Register from './pages/Register';
import Login from './pages/Login';
import Home from './pages/Home';
import ObjectDetection from './pages/ObjectDetection';
import LocationHelper  from './pages/LocationHelper';
import HotelHelper from './pages/HotelHelper';
import JourneyTracker from './components/JourneyTracker';
import ConsentBanner from './components/ConsentBanner';

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Tourist Helper
            </Typography>
            <Button color="inherit" component={Link} to="/">
              Home
            </Button>
            <Button color="inherit" component={Link} to="/price">
              Price Helper
            </Button>
            <Button color="inherit" component={Link} to="/location">
              Location Helper
            </Button>
            <Button color="inherit" component={Link} to="/journey">
              Journey Tracker
            </Button>
            <Button color="inherit" component={Link} to="/hotels">
              Hotels
            </Button>
            <Button color="inherit" component={Link} to="/login">
              Login
            </Button>
          </Toolbar>
        </AppBar>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/price" element={<ObjectDetection />} />
          <Route path="/location" element={<LocationHelper />} />
          <Route path="/journey" element={<JourneyTracker />} />
          <Route path="/hotels" element={<HotelHelper />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
        
        <ConsentBanner />
      </Box>
    </Router>
  );
}

export default App;