// src/components/Modal.jsx
import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import modalStyles from '../styles/modules/Modal.module.css';

const backdropVariants = {
  visible: { opacity: 1 },
  hidden: { opacity: 0 }
};

const modalVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { type: 'spring', stiffness: 300, damping: 20 }
  },
  exit: { opacity: 0, scale: 0.8, transition: { duration: 0.2 } }
};

const Modal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Shift focus to the modal
      modalRef.current.focus();
    } else {
      document.removeEventListener('keydown', handleEscape);
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          className={modalStyles.overlay} 
          onClick={handleOverlayClick}
          variants={backdropVariants}
          initial="hidden"
          animate="visible"
          exit="hidden"
        >
          <motion.div 
            className={modalStyles.modal}
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            ref={modalRef}
            tabIndex="-1"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-heading"
          >
            <button 
              className={modalStyles.closeButton} 
              onClick={onClose}
              aria-label="Close Modal"
            >
              &times;
            </button>
            <div className={modalStyles.content}>
              {children}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Modal;
