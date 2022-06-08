/*
    $Id: bindtip.js,v 1.2 2022/05/21 18:21:19 dfm Exp $
    $Log: bindtip.js,v $
    Revision 1.2  2022/05/21 18:21:19  dfm
    fix the tooltip position

    Revision 1.1  2022/05/14 17:52:57  dfm
    Initial revision


    manage tooltips for covdir
*/
function showTooltip(x, y, contents) {
    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y - 16 - 5,
        left: x + 5,
        border: '1px solid #fdd',
        padding: '2px',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}
var previousPoint = null;
function bindtip(phname) {
    $(phname).bind("plothover", function (event, pos, item) {
        if (item) {
            if (previousPoint != item.dataIndex) {
                function sfmt(v) {
                    let s = v.toFixed(3);
                    if (s.substring(s.length - 4) == ".000") {
                        s = s.substring(0, s.length - 4);
                    }
                    return (s);
                }

                previousPoint = item.dataIndex;
                
                $("#tooltip").remove();
                var d = new Date(item.datapoint[0]);
                sdat = (d.getUTCMonth() + 1) + "/" + d.getUTCDate() + "/" + (d.getUTCFullYear());
                if (item.series.stack) {
                    let vn = sfmt(item.datapoint[1] - item.datapoint[2]);
                    let vt = sfmt(item.datapoint[1]);
                    var tip = "<table border='1'><tr><td colspan='2' align='center'>" + sdat + "</td></tr><tr><td>" + item.series.label + "</td><td align='right'>" + vn + "</td></tr><tr><td>Total</td><td>" + vt + "</td></tr></table>";
                } else {
                    let v = sfmt(item.datapoint[1]);
                    var tip = sdat + " " + item.series.label + " = " + v;
                }

                showTooltip(item.pageX, item.pageY, tip);
            }
        }
        else {
            $("#tooltip").remove();
            previousPoint = null;            
        }
    });
}
/*
    $Id: buildhtml.js,v 1.7 2022/06/06 02:20:56 dfm Exp dfm $
    $Log: buildhtml.js,v $
    Revision 1.7  2022/06/06 02:20:56  dfm
    get norm, updated, and county from controls in favor of globals
    add holder table for table display to html

    Revision 1.6  2022/05/14 18:00:27  dfm
    fix placeholder in tab activation
    moved tooltip stuff to its own file

    Revision 1.5  2022/01/16 21:38:47  dfm
    get data-updated date from meta, not localStorage
    add "per 100k" to page header if appropriate

    Revision 1.4  2021/11/09 01:25:43  dfm
    major overhaul/restructure. most visible change is tabs_, choices_, and cbid_ no longer
    have sheet names, using digits instead.

    Revision 1.3  2021/10/27 19:10:16  dfm
    make active_sheet global, set when a sheet is selected

    Revision 1.2  2021/10/08 00:39:35  dfm
    get rid of the agerangechkd, choices, and placeholder arrays, use jquery refs instead.

    Revision 1.1  2021/10/07 19:46:13  dfm
    Initial revision


    use alldata to build tabs_html
*/

var allsheets, active_sheet, active_sheet_ndx;
var county;
var tabdiv_html;
var tabs_html;
var meta;

