<?php
require('mus_smarty.php');
    $qs = $_SERVER['QUERY_STRING'];
    parse_str($qs, $args);

    $verbose = array_key_exists('verbose', $args);

    if (array_key_exists('cat', $args)) {
        $cats = explode(" ", $args['cat']);
    } else {
        $cats = "";
    }

    $db = new SQLite3('../music/music.db3');

    if ($cats == "") {
        $stmt = $db->prepare("SELECT songName, Song_ID
            FROM songs
            ORDER BY songName");
    } else {
        $placeHolders = implode(',', array_fill(0, count($cats), '?'));
        $stmt = $db->prepare("SELECT songName, songs.Song_ID
            FROM songs, categories, validCats
            WHERE songs.Song_ID = categories.Song_ID
            AND categories.Cat_ID = validCats.Cat_ID
            AND category IN ($placeHolders)
            ORDER BY songName");

        $n = 0;
        foreach ($cats as $cat) {
            $n += 1;
            $stmt->bindValue($n, $cat);
        }
    }

    $tstmt = $db->prepare("SELECT voice, gdid, path, mods
        FROM songTracks
        WHERE Song_ID = ?");
    
    $results = $stmt->execute();
    if (!$results) {
        print("after select song: ".$db->lastErrorMsg());
    }

    $mstmt = $db->prepare("SELECT voice, gdid, path, mods
        FROM songTracks
        WHERE Song_ID = ?");
    
    $results = $stmt->execute();
    if (!$results) {
        print("after select song: ".$db->lastErrorMsg());
    }

    $songs = [];
    while ($row = $results->fetchArray()) {
        $nam = $row['songName'];
        $sid = $row['Song_ID'];
        $songs[$nam] = [];

        $tstmt->bindValue(1, $sid);
        $tres = $tstmt->execute();
        if (!$tres) {
            print("after select trax: ".$db->lastErrorMsg());
        }
        while ($trow = $tres->fetchArray()) {
            $voice = $trow['voice'];
            $gdid = $trow['gdid'];
            $path = $trow['path'];
            $mods = $trow['mods'];

            if (! array_key_exists($voice, $songs[$nam])) {
                $songs[$nam][$voice] = [];
            }
            $songs[$nam][$voice][$mods] = [$gdid, $path];
        }
    }

    $hdrs = ['Song', 'mix', 'bari', 'bass', 'lead', 'tenor'];
    $voices = $hdrs;
    array_shift($voices);
    $title = "Tuner Training Tracks";

    $smarty->assign("hdrs", $hdrs);
    $smarty->assign("voices", $voices);
    $smarty->assign("title", $title);
    $smarty->assign("songs", $songs);
    $smarty->display("matrix.tpl");
?>
