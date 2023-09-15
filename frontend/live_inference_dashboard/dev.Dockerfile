FROM node:alpine
WORKDIR /app
COPY ./ /app/
RUN npm install
RUN apk update && apk add bash
# SHELL [ "bash" ]
# CMD ["npm", "run","generate-client","&&", "npm", "run", "start", "devlopment"]
RUN npm install openapi-typescript-codegen --save-dev
RUN chmod +x start.sh
CMD ["./start.sh"]
