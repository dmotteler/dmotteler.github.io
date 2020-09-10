/*
    $Id: getqv.js,v 1.1 2020/08/22 19:30:20 dfm Exp $
    $Log: getqv.js,v $
    Revision 1.1  2020/08/22 19:30:20  dfm
    Initial revision


    parse the query string
*/

// started with https://css-tricks.com/snippets/javascript/get-url-variables/
var qvdict = {};

function getQueryVariable(variable, dflt)
{
    var query = window.location.search.substring(1);
    var vars = query.split("&");

    if (Object.keys(qvdict).length == 0) {
        for (var i=0;i<vars.length;i++) {
            var [k, v] = vars[i].split("=");
            v = unescape(v.replace(/\+/g, ' '));
            if (k in qvdict) {
                qvdict[k].push(v);
            } else {
                qvdict[k] = v;
            }
        }
    }
    var rv;
    if (variable in qvdict) {
        rv = qvdict[variable];
    } else {
        rv = [dflt];
    }

    return(rv);
}
