# Multi-stage build for React frontend

# Stage 1: Build the React application
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies fresh (without package-lock.json for clean resolution)
# Using npm install to generate fresh lockfile
RUN npm install --silent --legacy-peer-deps

# Install ajv explicitly to fix module resolution
RUN npm install ajv@^8.12.0 --save --silent --legacy-peer-deps

# Copy source code
COPY . .

# Build arguments for environment variables (injected at build time)
ARG REACT_APP_API_URL
ARG REACT_APP_RANKING_URL

# Set environment variables for build
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_RANKING_URL=$REACT_APP_RANKING_URL

# Build the React app for production
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 3000
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

