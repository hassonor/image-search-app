import React, { useEffect } from 'react';
import { Modal, Box, IconButton, Fade, Backdrop } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

interface ImageModalProps {
  open: boolean;
  imageUrl: string | null;
  onClose: () => void;
  onNext?: () => void;
  onPrevious?: () => void;
  showNextPrev?: boolean;
}

const ImageModal: React.FC<ImageModalProps> = ({ open, imageUrl, onClose, onNext, onPrevious, showNextPrev }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowRight' && onNext) onNext();
      if (e.key === 'ArrowLeft' && onPrevious) onPrevious();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose, onNext, onPrevious]);

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="enlarged-image-modal"
      aria-describedby="shows-the-selected-image-in-larger-view"
      closeAfterTransition
      BackdropComponent={Backdrop}
      BackdropProps={{
        timeout: 500,
        style: { backgroundColor: 'rgba(0,0,0,0.8)' }
      }}
    >
      <Fade in={open}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          sx={{
            width: '100vw',
            height: '100vh',
            outline: 'none'
          }}
        >
          <Box
            sx={{
              position: 'relative',
              bgcolor: 'background.paper',
              p: 2,
              borderRadius: 2,
              maxWidth: '90%',
              maxHeight: '90%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <IconButton
              onClick={onClose}
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                zIndex: 2
              }}
              aria-label="close image modal"
            >
              <CloseIcon />
            </IconButton>

            {showNextPrev && onPrevious && (
              <IconButton
                onClick={onPrevious}
                sx={{
                  position: 'absolute',
                  left: 8,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  zIndex: 2
                }}
                aria-label="previous image"
              >
                <ChevronLeftIcon fontSize="large" />
              </IconButton>
            )}

            {showNextPrev && onNext && (
              <IconButton
                onClick={onNext}
                sx={{
                  position: 'absolute',
                  right: 8,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  zIndex: 2
                }}
                aria-label="next image"
              >
                <ChevronRightIcon fontSize="large" />
              </IconButton>
            )}

            {imageUrl && (
              <img
                src={imageUrl}
                alt="Enlarged View"
                style={{ maxWidth: '100%', maxHeight: '80vh', borderRadius: '4px' }}
              />
            )}
          </Box>
        </Box>
      </Fade>
    </Modal>
  );
};

export default ImageModal;
