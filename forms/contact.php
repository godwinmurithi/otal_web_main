<?php

$to = 'info@orionterrametrics.co.ke';

// Sanitize and validate input
$name    = htmlspecialchars(strip_tags(trim($_POST['name'])));
$email   = filter_var(trim($_POST['email']), FILTER_SANITIZE_EMAIL);
$subject = htmlspecialchars(strip_tags(trim($_POST['subject'])));
$message = htmlspecialchars(strip_tags(trim($_POST['message'])));

if (empty($name) || !filter_var($email, FILTER_VALIDATE_EMAIL) || empty($subject) || empty($message)) {
  http_response_code(400);
  echo 'Please complete the form correctly.';
  exit;
}

// Compose email
$email_subject = "Website Contact Form: $subject";
$email_body = "You have received a new message from your website contact form.\n\n".
              "Name: $name\n".
              "Email: $email\n".
              "Subject: $subject\n\n".
              "Message:\n$message";

// Email headers
$headers = "From: Orion Terrametrics <noreply@orionterrametrics.co.ke>\r\n";
$headers .= "Reply-To: $email\r\n";

// Send mail
if (mail($to, $email_subject, $email_body, $headers)) {
  echo 'OK'; // What the JS expects on success
} else {
  http_response_code(500);
  echo 'Message could not be sent. Please try again later.';
}
?>


