function loadlib() {
    let voices = ['mix', 'bass', 'bari', 'lead', 'tenor'];
    let others = ['key', 'cat', 'firstwords', 'title'];

    // fetch('http://localhost/dfm_ws/jscheat/songlib.json')
    fetch('songlib.json')
        .then(function(response) { if (!response.ok) { throw new Error(`HTTP error! status: ${response.status}`); }
            return response.json();
        })
        .then(function(libjs) {

        for (let song in libjs) {
            songlib[song] = [];
            for (let voice in libjs[song]) {
                if (voices.includes(voice)) {
                    songlib[song][voice] = [];
                    for (let mod in libjs[song][voice]) {
                        songlib[song][voice][mod] = libjs[song][voice][mod];
                    }
                } else {
                    if (others.includes(voice)) {
                        songlib[song][voice] = libjs[song][voice];
                    } else {
                        alert("voice is " + voice);
                    }
                }
            }
        }
        console.log(Object.keys(songlib).length + " songs in lib");

        var sljs = getQueryVariable('songlist', '');
        if (sljs != '') {
            makeCheat(sljs);
        }

        clickmix();
    });
}
