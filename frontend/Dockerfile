FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with force for beta versions
RUN npm install --force --legacy-peer-deps

# Copy source code
COPY . .

# Debug: Check if vite is installed
RUN npx vite --version

# Build the application
RUN npm run build

# Debug: Check build output
RUN ls -la && ls -la dist/ || echo "Checking for other build folders..." && find . -name "*.html" -type f

FROM nginx:alpine

# Try to copy from dist or build folder
COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]