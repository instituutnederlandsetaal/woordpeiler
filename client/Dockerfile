FROM node:25.2.1-alpine3.23 AS build
# Cache dependencies
COPY --link package.json package-lock.json ./
RUN npm ci
# Build source
COPY --link . .
RUN npm run build && mv /dist/*.* /dist/assets && mv /dist/assets/index.html /dist/assets/robots.txt /dist/

FROM nginx:1.29.4-alpine3.23-slim
COPY --from=build /dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
