FROM nginx:alpine
COPY nginx.conf /etc/nginx

# create new directory to store nginx logs
RUN mkdir -p /var/log/nginx