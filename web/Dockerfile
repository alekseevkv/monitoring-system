FROM node:24-alpine
RUN npm install -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install
COPY . .
EXPOSE 5173
ENV HOST=0.0.0.0
CMD ["pnpm", "run", "dev"]