<?php
// 925law – Kontaktformular-Verarbeitung
// 1) sendet die Nachricht an die Kanzlei (Text)
// 2) sendet dem Absender eine automatische Eingangsbestätigung als HTML-Mail
//    mit seinem Nachrichtentext und eingebettetem 925-Logo.
// Antwort per JSON (AJAX) oder Redirect (falls JavaScript aus ist).

$EMPFAENGER = 'kontakt@925law.de';   // Zieladresse (Kanzlei)
$ABSENDER   = 'kontakt@925law.de';   // Muss eine existierende Adresse deiner Domain sein

// 925-Logo (PNG, Base64) – wird in die Bestätigungsmail eingebettet
$LOGO_B64 = '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';

header('Content-Type: application/json; charset=utf-8');

$wantsJson = (
  (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest')
  || (isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false)
);

function antwort_ok($wantsJson) {
  if ($wantsJson) { echo json_encode(['ok' => true]); }
  else { header('Location: index.html?sent=1#contact'); }
  exit;
}
function antwort_fehler($code, $wantsJson) {
  if ($wantsJson) { http_response_code(400); echo json_encode(['ok' => false, 'error' => $code]); }
  else { header('Location: index.html?error=1#contact'); }
  exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  antwort_fehler('method', $wantsJson);
}

// Spam-Falle
if (!empty($_POST['website'])) {
  antwort_ok($wantsJson);
}

$name    = trim($_POST['name'] ?? '');
$email   = trim($_POST['email'] ?? '');
$message = trim($_POST['message'] ?? '');
$lang    = (($_POST['lang'] ?? 'de') === 'en') ? 'en' : 'de';

if ($name === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
  antwort_fehler('validation', $wantsJson);
}

$safeName  = str_replace(["\r", "\n"], ' ', $name);
$safeEmail = str_replace(["\r", "\n"], '', $email);

// ---------------------------------------------------------------
// 1) Benachrichtigung an die Kanzlei (Text)
// ---------------------------------------------------------------
$subject = 'Neue Nachricht über 925law.de';
$body =
  "Neue Kontaktanfrage über die Website\n\n" .
  "Name:    " . $safeName . "\n" .
  "E-Mail:  " . $safeEmail . "\n" .
  "Sprache: " . ($lang === 'en' ? 'Englisch' : 'Deutsch') . "\n\n" .
  "Nachricht:\n" . $message . "\n";

$headers  = 'From: 925law Website <' . $ABSENDER . ">\r\n";
$headers .= 'Reply-To: <' . $safeEmail . ">\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

$sent = @mail($EMPFAENGER, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers, '-f ' . $ABSENDER);

if (!$sent) {
  antwort_fehler('mail', $wantsJson);
}

// ---------------------------------------------------------------
// 2) Automatische Eingangsbestätigung an den Absender (HTML + Logo)
//    Fehlversand bricht die Verarbeitung nicht ab.
// ---------------------------------------------------------------
$replySubject = ($lang === 'en') ? 'Your message to 925law' : 'Ihre Nachricht an 925law';

if ($lang === 'en') {
  $replyText =
    "Hello " . $safeName . ",\n\n" .
    "Thank you for your enquiry. I'll get back to you shortly.\n\n" .
    "Your message:\n" . $message . "\n\n" .
    "Kind regards\nMax Englhard\n925law\n\n" .
    "This is an automated confirmation. Please do not reply to this email.\n";
} else {
  $replyText =
    "Guten Tag " . $safeName . ",\n\n" .
    "Vielen Dank für Ihre Anfrage. Ich melde mich umgehend.\n\n" .
    "Ihre Nachricht:\n" . $message . "\n\n" .
    "Mit freundlichen Grüßen\nMax Englhard\n925law\n\n" .
    "Diese E-Mail wurde automatisch erzeugt. Bitte antworten Sie nicht direkt darauf.\n";
}

$nameHtml = htmlspecialchars($safeName, ENT_QUOTES, 'UTF-8');
$msgHtml  = nl2br(htmlspecialchars($message, ENT_QUOTES, 'UTF-8'));

$bodyFont  = "'IBM Plex Sans', Arial, Helvetica, sans-serif";
$brandFont = "'Archivo', 'IBM Plex Sans', Arial, Helvetica, sans-serif";

if ($lang === 'en') {
  $htmlLang = 'en';
  $greet    = 'Hello ' . $nameHtml . ',';
  $intro    = 'Thank you for your enquiry. I&rsquo;ll get back to you shortly.';
  $msgLbl   = 'Your message:';
  $signoff  = 'Kind regards';
  $autoNote = 'This is an automated confirmation. Please do not reply to this email.';
} else {
  $htmlLang = 'de';
  $greet    = 'Guten Tag ' . $nameHtml . ',';
  $intro    = 'Vielen Dank für Ihre Anfrage. Ich melde mich umgehend.';
  $msgLbl   = 'Ihre Nachricht:';
  $signoff  = 'Mit freundlichen Grüßen';
  $autoNote = 'Diese E-Mail wurde automatisch erzeugt. Bitte antworten Sie nicht direkt darauf.';
}

$replyHtml =
  '<!DOCTYPE html><html lang="' . $htmlLang . '"><head><meta charset="utf-8">' .
  '<style>' .
  "@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Sans:wght@400;600&display=swap');" .
  'body{margin:0;}' .
  '</style></head><body style="margin:0;">' .
  '<div style="font-family:' . $bodyFont . ';font-size:14px;line-height:1.6;color:#161616;">' .
  '<p>' . $greet . '</p>' .
  '<p>' . $intro . '</p>' .
  '<p><strong style="font-weight:600;">' . $msgLbl . '</strong><br>' . $msgHtml . '</p>' .
  '<p>' . $signoff . '<br>Max Englhard<br>' .
  '<span style="font-family:' . $brandFont . ';font-weight:800;">925law</span></p>' .
  '<p style="margin-top:20px;"><img src="cid:logo925" width="64" height="64" alt="925law" style="display:block;border:0;"></p>' .
  '<p style="font-family:' . $bodyFont . ';font-size:12px;color:#888888;">' . $autoNote . '</p>' .
  '</div></body></html>';

$rel = 'rel_' . bin2hex(random_bytes(8));
$alt = 'alt_' . bin2hex(random_bytes(8));

$replyHeaders  = 'From: 925law <' . $ABSENDER . ">\r\n";
$replyHeaders .= 'Reply-To: <' . $ABSENDER . ">\r\n";
$replyHeaders .= "Auto-Submitted: auto-replied\r\n";
$replyHeaders .= "MIME-Version: 1.0\r\n";
$replyHeaders .= 'Content-Type: multipart/related; boundary="' . $rel . "\"\r\n";

$b  = '--' . $rel . "\r\n";
$b .= 'Content-Type: multipart/alternative; boundary="' . $alt . "\"\r\n\r\n";
$b .= '--' . $alt . "\r\n";
$b .= "Content-Type: text/plain; charset=UTF-8\r\n";
$b .= "Content-Transfer-Encoding: base64\r\n\r\n";
$b .= chunk_split(base64_encode($replyText)) . "\r\n";
$b .= '--' . $alt . "\r\n";
$b .= "Content-Type: text/html; charset=UTF-8\r\n";
$b .= "Content-Transfer-Encoding: base64\r\n\r\n";
$b .= chunk_split(base64_encode($replyHtml)) . "\r\n";
$b .= '--' . $alt . "--\r\n\r\n";
$b .= '--' . $rel . "\r\n";
$b .= "Content-Type: image/png; name=\"925law.png\"\r\n";
$b .= "Content-Transfer-Encoding: base64\r\n";
$b .= "Content-ID: <logo925>\r\n";
$b .= "Content-Disposition: inline; filename=\"925law.png\"\r\n\r\n";
$b .= chunk_split($LOGO_B64) . "\r\n";
$b .= '--' . $rel . "--\r\n";

@mail($safeEmail, '=?UTF-8?B?' . base64_encode($replySubject) . '?=', $b, $replyHeaders, '-f ' . $ABSENDER);

antwort_ok($wantsJson);
