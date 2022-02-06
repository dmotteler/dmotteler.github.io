function saveit() {
    // make sure no required values are missing...
    let needvals = document.querySelectorAll(".reqd");
    if (needvals.length > 0) {
        needvals[0].scrollIntoView(true); 
        alert("missing required value!");
        return;
    }
    
    // no missing requireds - only download if there are
    // new or changed values.
    let news = document.querySelectorAll(".added");
    let chgs = document.querySelectorAll(".chgd");

    if (news.length < 1 && chgs.length < 1 && deleteCount < 1) {
        alert("nothing has changed - no need to download!");
        return;
    }

    let rev = fmtDate()[2];
    let newxml = `<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet type="text/xsl" href="musiclib.xsl"?>
<musiclib name="Tuners Music Library" rev="${rev}">
`;
    let attrs = ['id', 'name'];
    let props = [ 'notes', 'location', 'key', 'pitch', 'words', 'arranger', 'composer',
        'lyricist', 'learn_by', 'ordered', 'stockID', 'copies', 'source', 'copyright', 'crdate'];

    sortcol = 'name';

    // process the song objects in song name order
    for (let song of songobjects.sort(bycol)) {
        let sid = song['id'];
        let nam = song['name'];
        newxml += `  <song id="${sid}" name="${nam}">\n`;
        if (song.hasOwnProperty('aliases')) {
            for (let aka of song['aliases']) {
                newxml += `    <alias>${aka}</alias>\n`;
            }
        }
        for (let cat of song['categories']) {
            newxml += `    <category>${cat}</category>\n`;
        }
        for (let prop of props) {
            if (song.hasOwnProperty(prop)) {
                let val = song[prop];
                newxml += `    <${prop}>${val}</${prop}>\n`;
            }
        }
        if (song.hasOwnProperty('sheet')) {
            let gdid = song['sheet']['gdid'];
            let fpat = song['sheet']['sheet'];
            newxml += `    <sheet gdid="${gdid}" sheet="${fpat}" />\n`;
        }
        if (song.hasOwnProperty('tracks')) {
            newxml += `    <tracks>\n`;
            for (let voice in song['tracks']) {
                let gdid = song['tracks'][voice]['gdid'];
                let mods = song['tracks'][voice]['mods'];
                let path = song['tracks'][voice]['path'];
                newxml += `      <voice gdid="${gdid}" mods="${mods}" path="${path}" voice="${voice}" />\n`;
            }
            newxml += "    </tracks>\n";
        }
        newxml += "  </song>\n";
    }
    newxml += "</musiclib>\n";

    // expand special chars here - only & seems to be needed.
    let re = /&/g;
    newxml = newxml.replace(re, "&amp;");

    var dlname = 'musiclib.xml';

    let pom = document.createElement('a');
    pom.style.display = 'none';
    pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(newxml));
    pom.setAttribute('download', dlname);
    document.body.appendChild(pom);
    pom.click();
    document.body.removeChild(pom);
}
