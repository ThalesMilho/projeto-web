# Stage 1: Build the Next.js application
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package.json and yarn.lock/package-lock.json to leverage Docker layer caching
COPY package.json yarn.lock* ./
# If using npm, use package-lock.json instead of yarn.lock
# COPY package.json package-lock.json ./

RUN yarn install --frozen-lockfile
# If using npm:
# RUN npm ci

COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

RUN yarn build
# If using npm:
# RUN npm run build

# Stage 2: Create the production image
FROM node:22-alpine AS runner

WORKDIR /app

# Set correct permissions for Next.js cache directory
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

USER nextjs

EXPOSE 3000

CMD ["yarn", "start"]
# If using npm:
# CMD ["npm", "start"]