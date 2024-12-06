// EventCard.js
import React from 'react';
import styles from '../styles';

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
  const cardClasses = `${styles.eventCard} ${event.type ? styles[`type${event.type}`] : ''}`;

  return (
    <div className={cardClasses} onClick={handleClick}>
      <div className={styles.cardContent}>
        <div className={styles.cardFront}>
          <div className={styles.typeIcon}>
            {/* Icon based on event type */}
          </div>
          <h3 className={styles.title}>{event.title}</h3>
          <div className={styles.details}>
            <p className={styles.date}>{formatDate(event.start)}</p>
            <p className={styles.distance}>{formatDistance(event.distance)}</p>
          </div>
        </div>
        <div className={styles.cardBack}>
          {/* Additional details */}
          <p className={styles.description}>{event.description}</p>
          <p className={styles.price}>
            {formatPrice(event.amount, event.currencyCode)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default EventCard;