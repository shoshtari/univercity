FROM node:20-alpine AS build
WORKDIR /app

RUN npm config set registry https://npm.devneeds.ir/ --save

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
