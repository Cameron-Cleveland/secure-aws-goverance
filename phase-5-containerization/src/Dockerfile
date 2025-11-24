FROM php:8.1-apache

WORKDIR /var/www/html

# Copy application files
COPY . .

# Install MySQL extensions specifically
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Enable Apache modules
RUN a2enmod rewrite

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Create a simple health check that tests DB connection
RUN echo '<?php \
header("Content-Type: application/json"); \
try { \
    $con = mysqli_connect(getenv("DB_HOST"), getenv("DB_USER"), getenv("DB_PASSWORD"), getenv("DB_NAME")); \
    if ($con) { \
        echo json_encode(["status": "healthy", "database": "connected"]); \
    } else { \
        echo json_encode(["status": "degraded", "database": "disconnected", "error": mysqli_connect_error()]); \
    } \
} catch (Exception $e) { \
    echo json_encode(["status": "unhealthy", "database": "error", "message": $e->getMessage()]); \
} \
?>' > /var/www/html/health-check.php

# Apache configuration
RUN echo '<Directory /var/www/html/>\n\
    Options Indexes FollowSymLinks\n\
    AllowOverride All\n\
    Require all granted\n\
    RewriteEngine On\n\
</Directory>' > /etc/apache2/conf-available/docker-php.conf

EXPOSE 80

CMD ["apache2-foreground"]
