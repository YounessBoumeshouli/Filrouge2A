import React, { useState, useRef } from 'react';
import { Button, Box, Typography, Paper } from '@mui/material';

const ImageUpload = ({ onImageUpload }) => {
  const [image, setImage] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result);
        onImageUpload(file);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  return (
    <Box sx={{ textAlign: 'center', mt: 2 }}>
      <input
        type="file"
        accept="image/*"
        capture="environment"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      <Button variant="contained" onClick={handleUploadClick}>
        Upload or Take Photo
      </Button>
      {image && (
        <Paper elevation={3} sx={{ mt: 2, p: 1, display: 'inline-block' }}>
          <img src={image} alt="Preview" style={{ maxWidth: '100%', height: 'auto', maxHeight: '300px' }} />
          <Typography variant="caption" display="block">
            Image Preview
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default ImageUpload;
