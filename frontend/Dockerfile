# Frontend Dockerfile — Node 20
# Issue: D-01
FROM node:20-alpine

WORKDIR /app

# Install curl for healthcheck probe
RUN apk add --no-cache curl

# Install npm dependencies first to maximise layer cache hits
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
