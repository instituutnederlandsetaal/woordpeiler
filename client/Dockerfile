FROM node:24.4.1-bookworm-slim AS build
COPY . .
RUN npm ci && npm run build && mv /dist/*.* /dist/assets && mv /dist/assets/index.html /dist/assets/robots.txt /dist/

FROM nginx:1.28.0-alpine3.21-slim
COPY --from=build /dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
