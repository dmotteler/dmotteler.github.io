/*
    $Id: getqv.js,v 1.1 2021/09/25 17:59:48 dfm Exp $
    $Log: getqv.js,v $
    Revision 1.1  2021/09/25 17:59:48  dfm
    Initial revision

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
            if (k in qvdict) {
                qvdict[k].push(v)
            } else {
                qvdict[k] = [v];
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
