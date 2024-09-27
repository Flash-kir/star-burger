FROM node:16-alpine
RUN npm install -g nodemon
WORKDIR /star-burger
COPY ./package.json .
COPY ./package-lock.json .
#RUN npm install --save core-js@3
RUN npm install
RUN npm ci --dev
COPY ./bundles-src ./bundles-src
