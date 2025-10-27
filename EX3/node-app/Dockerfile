FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY server.js ./
RUN apk add --no-cache curl
EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s \
    CMD curl -f http://localhost:3000/api/health || exit 1
CMD ["node", "server.js"]
