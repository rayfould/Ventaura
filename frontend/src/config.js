// src/config.js
// API URLs are configured via environment variables at build time
// Default to HTTPS ventaura.co (reverse proxy handles routing)
export const API_BASE_URL = process.env.REACT_APP_API_URL || "https://ventaura.co";
export const RANKING_API_URL = process.env.REACT_APP_RANKING_URL || "https://ventaura.co";