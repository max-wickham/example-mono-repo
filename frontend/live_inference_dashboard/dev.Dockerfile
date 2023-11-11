# FROM node:alpine
# WORKDIR /app
# COPY ./ /app/
# RUN npm install
# RUN npm uninstall react-scripts
# RUN apk update && apk add bash
# # SHELL [ "bash" ]
# # CMD ["npm", "run","generate-client","&&", "npm", "run", "start", "devlopment"]
# RUN npm install -D react-scripts
# # RUN chmod +x start.sh
# CMD ["npm","start"]
FROM node:alpine
WORKDIR /app
COPY ./ /app/
RUN npm install
RUN apk update && apk add bash
RUN npm uninstall react-scripts
RUN npm install -D react-scripts
CMD ["npm","start"]
