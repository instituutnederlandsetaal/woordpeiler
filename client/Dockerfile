# Build stage
FROM node:21.6.2-alpine3.19 as build
COPY . .
RUN npm install
CMD [ "npm run dev" ]