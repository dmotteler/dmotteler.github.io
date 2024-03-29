/*
    $Id: getEventList.js,v 1.2 2022/07/05 23:01:58 dfm Exp $
    $Log: getEventList.js,v $
    Revision 1.2  2022/07/05 23:01:58  dfm
    use camel-case qtetSongs throughout

    Revision 1.1  2022/06/30 23:37:59  dfm
    Initial revision


    load Tuners event list, return promise
*/

function getEventList(url) {
    return fetch(url, {cache: "no-cache"})
    .then(response => response.text())
    .then(str => new window.DOMParser().parseFromString(str, "text/xml"))
    .then(data => {
        let listel = data.children[0];
        let eventlist = {};
        for (let eventel of listel.children) {
            let evt = [];
            let dtndx = '';
            for (let att of eventel.attributes) {
                if (att.name == 'songlist' || att.name == 'qtetSongs') {
                    evt[att.name] = att.value.split(" ");
                } else if (att.name == 'dtndx') {
                    dtndx = att.value;
                } else {
                    evt[att.name] = att.value;
                }
            }
            eventlist[dtndx] = evt;
        }
        console.log('event list loaded.');
        return eventlist;
    });
}
