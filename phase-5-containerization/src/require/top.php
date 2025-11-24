<?php
session_start();
// Database connection
$con = mysqli_connect(getenv('DB_HOST'), getenv('DB_USER'), getenv('DB_PASSWORD'), getenv('DB_NAME'));
if (!$con) {
    die("Database connection failed");
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Store</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        .header { background: #333; color: white; padding: 1rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 1rem; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>E-Commerce Store</h1>
        </div>
    </div>
    <div class="container">
