<?php
$xml = file_get_contents('php://input');
file_put_contents("uploadedmusiclib.xml", $xml);
?>
