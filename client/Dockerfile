FROM node:24.7.0-alpine3.22 AS build
COPY . .
RUN npm ci && npm run build && mv /dist/*.* /dist/assets && mv /dist/assets/index.html /dist/assets/robots.txt /dist/

FROM nginx:1.29.1-alpine3.22-slim
COPY --from=build /dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
