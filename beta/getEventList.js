/*
    $Id: getEventList.js,v 1.1 2022/06/30 23:37:59 dfm Exp $
    $Log: getEventList.js,v $
    Revision 1.1  2022/06/30 23:37:59  dfm
    Initial revision


    load Tuners event list, return promise
*/

function getEventList(url) {
    return fetch(url)
    .then(response => response.text())
    .then(str => new window.DOMParser().parseFromString(str, "text/xml"))
    .then(data => {
        let listel = data.children[0];
        let eventlist = {};
        for (let eventel of listel.children) {
            let evt = [];
            let dtndx = '';
            for (let att of eventel.attributes) {
                if (att.name == 'songlist' || att.name == 'qtetsongs') {
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
