# Build stage
FROM node:21.6.2-alpine3.19 as build
COPY . .
RUN npm ci
# Builds to dist/
RUN npm run build

# Production stage.
FROM node:21.6.2-alpine3.19
WORKDIR /app
# Install dependencies of server.js
RUN npm install express connect-history-api-fallback && npm cache clean --force
# Copy over build & server.
COPY --from=build /dist ./dist
COPY . .

EXPOSE 8080
CMD [ "node", "server.js" ]
