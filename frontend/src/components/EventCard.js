// EventCard.jsx
import React, { useState } from 'react';
import eventCardStyles from '../styles/modules/EventCard.module.css';
import eventIcons from '../assets/icons/eventIcons';
import Other from '../assets/icons/Other.png'; // Import the fallback icon (optional, if not included in eventIcons)
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
    // Normalize the type string to match the keys in eventIcons
    return eventIcons[type] || Other;
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
