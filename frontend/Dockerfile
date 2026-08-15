FROM node:22-alpine

RUN corepack enable

WORKDIR /app

ENV CI=true

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN pnpm install --frozen-lockfile --ignore-scripts

COPY . .

EXPOSE 5173

CMD ["pnpm", "dev", "--", "--host", "0.0.0.0"]