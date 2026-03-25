import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Chip,
  Grid
} from '@mui/material';

const YoloDetection = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const fileInputRef = useRef(null);

  // Load model info on component mount
  React.useEffect(() => {
    fetchModelInfo();
  }, []);

  const fetchModelInfo = async () => {
    try {
      const response = await fetch('http://localhost:8000/model-info');
      if (response.ok) {
        const info = await response.json();
        setModelInfo(info);
      }
    } catch (err) {
      console.error('Failed to fetch model info:', err);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResults(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDetection = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:8000/detect', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(`Detection failed: ${err.message}`);
      console.error('Detection error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
    setResults(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        🏺 Ceramic Products Detection
      </Typography>
      
      <Typography variant="subtitle1" align="center" color="text.secondary" sx={{ mb: 4 }}>
        Upload an image to detect ceramic products using our trained YOLO model
      </Typography>

      {/* Model Info */}
      {modelInfo && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: '#f5f5f5' }}>
          <Typography variant="h6" gutterBottom>
            ℹ️ Model Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2">
                <strong>Model Type:</strong> {modelInfo.model_type}
              </Typography>
              <Typography variant="body2">
                <strong>Classes:</strong> {modelInfo.total_classes}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2">
                <strong>Input Size:</strong> {modelInfo.input_size}px
              </Typography>
              <Typography variant="body2">
                <strong>Framework:</strong> {modelInfo.framework}
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

      <Grid container spacing={3}>
        {/* Upload Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 'fit-content' }}>
            <Typography variant="h6" gutterBottom>
              📤 Upload Image
            </Typography>
            
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              ref={fileInputRef}
            />
            
            <Button
              variant="outlined"
              fullWidth
              onClick={() => fileInputRef.current?.click()}
              sx={{ mb: 2, py: 2 }}
            >
              📷 Choose Image
            </Button>

            {preview && (
              <Box sx={{ mb: 2 }}>
                <img
                  src={preview}
                  alt="Preview"
                  style={{
                    width: '100%',
                    maxHeight: '300px',
                    objectFit: 'contain',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              </Box>
            )}

            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="contained"
                onClick={handleDetection}
                disabled={!selectedFile || loading}
                sx={{ flex: 1 }}
              >
                {loading ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    Detecting...
                  </>
                ) : (
                  '👁️ Detect Objects'
                )}
              </Button>
              
              <Button
                variant="outlined"
                onClick={handleClear}
                disabled={loading}
              >
                Clear
              </Button>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              ✅ Detection Results
            </Typography>

            {!results && !loading && (
              <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
                Upload an image and click "Detect Objects" to see results
              </Typography>
            )}

            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            )}

            {results && (
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Found {results.total_detections} object(s)
                </Typography>

                {results.detections.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    {results.detections.map((detection, index) => (
                      <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          ✅ {detection.class_name}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            label={`${(detection.confidence * 100).toFixed(1)}%`}
                            size="small"
                            color={getConfidenceColor(detection.confidence)}
                          />
                          <Typography variant="caption" color="text.secondary">
                            Size: {detection.bbox.width}×{detection.bbox.height}px
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                )}

                {results.annotated_image && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Annotated Image:
                    </Typography>
                    <img
                      src={results.annotated_image}
                      alt="Detection Results"
                      style={{
                        width: '100%',
                        maxHeight: '400px',
                        objectFit: 'contain',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </Box>
                )}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Available Classes */}
      {modelInfo && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            🎯 Detectable Objects
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {modelInfo.classes.map((className, index) => (
              <Chip
                key={index}
                label={className}
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default YoloDetection;