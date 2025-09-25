# Stage 1: Build
FROM node:20 AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy dependencies first (to cache installs)
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# Copy app source
COPY . .

# Build Next.js app
RUN pnpm build

# Stage 2: Production image
FROM node:20 AS runner

WORKDIR /app

RUN npm install -g pnpm

# Copy only necessary files
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/pnpm-lock.yaml ./pnpm-lock.yaml
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["pnpm", "start"]
