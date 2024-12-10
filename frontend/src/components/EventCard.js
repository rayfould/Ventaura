// src/components/EventCard.jsx
import React, { useState } from 'react';
import eventCardStyles from '../styles/modules/EventCard.module.css';
import eventIcons from '../assets/icons/eventIcons';
import Other from '../assets/icons/Other.png';
import Modal from './Modal'; // Import the Modal component
import modalStyles from '../styles/modules/Modal.module.css';

const EventCard = ({ event }) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false); // State for modal

  // Formatting functions (same as before)
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const options = { 
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
  };

  const formatEvent = (eventString) => {
    if (!eventString || eventString == "event")  return "N/A";
    return eventString;
  }

  const formatPrice = (amount, currencyCode) => {
    // Return "Free" if no amount or currency code
    if (!amount || !currencyCode) return "Free";
    
    // Currency symbol mapping
    const currencySymbols = {
        USD: '$',    // US Dollar
        EUR: '€',    // Euro
        GBP: '£',    // British Pound
        JPY: '¥',    // Japanese Yen
        AUD: 'A$',   // Australian Dollar
        CAD: 'C$',   // Canadian Dollar
        CHF: 'Fr',   // Swiss Franc
        CNY: '¥',    // Chinese Yuan
        NZD: 'NZ$',  // New Zealand Dollar
        INR: '₹',    // Indian Rupee
        BRL: 'R$',   // Brazilian Real
        ZAR: 'R',    // South African Rand
        SEK: 'kr',   // Swedish Krona
        NOK: 'kr',   // Norwegian Krone
        DKK: 'kr',   // Danish Krone
        RUB: '₽',    // Russian Ruble
        MXN: '$',    // Mexican Peso
        SGD: 'S$',   // Singapore Dollar
        HKD: 'HK$'   // Hong Kong Dollar
    };

    // Format the amount with 2 decimal places if needed
    const formattedAmount = Number(amount).toFixed(2).replace(/\.00$/, '');

    // Get currency symbol or use currency code if not mapped
    const symbol = currencySymbols[currencyCode.toUpperCase()] || currencyCode;

    // Format based on currency position (most currencies are prefix)
    switch(currencyCode.toUpperCase()) {
        // Currencies that commonly appear after the amount
        case 'SEK':
        case 'NOK':
        case 'DKK':
            return `${formattedAmount} ${symbol}`;
            
        // Special formatting for specific currencies
        case 'EUR':
            return `${symbol}${formattedAmount}`;
            
        // Default format (symbol before amount)
        default:
            return `${symbol}${formattedAmount}`;
    }
  };


  const truncateTitle = (title = '') => {
    const maxLength = 30;
    if (!title || title.length <= maxLength) return title || 'Untitled Event';
    return `${title.substring(0, maxLength)}...`;
  };

  const formatDistance = (distance) => {
    if (!distance) return "N/A";
    const distanceNum = Number(distance);
    if (isNaN(distanceNum)) return "N/A";
    return `${distanceNum.toFixed(2)} km`;
  };

  const getIcon = (type) => {
    return eventIcons[type] || Other;
  };

  // Handle modal open
  const handleModalOpen = (e) => {
    e.stopPropagation(); // Prevent card flip
    setIsModalOpen(true);
  };

  // Handle modal close
  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <div 
        className={`${eventCardStyles.eventCard} ${isFlipped ? eventCardStyles.flipped : ''}`} 
        onClick={() => setIsFlipped(!isFlipped)}
        role="button"
        tabIndex={0}
        onKeyPress={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            setIsFlipped(!isFlipped);
          }
        }}
      >
        <div className={eventCardStyles.cardContent}>
          {/* Front Face */}
          <div className={eventCardStyles.cardFront}>
            <div className={eventCardStyles.imageContainer}>
              <img 
                src={getIcon(event.type)} 
                alt={`${event.type} icon`} 
                className={eventCardStyles.eventIcon} 
              />
            </div>
            <div className={eventCardStyles.titleContainer}>
              <h3 className={eventCardStyles.title}>{truncateTitle(event.title)}</h3>
            </div>
          </div>

          {/* Back Face */}
          <div className={eventCardStyles.cardBack}>
            <div className={eventCardStyles.details}>
              <p><strong>Type:</strong> {event.type}</p>
              <p><strong>Date:</strong> {formatDate(event.start)}</p>
              <p><strong>Distance:</strong> {formatDistance(event.distance)}</p>
              <p><strong>Price:</strong> {formatPrice(event.amount, event.currencyCode)}</p>
              <button 
                className={eventCardStyles.moreInfoButton}
                onClick={handleModalOpen}
              >
                More Info
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal Implementation */}
      <Modal isOpen={isModalOpen} onClose={handleModalClose}>
        <h2 id="modal-heading">{event.title || 'Untitled Event'}</h2>
        <p><strong>Description:</strong> {formatEvent(event.description)}</p>
        <p><strong>Type:</strong> {event.type || 'N/A'}</p>
        <p><strong>Date:</strong> {formatDate(event.start)}</p>
        <p><strong>Distance:</strong> {formatDistance(event.distance)}</p>
        <p><strong>Location:</strong> {event.location || 'N/A'}</p>
        <p><strong>Price:</strong> {formatPrice(event.amount, event.currencyCode)}</p>
        <p>
          <strong>Source:</strong> <a href={event.url} target="_blank" rel="noopener noreferrer">View Source</a>
        </p>
        <div className={modalStyles.footer}>
          <button className={modalStyles.actionButton} onClick={handleModalClose}>
            Close
          </button>
        </div>
      </Modal>
    </>
  );
};

export default EventCard;
