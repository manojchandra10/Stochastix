#Build the React App
FROM node:20-alpine as builder

WORKDIR /app

# Install dependencies (better caching)
COPY package.json package-lock.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Serve with Nginx
FROM nginx:alpine

# Copy built React app from builder stage to Nginx's html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 (Standard Web Port)
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]