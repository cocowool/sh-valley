<?php

set_time_limit(0);

echo "Init socket timeout : " . ini_get('default_socket_timeout') . "<br />";
echo "Program starts at ". date('h:i:s') . ".\n<br />";

$timeout=60; 
$result=array(); 
$sockets=array(); 
$convenient_read_block=8192;

/* Issue all requests simultaneously; there's no blocking. */
$delay=15;
$id=0;
while ($delay > 0) {
    $s=stream_socket_client("tcp://127.0.0.1:80", $errno, $errstr, $timeout); 
    if ($s) { 
        $sockets[$id++]=$s; 
        echo "\$sockets[$id] delay $delay<br />";
        $http_message="GET /stream/delay.php?delay=" . $delay . " HTTP/1.1\r\nHost: fun.php\r\n\r\n"; 
        fwrite($s, $http_message);
    } else { 
        echo "Stream " . $id . " failed to open correctly.<br />";
    } 
    $delay -= 3;
} 

while (count($sockets)) { 
    $read=$sockets; 
    stream_select($read, $w=null, $e=null, $timeout); 
    if (count($read)) {
        /* stream_select generally shuffles $read, so we need to
        compute from which socket(s) we're reading. */
        foreach ($read as $r) { 
            $id=array_search($r, $sockets); 
            $data=fread($r, $convenient_read_block); 
            /* A socket is readable either because it has
            data to read, OR because it's at EOF. */
            if (strlen($data) == 0) { 
                echo "Stream " . $id . " closes at " . date('h:i:s') . ".\n<br />";
                fclose($r); 
                unset($sockets[$id]); 
            } else { 
                $result[$id] .= $data; 
            } 
        } 
    } else { 
        /* A time-out means that *all* streams have failed
        to receive a response. */
        echo "Time-out!\n<br />";
        break;
    } 
} 
        
print_r( $result );