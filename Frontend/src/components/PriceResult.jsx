import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress } from '@mui/material';

const PriceResult = ({ data }) => {
  const { product_name, price_range, confidence_score } = data;

  const confidenceValue = parseFloat(confidence_score);

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h5" component="div">
          {product_name}
        </Typography>
        <Typography sx={{ mt: 2, fontSize: '1.2rem' }} color="text.primary">
          Fair Price Range:
          <Typography component="span" sx={{ fontWeight: 'bold', ml: 1 }}>
            {price_range} MAD
          </Typography>
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Confidence Score
          </Typography>
          <LinearProgress
            variant="determinate"
            value={confidenceValue}
            sx={{ height: 10, borderRadius: 5, mt: 0.5 }}
          />
          <Typography variant="body2" align="right">
            {confidence_score}%
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PriceResult;
