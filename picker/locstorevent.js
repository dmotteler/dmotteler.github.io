function getlsevs() {
    // eventlist has been loaded from eventx.xml. add any
    // events from localStorage that haven't been "published"
    // to eventlist. remove event from localStorage if it is
    // in eventlist.
    let newevs = [];
    for (let lskeyn = 0; lskeyn < localStorage.length; lskeyn++) {
        let lskey = localStorage.key(lskeyn);
        if (lskey in eventlist) {
            // event from local storage is in eventlist, 
            // don't need it in local storage.
            console.log(`removed ${lskey} from localStorage.`);
            localStorage.removeItem(lskey);
        } else if (! isNaN(lskey)) {
            // the key is numeric ("not not-a-number"), get the entry
            let tryev = JSON.parse(localStorage.getItem(lskey));
            if ('when' in tryev && 'where' in tryev && 'songlist' in tryev) {
                // ls entry sure looks like a valid event, but it's not in 
                // eventlist yet. add it now.
                eventlist[lskey] = tryev;
                newevs.push(lskey);
            }
        }
    }
    return newevs;
}

function savelsev() {
    // fulldate appears on the cheat sheet header
    // fulldate = formatDate(evdate, "%B %d, %Y %I:%M%P");
    fulldate = evdate;

    newevent = {'when': fulldate, 'where': venue, 'songlist': songlist, 'qtetSongs': qtetSongs };

    // save/replace event in localStorage
    localStorage.setItem(evndx, JSON.stringify(newevent))
    console.log(`saved ${evndx} to localStorage`);

    // add the new event to the event list for possible reuse by this ps
    eventlist[evndx] = newevent;
}
