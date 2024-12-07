// EventCard.js
import React from 'react';

// Import specific CSS modules
import eventCardStyles from '../styles/modules/EventCard.module.css';
import layoutStyles from '../styles/layout.module.css';

const EventCard = ({ event }) => {
  // Format date to short format
  const formatDate = (dateString) => {
    if (!dateString) return "NULL";
    const options = { 
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
  };

  // Format price
  const formatPrice = (amount, currencyCode) => {
    if (!amount || !currencyCode) return "NULL";
    return `$${amount}`;
  };

  // Format distance
  const formatDistance = (distance) => {
    if (!distance) return "NULL";
    // Convert string to number and check if it's valid
    const distanceNum = Number(distance);
    if (isNaN(distanceNum)) return "NULL";
    return `${distanceNum.toFixed(2)} km`;
  };

  // Handle click event
  const handleClick = () => {
    if (event.url) {
      window.open(event.url, '_blank', 'noopener,noreferrer');
    }
  }; 

  // Add conditional classes based on event type
  const cardClasses = `${eventCardStyles.eventCard} ${event.type ? eventCardStyles[`type${event.type.replace(/[^a-zA-Z0-9]/g, '')}`] : ''}`;

  return (
    <div className={cardClasses} onClick={handleClick}>
      <div className={eventCardStyles.cardContent}>
        <div className={eventCardStyles.cardFront}>
          <div className={eventCardStyles.typeIcon}>
            {/* Icon based on event type */}
            {event.typeIcon || '🎟️'}
          </div>
          <h3 className={layoutStyles.heading}>{event.title}</h3>
          <div className={eventCardStyles.details}>
            <p className={eventCardStyles.date}>{formatDate(event.start)}</p>
            <p className={eventCardStyles.distance}>{formatDistance(event.distance)}</p>
          </div>
        </div>
        <div className={eventCardStyles.cardBack}>
          {/* Additional details */}
          <p className={eventCardStyles.description}>{event.description || "No description available."}</p>
          <p className={eventCardStyles.price}>
            {formatPrice(event.amount, event.currencyCode)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default EventCard;
