# --- Etapa de build ---
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# --- Etapa de producción ---
FROM nginx:alpine

# Copiar build de Vite
COPY --from=build /app/dist /usr/share/nginx/html

# Configuración de nginx para SPA + proxy al backend
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location /api/ { \
        proxy_pass http://backend:8000/api/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
    location /uploads/ { \
        proxy_pass http://backend:8000/uploads/; \
        proxy_set_header Host $host; \
    } \
    location /docs { \
        proxy_pass http://backend:8000/docs; \
        proxy_set_header Host $host; \
    } \
    location /openapi.json { \
        proxy_pass http://backend:8000/openapi.json; \
        proxy_set_header Host $host; \
    } \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]