# syntax=docker/dockerfile:1.4

# Build stage
FROM node:25.7.0-alpine3.23 AS build
# Cache dependencies
COPY --link package.json package-lock.json ./
RUN npm ci
# Build source
COPY --link . .
RUN npm run build && mv /dist/*.* /dist/assets && mv /dist/assets/index.html /dist/assets/robots.txt /dist/

# Server stage
FROM nginx:1.29.4-alpine3.23-slim
COPY --link nginx.conf /etc/nginx/nginx.conf
COPY --link --from=build /dist /usr/share/nginx/html
