# Use an official PHP image with Apache
FROM php:8.2-apache

# Copy your application code into the container
COPY . /var/www/html/

# Set permissions for Apache
RUN chown -R www-data:www-data /var/www/html

# Expose port 80
EXPOSE 80
