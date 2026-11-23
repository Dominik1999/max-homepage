<?php
// 925law – Zugriffsprotokolle nach 7 Tagen löschen (so steht es in der Datenschutzerklärung, Ziffer 3).
//
// Liegt auf dem Server unter ~/cron/logs_aufraeumen.php (NICHT in public_html) und läuft
// täglich über den Cronjob Manager der konsoleH. Hochgeladen wird es von bearbeiten/deploy_hetzner.sh.
// Hetzner legt die Protokolle als www_logs/<domain>/access.log.JJJJMMTT.gz ab und löscht sie selbst nicht.

$TAGE = 7;
$grenze = time() - $TAGE * 86400;
$basis = dirname(__DIR__) . '/www_logs';
$geloescht = 0;

foreach (glob($basis . '/*/*.log.*') ?: [] as $datei) {
    if (is_file($datei) && filemtime($datei) < $grenze && unlink($datei)) {
        $geloescht++;
    }
}
echo date('Y-m-d H:i') . " logs_aufraeumen: $geloescht Datei(en) gelöscht\n";
