/*
    $Id: getMusicLib.js,v 1.2 2022/07/05 23:02:55 dfm Exp $
    $Log: getMusicLib.js,v $
    Revision 1.2  2022/07/05 23:02:55  dfm
    minor log message tweak

    Revision 1.1  2022/06/30 23:35:50  dfm
    Initial revision


    load musiclib.xml, return promise
*/
function getMusicLib(url) {
    return fetch(url, {cache: "no-cache"})
    .then(response => response.text())
    .then(str => new window.DOMParser().parseFromString(str, "text/xml"))
    .then(data => {
        let libel = data.children[0];
        let musiclib = {};
        for (let songel of libel.children) {
            let song = {};
            let cats = [], trax = {}, sheet = {};
            for (let att of songel.attributes) {
                song[att.name] = att.value;
            }
            let sid = song.id;
            if (song.hasOwnProperty("aliasfor")) {
                // all of the song attributes are processed for aliases -
                // just go add it to the library.
                // console.log(`${sid} is alias for ${song['aliasfor']}`);
            } else {
                for (let el of songel.children) {
                    switch (el.tagName) {
                    case 'category':
                        if (! song.hasOwnProperty('category')) { song.category = []; }
                        song.category.push(el.textContent);
                        break;
                    case 'sheet':
                        song.sheet = {};
                        for (let att of el.attributes) {
                            song.sheet[att.name] = att.value;
                        }
                        break;
                    case 'tracks':
                        song.tracks = {};
                        for (let vel of el.children) {
                            let voice = {};
                            let v = "";
                            for (let att of vel.attributes) {
                                if (att.name == "voice") {
                                    v = att.value;
                                } else {
                                    voice[att.name] = att.value;
                                }
                            }
                            if (! song.tracks.hasOwnProperty(v)) {
                                song.tracks[v] = [];
                            }
                            song.tracks[v].push(voice);
                        }
                        break;
                    default:
                        song[el.tagName] = el.textContent;
                    }
                }
            }
            musiclib[sid] = song;
        }
        console.log('lib loaded.');
        return musiclib;
    });
}
