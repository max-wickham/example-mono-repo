FROM node:alpine
WORKDIR /app
COPY ./ /app/
RUN npm install
RUN npm install react-scripts
RUN apk update && apk add bash
# SHELL [ "bash" ]
# CMD ["npm", "run","generate-client","&&", "npm", "run", "start", "devlopment"]
RUN npm install --save react react-dom react-scripts
# RUN chmod +x start.sh
CMD ["npm","start"]
