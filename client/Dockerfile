# syntax=docker/dockerfile:1

# Build stage
FROM node:25.8.2-alpine3.23 AS build
# Cache dependencies
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    --mount=type=bind,source=package.json,target=package.json \
    npm ci
COPY --link . .
RUN npx vite build && mv /dist/*.* /dist/assets && mv /dist/assets/index.html /dist/assets/robots.txt /dist/

# Server stage
FROM nginx:1.29.7-alpine3.23-slim
COPY --link nginx.conf /etc/nginx/nginx.conf
COPY --link --from=build /dist /usr/share/nginx/html
