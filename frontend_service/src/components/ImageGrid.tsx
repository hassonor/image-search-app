import React, { useEffect, useState } from 'react';
import { fetchImages } from '../api/client';
import { Grid, Card, CardMedia, Typography } from '@mui/material';

import NoResults from './NoResults';
import ImageModal from "./ImageModel";

interface ImageItem {
  image_id: number;
  image_url: string;
  score: number;
}

interface ImageGridProps {
  query: string;
  page: number;
}

const ImageGrid: React.FC<ImageGridProps> = ({ query, page }) => {
  const [images, setImages] = useState<ImageItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  useEffect(() => {
    if (!query) return;
    setLoading(true);
    setError(null);
    fetchImages(query, page)
      .then((data) => {
        setImages(data.results);
        setSelectedIndex(null);
      })
      .catch((err) => {
        console.error('Failed to fetch images', err);
        setError('Failed to fetch images');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [query, page]);

  if (!query) {
    return <Typography>Enter a query to search for images.</Typography>;
  }

  if (loading) {
    return <Typography>Loading images...</Typography>;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  if (images.length === 0) {
    return <NoResults query={query} />;
  }

  const handleImageClick = (index: number) => {
    setSelectedIndex(index);
  };

  const handleClose = () => {
    setSelectedIndex(null);
  };

  const handleNext = () => {
    if (selectedIndex !== null && selectedIndex < images.length - 1) {
      setSelectedIndex(selectedIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (selectedIndex !== null && selectedIndex > 0) {
      setSelectedIndex(selectedIndex - 1);
    }
  };

  const selectedImageUrl = selectedIndex !== null ? images[selectedIndex].image_url : null;

  return (
    <>
      <Grid container spacing={2}>
        {images.map((img, idx) => (
          <Grid item key={img.image_id} xs={12} sm={6} md={4}>
            <Card
              style={{ cursor: 'pointer' }}
              onClick={() => handleImageClick(idx)}
            >
              <CardMedia
                component="img"
                image={img.image_url}
                alt={`Image ${img.image_id}`}
                style={{ maxHeight: '200px', objectFit: 'cover', borderRadius: '4px 4px 0 0' }}
              />
              <Typography variant="body2" style={{ padding: '8px' }}>
                Score: {img.score.toFixed(2)}
              </Typography>
            </Card>
          </Grid>
        ))}
      </Grid>

      <ImageModal 
        open={selectedIndex !== null}
        imageUrl={selectedImageUrl}
        onClose={handleClose}
        onNext={handleNext}
        onPrevious={handlePrevious}
        showNextPrev={true}
      />
    </>
  );
};

export default ImageGrid;
