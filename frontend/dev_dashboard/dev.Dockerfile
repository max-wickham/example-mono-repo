FROM node:alpine
WORKDIR /app
COPY ./ /app/
RUN npm install
SHELL [ "bash" ]
# CMD ["npm", "run","generate-client","&&", "npm", "run", "start", "devlopment"]
CMD ["npm", "run", "start", "devlopment"]
