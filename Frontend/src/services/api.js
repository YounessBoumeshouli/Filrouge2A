import axios from 'axios';

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
});

// Auth functions - Mock implementation for demo
export const login = (email, password) => {
  console.log('Mock login called with:', { email, password });
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: {
          access_token: 'mock_token_' + Math.random().toString(36).substr(2, 9),
          user: {
            id: 1,
            email: email,
            name: 'Demo User'
          }
        }
      });
    }, 500);
  });
};

export const register = (username, email, password) => {
  console.log('Mock register called with:', { username, email, password });
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: {
          access_token: 'mock_token_' + Math.random().toString(36).substr(2, 9),
          user: {
            id: 1,
            email: email,
            name: username
          }
        }
      });
    }, 500);
  });
};

// Mock functions to simulate API calls
export const analyzeLocation = (imageData, userLocation) => {
  console.log('Mock analyzeLocation called with:', { imageData, userLocation });
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: {
          name: 'Hassan II Mosque',
          city: 'Casablanca',
          history: 'The Hassan II Mosque is a mosque in Casablanca, Morocco. It is the second largest functioning mosque in Africa and is the 7th largest in the world. Its minaret is the world\'s second tallest minaret at 210 metres.',
          latitude: 33.608,
          longitude: -7.632,
        },
      });
    }, 1000);
  });
};

export const getNearbyAttractions = (lat, lon) => {
  console.log('Mock getNearbyAttractions called with:', { lat, lon });
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: [
          { name: 'Old Medina of Casablanca', latitude: 33.59, longitude: -7.61 },
          { name: 'Rick\'s Café', latitude: 33.60, longitude: -7.62 },
        ],
      });
    }, 1000);
  });
};

export const analyzePrice = async (imageData) => {
  try {
    // Convert image data to base64 if it's a data URL
    let base64Image = imageData;
    if (imageData.startsWith('data:image/')) {
      base64Image = imageData.split(',')[1];
    }
    
    const response = await API.post('/detect', {
      image: base64Image
    });
    
    return response;
  } catch (error) {
    console.error('Price analysis error:', error);
    // Fallback to mock data if API fails
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: {
            success: true,
            product_type: 'leather',
            confidence: 0.85,
            all_predictions: {
              leather: 0.85,
              textiles: 0.10,
              crafts: 0.05
            }
          }
        });
      }, 1000);
    });
  }
};