function buildHTML() {
    // create the html for the header, the choices panel and an empty placeholder for all sheets.
    tabs_html = '';

    let updated = meta["dtm_updated"];

    let w = 0.85 * window.innerWidth + "px", h = 0.78 * window.innerHeight + "px";
    // for each sheet (Cases, Deaths, Hospitilizations)...
    $.each(alldata[county], function (sheet, ageranges) {
        // start the tab div, put in a header, start a table, row, and cell 1.
        // open the choices para.
        let m = allsheets.indexOf(sheet);
        let norm = $("#norm").prop("checked");
        let normornot = norm ? " per 100k" : "";
        let dispCounty = county == "Statewide" ? county : (county + " County");
        tabs_html += `\n<div id="tabs_${m}">
<h3>${dispCounty} ${sheet}${normornot}</h3>
<h5>data updated ${updated}</h5>
<table><tr><td class="choices">
<p id="choices_${m}"><br/>`;

        let n = -1;
        // for each age-range in the sheet for county...
        $.each(alldata[county][sheet], function (agerange, ageseries) {
            n += 1;
            // add a checkbox in checked state and a label for the agerange to cell 1,1
            var cbid = `cbid_${m}_${n}`;

            tabs_html += `<input type="checkbox" name="${agerange}" checked="checked" id="${cbid}"><label for="${cbid}">${agerange}</label><br/>\n`;
        });

        // add set all and clear all buttons
        tabs_html += `<br/><input type="button" name="set_${m}" id="set_${m}" value="Set All"><br/><br/>
<input type="button" name="clear_${m}" id="clear_${m}" value="Clear All">`;

        // close the choices para and cell 1,1,
        // create cell 1,2 with the placeholder div 
        // and a hidden cell 1,3 for a table display.
        // close cell 1,3 and row 1
        tabs_html += `</p></td>
<td class='dispischart'><div id="placeholder_${m}" style="display:block;width:${w};height:${h};"></div></td>
<td class='dispistable hidden'></td></tr>
`;

        // close the table
        tabs_html += '</table>';
        // close the tab-n (sheet) div
        tabs_html += '</div>';
        // close the tabs div
        tabs_html += '</div>';
    });

    var tabsOps = {
        active: 0,
        activate: function(event ,ui) {
            active_sheet = ui.newTab[0].innerText;
            active_sheet_ndx = allsheets.indexOf(active_sheet);

            let phname = `#placeholder_${active_sheet_ndx}`;
            placeholder = $(phname);
            placeholder.bind("plotselected", plotselfun);
            placeholder.bind("plotunselected", plotunselfun);

            bindtip(phname);

            county = $("#county option:selected").text();

            console.log(`${county} ${active_sheet} ${phname} activated.`);

            plotAccordingToChoices();
        },
        ajaxOptions: {
            error: function( xhr, status, index, anchor ) {
                $( anchor.hash ).html("Couldn't load this tab. We'll try to fix this as soon as possible.");
            }
        }
    }

    $("#tabs").replaceWith(tabdiv_html);
    $("#tabs").append(tabs_html);
    $("#tabs").tabs(tabsOps);

    // the choices panel is active, the display panel is empty at this point.

    $.each(alldata[county], function (sheet, sheetdata) {
        let sn = allsheets.indexOf(sheet);
        let chn = `#choices_${sn}`;
        $(chn).find("input:checkbox").click(setChoice);
        $(chn).find("input:button").click(setClear);
    });
}
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
/*
    $Id: savetab.js,v 1.1 2022/06/06 02:18:53 dfm Exp $
    $Log: savetab.js,v $
    Revision 1.1  2022/06/06 02:18:53  dfm
    Initial revision


    save data for current_sheet, county as CSV
*/

var allsheets;
function saveCSV(county, sheet) {
    let sn = allsheets.indexOf(sheet);
    let normornot = norm ? " per 100k" : "";

    let chn = `#choices_${sn}`;
    let cbs = $(chn).find("input[type='checkbox']");
    
    let ranges = ['Date'];
    $.each(cbs, function(n, cb) {
        if (cb.checked) {
            let agerange = cb.name;
            ranges.push(agerange);
        }
    });

    let csvtxt = ranges.join(",") + "\n";

    // get date range from selected range if set, else pickers.
    var fromdate = selfrom ? selfrom : startdate;
    var todate = selto ? selto : enddate;
    let restruc = {};
    $.each(cbs, function(n, cb) {
        // if the agerange is selected (checked)...
        if (cb.checked) {
            // make it easier to build table (row order) from data (column order)
            let agerange = cb.name;
            $.each(alldata[county][sheet][agerange], function (n, ser) {
               if (ser[0] >= fromdate && ser[0] <= todate) {
                   var d = new Date(ser[0]).toISOString().substring(0,10);
                   var v = ser[1];
                   if (norm) {
                       v *= normfac[county];
                   }
                   if (! restruc.hasOwnProperty(d)) {
                       restruc[d] = [];
                   }
                   restruc[d].push(v);
               }
            });
        }
    });

    for (let d in restruc) {
        let n = 0;
        let vals = [d];
        for (let v of restruc[d]) {
            // restruc[d] is a list of values per selected age range
            n += 1;
            let ar = ranges[n];
            let s = v ? v.toFixed(3) : "";
            vals.push(s);
        }
        csvtxt += vals.join(",") + "\n";
    }

    // download the csv file
    let csvfn = `${county}_${sheet}${normornot}.csv`;
    let pom = document.createElement('a');
    pom.style.display = 'none';
    pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(csvtxt));
    pom.setAttribute('download', csvfn);
    document.body.appendChild(pom);
    pom.click();
    document.body.removeChild(pom);
    console.log(`${csvfn} created.`);
}
/*
    $Id: tablehtml.js,v 1.5 2022/06/06 02:19:35 dfm Exp dfm $
    $Log: tablehtml.js,v $
    Revision 1.5  2022/06/06 02:19:35  dfm
    pay attention to selected range, if present

    Revision 1.4  2022/05/21 18:24:07  dfm
    remove County from Statewide header

    Revision 1.3  2022/01/16 21:43:06  dfm
    make function to format fp data 
    add "per 100k" to table header as appropriate
    track and highlight max values in each column

    Revision 1.2  2021/12/22 00:36:13  dfm
    placeholder name in the generated html was a selector, wanted id (removed leading #)

    Revision 1.1  2021/11/09 01:29:58  dfm
    Initial revision


    create the html to display selected columns of a sheet
*/

