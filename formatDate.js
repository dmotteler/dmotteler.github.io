/*
    $Id: formatDate.js,v 1.1 2022/07/05 23:01:35 dfm Exp $
    $Log: formatDate.js,v $
    Revision 1.1  2022/07/05 23:01:35  dfm
    Initial revision


    lifted from jquery.flot.time.js
*/

// Returns a string with the date d formatted according to fmt.
// A subset of the Open Group's strftime format is supported.

// formatDate assumes local timezone, formatUTCDate assumes UTC

// formatTZDate makes a new Date by applying tzoff to the valueOf the given date, 
// then formats it with formatDate

// next 4 based on
//   https://stackoverflow.com/questions/76464487/get-localized-short-names-of-days-of-week-from-monday-to-sunday-in-javascript
var lang = undefined; // use browser lang. like 'en-US'
var longMonthNames = new Array(12).fill(0).map((x, i) => new Date(1,i,1).toLocaleString(lang, {month:'long'}))
var shortMonthNames = new Array(12).fill(0).map((x, i) => new Date(1,i,1).toLocaleString(lang, {month:'short'}))
var shortWeekdayNames = new Array(7).fill(0).map((x, i) => new Date(1,0,i-1).toLocaleString(lang, {weekday:'short'}));
var longWeekdayNames = new Array(7).fill(0).map((x, i) => new Date(1,0,i-1).toLocaleString(lang, {weekday:'long'}));

function formatDate(d, fmt, monthNames, dayNames) {

    if (typeof d.strftime == "function") {
        return d.strftime(fmt);
    }

    var leftPad = function(n, pad) {
        n = "" + n;
        pad = "" + (pad == null ? "0" : pad);
        return n.length == 1 ? pad + n : n;
    };

    var r = [];
    var escape = false;
    var hours = d.getHours();
    var isAM = hours < 12;

    var hours12;

    if (hours > 12) {
        hours12 = hours - 12;
    } else if (hours == 0) {
        hours12 = 12;
    } else {
        hours12 = hours;
    }

    for (var i = 0; i < fmt.length; ++i) {

        var c = fmt.charAt(i);

        if (escape) {
            switch (c) {
                case 'a': c = "" + shortWeekdayNames[d.getDay()]; break;
                case 'A': c = "" + longWeekdayNames[d.getDay()]; break;
                case 'b': c = "" + shortMonthNames[d.getMonth()]; break;
                case 'B': c = "" + longMonthNames[d.getMonth()]; break;
                case 'd': c = leftPad(d.getDate()); break;
                case 'e': c = leftPad(d.getDate(), " "); break;
                case 'h':	// For back-compat with 0.7; remove in 1.0
                case 'H': c = leftPad(hours); break;
                case 'I': c = leftPad(hours12); break;
                case 'l': c = leftPad(hours12, " "); break;
                case 'm': c = leftPad(d.getMonth() + 1); break;
                case 'M': c = leftPad(d.getMinutes()); break;
                // quarters not in Open Group's strftime specification
                case 'q':
                    c = "" + (Math.floor(d.getMonth() / 3) + 1); break;
                case 'S': c = leftPad(d.getSeconds()); break;
                case 'y': c = leftPad(d.getFullYear() % 100); break;
                case 'Y': c = "" + d.getFullYear(); break;
                case 'p': c = (isAM) ? ("" + "am") : ("" + "pm"); break;
                case 'P': c = (isAM) ? ("" + "AM") : ("" + "PM"); break;
                case 'w': c = "" + d.getDay(); break;
            }
            r.push(c);
            escape = false;
        } else {
            if (c == "%") {
                escape = true;
            } else {
                r.push(c);
            }
        }
    }

    return r.join("");
}

function formatUTCDate(d, fmt, monthNames, dayNames) {

    if (typeof d.strftime == "function") {
        return d.strftime(fmt);
    }

    var leftPad = function(n, pad) {
        n = "" + n;
        pad = "" + (pad == null ? "0" : pad);
        return n.length == 1 ? pad + n : n;
    };

    var r = [];
    var escape = false;
    var hours = d.getUTCHours();
    var isAM = hours < 12;

    var hours12;

    if (hours > 12) {
        hours12 = hours - 12;
    } else if (hours == 0) {
        hours12 = 12;
    } else {
        hours12 = hours;
    }

    for (var i = 0; i < fmt.length; ++i) {

        var c = fmt.charAt(i);

        if (escape) {
            switch (c) {
                case 'a': c = "" + shortWeekdayNames[d.getUTCDay()]; break;
                case 'A': c = "" + longWeekdayNames[d.getUTCDay()]; break;
                case 'b': c = "" + shortMonthNames[d.getUTCMonth()]; break;
                case 'B': c = "" + longMonthNames[d.getUTCMonth()]; break;
                case 'd': c = leftPad(d.getUTCDate()); break;
                case 'e': c = leftPad(d.getUTCDate(), " "); break;
                case 'h':	// For back-compat with 0.7; remove in 1.0
                case 'H': c = leftPad(hours); break;
                case 'I': c = leftPad(hours12); break;
                case 'l': c = leftPad(hours12, " "); break;
                case 'm': c = leftPad(d.getUTCMonth() + 1); break;
                case 'M': c = leftPad(d.getUTCMinutes()); break;
                // quarters not in Open Group's strftime specification
                case 'q':
                    c = "" + (Math.floor(d.getUTCMonth() / 3) + 1); break;
                case 'S': c = leftPad(d.getUTCSeconds()); break;
                case 'y': c = leftPad(d.getUTCFullYear() % 100); break;
                case 'Y': c = "" + d.getUTCFullYear(); break;
                case 'p': c = (isAM) ? ("" + "am") : ("" + "pm"); break;
                case 'P': c = (isAM) ? ("" + "AM") : ("" + "PM"); break;
                case 'w': c = "" + d.getUTCDay(); break;
            }
            r.push(c);
            escape = false;
        } else {
            if (c == "%") {
                escape = true;
            } else {
                r.push(c);
            }
        }
    }

    return r.join("");
}

function formatTZDate(d, tzctrl, fmt, monthNames, dayNames) {
    if (isNaN(d.valueOf())) {
        return ("-NA-");
    } else {
        // tzctrl = {'tzoff':tzoff; 'ondate':ondate, 'offdate':offdate; 'obs':obs }
        let tzoff = tzctrl['tzoff'];
        if (tzctrl['obs'] != 0) {
            // this timezone observes DST for dates from ondate to offdate
            if (d >= tzctrl['ondate'] && d < tzctrl['offdate']) {
                tzoff -= 3600 * 1000;
            }
        }
        let tdat = new Date(d.valueOf() + tzoff);
        return formatDate(tdat, fmt, monthNames, dayNames);
    }
}
