FROM node:24.2.0-bookworm-slim AS build
COPY . .
RUN npm ci && npm run build

FROM nginx:1.28.0-alpine3.21-slim
COPY --from=build /dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