var allsheets;
function fp4(v) {
    // protect against missing data - Unassigned County has several
    let rv;
    if (v) {
        let s = v.toString();
        let n = s.indexOf(".");
        if (n < 0) {
            // rv = s + ".0000";
            rv = s;
        } else {
            let t = `${s}0000`;
            rv = t.substring(0, n + 5);
        }
    } else {
        rv = "";
    }
    return(rv);
}
function tableHTML(county, sheet) {
    let sn = allsheets.indexOf(sheet);
    let dispCounty = county == "Statewide" ? county : (county + " County");
    let normornot = norm ? " per 100k" : "";
    let phname = `tableholder_${sn}`;
    var html = `<div id="${phname}">
<table class="datatab">
<caption> ${dispCounty} ${sheet}${normornot}</caption>
`;
    html += '<thead><tr><th>Date</th>';

    let chn = `#choices_${sn}`;
    let cbs = $(chn).find("input[type='checkbox']");
    
    let ranges = [];
    $.each(cbs, function(n, cb) {
        if (cb.checked) {
            let agerange = cb.name;
            html += `<th>${agerange}</th>`;
            ranges.push(agerange);
        }
    });

    html += "</tr></thead><tbody>\n";
    // get date range from selected range if set, else pickers.
    var fromdate = selfrom ? selfrom : startdate;
    var todate = selto ? selto : enddate;

    let restruc = {};
    let vmax = {};
    let dmax = {};
    $.each(cbs, function(n, cb) {
        // if the agerange is selected (checked)...
        if (cb.checked) {
            // make it easier to build table (row order) from data (column order)
            let agerange = cb.name;
            vmax[agerange] = 0.0;
            // console.log(`building table for ${sheet} ${agerange}`);   
            $.each(alldata[county][sheet][agerange], function (n, ser) {
                if (ser[0] >= fromdate && ser[0] <= todate) {
                    var d = new Date(ser[0]).toISOString().substring(0,10);
                    var v = ser[1];
                    if (norm) {
                        v *= normfac[county];
                    }
                    if (! restruc.hasOwnProperty(d)) {
                        restruc[d] = [];
                    }
                    restruc[d].push(v);
                    if (v > vmax[agerange]) {
                        vmax[agerange] = v;
                        dmax[agerange] = d;
                    }
                }
            });
        }
    });

    let svmax = {};
    for (let ar in vmax) {
        svmax[ar] = fp4(vmax[ar]);
        // console.log(`svmax ${ar} is ${svmax[ar]} on ${dmax[ar]}`);
    }

    for (let d in restruc) {
        let n = -1;
        html += `<tr><td>${d}</td>`;
        for (let v of restruc[d]) {
            // restruc[d] is a list of values per selected age range
            n += 1;
            let ar = ranges[n];
            let s = fp4(v);
            if (s == svmax[ar]) {
                html += `<td class='maxv'>${s}</td>`;
            } else {
                html += `<td>${s}</td>`;
            }
        }
        html += "</tr>\n";
    }
    html += '</table></div>';
    return html;
}
