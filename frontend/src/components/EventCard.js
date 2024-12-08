// EventCard.jsx
import React, { useState } from 'react';
import eventCardStyles from '../styles/modules/EventCard.module.css';

const EventCard = ({ event }) => {
  const [isFlipped, setIsFlipped] = useState(false);

  // Formatting functions
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

  const formatPrice = (amount, currencyCode) => {
    if (!amount || !currencyCode) return "Free";
    return `${currencyCode}${amount}`;
  };

  const formatDistance = (distance) => {
    if (!distance) return "N/A";
    const distanceNum = Number(distance);
    if (isNaN(distanceNum)) return "N/A";
    return `${distanceNum.toFixed(2)} km`;
  };

  return (
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
          <h3 className={eventCardStyles.title}>{event.title}</h3>
          {/* Hover Hint */}
          <div className={eventCardStyles.hoverHint}></div>
        </div>

        {/* Back Face */}
        <div className={eventCardStyles.cardBack}>
        <p className={eventCardStyles.description}>{event.description}</p>
          <div className={eventCardStyles.details}>
            <p><strong>Type:</strong> {event.type}</p>
            <p><strong>Date:</strong> {formatDate(event.start)}</p>
            <p><strong>Distance:</strong> {formatDistance(event.distance)}</p>
            <p><strong>Price:</strong> {formatPrice(event.amount, event.currencyCode)}</p>
            <a 
              href={event.url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className={eventCardStyles.link}
              onClick={(e) => e.stopPropagation()}
            >
              More Info
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventCard;
