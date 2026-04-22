FROM node:20-alpine AS build
WORKDIR /app


RUN npm config set registry https://npm.devneeds.ir/ --save

COPY package.json package-lock.json ./
RUN npm ci

COPY . .


RUN VITE_API_URL=BACKEND_URL_PLACEHOLDER npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /app/scripts/entrypoint.sh /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh", "BACKEND_URL_PLACEHOLDER"]
CMD ["nginx", "-g", "daemon off;"]
