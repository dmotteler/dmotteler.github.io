var data = [] // array of series for each category
var meta = {};
var alldata = {}; // indexed by county, then sheet, then agerange. values are list of [time, val]
var allsheets = []; // sheet (tab) names
var normfac = []; // county pops norm. to 100,000

var tabdiv_html; // tab select html goes here.
var tabs_html; // save the html for each sheet tab here.
var active_sheet; // name of the active tab (== sheet).
var active_sheet_ndx; // index in allsheets of active sheet
var placeholder; // active placeholder
var startdate, enddate; // date range, string yyyy-mm-dd
var selfrom = null, selto = null; // date range for selection
var plot; // current plot object

// these variables should always match the setting of the corresponding checkboxes, radio buttons, or select.
var norm; // normalize data (per 100,000) true/false
var dodetail; // plot agerange detail
var dototals; // plot accum. totals for each agerange
var displayType; // show chart if "c", table if "t"
var county; // currently selected county name

// chart plot options
var options = {
    series: {
        lines: { show: true, lineWidth: 2 },
        points: { show: false, symbol: "cross" },
    },
    grid: { hoverable: true, clickable: true },
    legend: { show: true, noColumns: 2, position: "ne", margin: 10 },
    xaxis: { mode: "time", labelHeight: 20,
        timeBase: "milliseconds", timezone: "utc", timeformat: "%m/%d/%y", tickSize: [7, "day"] },
    // yaxis: { min: 0, labelWidth: 60 },
    yaxis: { min: 0 },
    yaxes: [ { }, { position: "right", alignTicksWithAxis: 1 } ],
    selection: { mode: "x" },
};

function ajax_error(jqXHR, textStatus, errorThrown) {
    alert("ajax error " + textStatus + ", error Thrown is " + errorThrown);
}

function changeDates() {
    // called whenever one of the date pickers loses focus
    startdate = document.querySelector('#fromid').value;
    enddate = document.querySelector('#toid').value;
    plotAccordingToChoices();
}
function fetchData() {
    // (re)start the wait spinner
    document.querySelector("#tabs").outerHTML = `<div id="tabs" class="loader" style="width: 300px; height: 300px;">
  <img src="covid.png" alt="covid" width="300" height="300">
  </div>`;

    // ask ajax to get the data
    $.ajax({
        url: "Epi.json",
        xhr: function(){ // give ajax a new xhr, so we can access the status
            return this._xhr = new XMLHttpRequest();
        },
        method: 'GET',
        dataType: 'json',
        error: ajax_error,
        success: onDataReceived
    });
}
function onDataReceived(covdata) {
    // data ready - update the local (indexed) database

    if (covdata) {
        // got new data -
        console.log(`onDataReceived status with data ${this._xhr.status}, url ${this.url}`);
        meta['counties'] = covdata['meta']['counties'].split(",");
        meta['dtm_updated'] = covdata['meta']['dtm'];

        let countysel = `<select id='county' onchange='getCounty()'><option>${meta['counties'].join('<option>')}</select>`;
        countysel = countysel.replace(">Lewis", " selected>Lewis");
        document.querySelector("#county").outerHTML = countysel;
    } else {
        // didn't get data from ajax. put a message on the console 
        // and use database copy. 304 means the file modify time is unchanged.
        console.log(`onDataReceived status no data ${this._xhr.status}, url ${this.url}`);

        // no data => nothing to do.
        return;
    }

    // covdata has a dict indexed by 'data' and 'meta'. 'meta' has source file
    // metadata, including xlfile, filetime, dtm, tables, and counties.
    // 'data' has county dicts ('Lewis', etc.), which have sheets dicts
    // ('Cases', 'Hospitilizations', 'Deaths'), which contain the
    // rows from the sheets. The first row has the column headers.
    // by the sheet column headers (the age ranges). the age range
    // contains a list of (date, value) pairs.

    let sheethdrs;

    alldata = [];

    $.each(covdata['data'], function (county, countydata) {
        if (! alldata.hasOwnProperty(county)) {
            alldata[county] = {};
        }
        $.each(countydata, function (sheet, sheetrows) {
            if (! alldata[county].hasOwnProperty(sheet)) {
                alldata[county][sheet] = {};
            }
            let dat;
            $.each(sheetrows, function (rowno, row) {
                if (rowno == 0) {
                    // use slice to copy the list of hdrs (age ranges)
                    sheethdrs = row.slice();
                } else {
                    $.each(row, function (cellno, cell) {
                        switch (cellno) {
                            case 0:
                                if (cell == "Date" || cell == "Admission") {
                                    return; // "continue"
                                } else if (cell == "Unknown") {
                                    // use today for unknown date.
                                    dat = new Date().toISOString().substring(0,10);
                                } else {
                                    dat = new Date(cell).toISOString().substring(0,10);
                                }
                                break;
                            default:
                                let k = sheethdrs[cellno];

                                if (! alldata[county][sheet].hasOwnProperty(k)) {
                                    alldata[county][sheet][k] = [];
                                }
                                alldata[county][sheet][k].push([dat, cell]);
                                break;
                        }
                    });
                }
            });
        });
    });
    afterLoad();
}

function init() {
    startdate = getQueryVariable('from', ['2022-01-01'])[0];
    document.querySelector('#fromid').value = startdate;
    tod = $.plot.formatDate(new Date(), "%Y-%m-%d");
    enddate = getQueryVariable('to', [tod])[0];
    document.querySelector('#toid').value = enddate;
    console.log(`in init, startdate: ${startdate}, enddate: ${enddate}`);

    // start the data fetch
    fetchData();
}

function afterLoad() {
    // the next five reflect current option settings
    norm = $("#norm").prop("checked");
    dodetail = $("#detail").prop("checked");
    dototals = $("#totals").prop("checked");
    displayType = $("#dtTable").prop("checked") ? "t" : "c";
    county = $("#county option:selected").text();

    // create normalizing factors:
    //   act. value : act. pop == norm. value : 100k =>
    //   norm. value = act. value * (100k/act. pop)
    for (let cty in countypops) {
        normfac[cty] = 100000.0/countypops[cty];
    }

    $(function() {
        $( "#detail" ).click(setOpts);
        $( "#norm" ).click(setOpts);
        $( "#totals" ).click(setOpts);
        $( "#dtTable" ).click(changeMode);
        $( "#dtChart" ).click(changeMode);
        $( "#CSV" ).click(savetab);
        $( "#fromid" ).blur(changeDates);
        $( "#toid" ).blur(changeDates);
        $( "#showmeta" ).click(showmeta);

        $("#nextCounty").click(function() {
            $("#county > option:selected")
                .prop("selected", false)
                .next()
                .prop("selected", true);

            getCounty();
        });
        $("#prevCounty").click(function() {
            $("#county > option:selected")
                .prop("selected", false)
                .prev()
                .prop("selected", true);

            getCounty();
        });
    });

    tabdiv_html = '<div id="tabs"><ul class="navtab">\n';

    $.each(alldata[county], function (sheet, ageranges) {
        allsheets.push(sheet);
        let m = allsheets.indexOf(sheet);
        tabdiv_html += `<li><a href="#tabs_${m}">${sheet}</a></li>\n`;
    });

    tabdiv_html += '</ul></div>\n';

    buildHTML();

    // default to the Cases tab
    active_sheet = "Cases";
    active_sheet_ndx = allsheets.indexOf(active_sheet);

    let phname = `#placeholder_${active_sheet_ndx}`;
    placeholder = $(phname);
    placeholder.bind("plotselected", plotselfun);
    placeholder.bind("plotunselected", plotunselfun);

    bindtip(phname);

    plotAccordingToChoices();
}
function getCounty() {
    // called when new county selected
    county = $("#county option:selected").text();
    plotAccordingToChoices();
}
function setChoice() {
    // an age range checkbox has been set or cleared.
    // just go do the output, which will find out the current settings.
    plotAccordingToChoices();
}

function plotselfun(event, ranges) {
    // called when user selects a date range by dragging pointer.
    // bound to active placeholder during init and in buildhtml
    let frdatd = new Date(ranges.xaxis.from);
    let todatd = new Date(ranges.xaxis.to);
    selfrom = $.plot.formatDate(frdatd, "%Y-%m-%d");
    selto = $.plot.formatDate(todatd, "%Y-%m-%d");
    console.log(`selected date range from ${selfrom} to ${selto}`);
    plotAccordingToChoices();
}
function plotunselfun(event) {
    // called when a date range is un-selected. bound to placeholder in buildhtml
    selfrom = null;
    selto = null;
    console.log(`plot selection canceled - date range set to nulls`);
    plotAccordingToChoices();
}
function plotAccordingToChoices() {
    if (displayType == "c") {
        var plseries = [];

        let smax = null; // max series value
        let tmax = null; // max series total value

        let n = 0;
        let chn = `#choices_${active_sheet_ndx}`;
        $(chn).find("input[type='checkbox']").each(function (key, val) {
            n += 1;
            // console.log(`n: ${n}, key ${key}`);
            if (val.checked) {
                let agerange = val.name;
                // console.log(`val checked for agerange ${agerange}`);

                // get date range from selected range if set, else pickers.
                var fromdate = selfrom ? selfrom : startdate;
                var todate = selto ? selto : enddate;

                if (dodetail) {
                    let ser = {};
                    ser.data = [];
                    for (let v of alldata[county][active_sheet][agerange]) {
                        // stackoverflow.com/questions/12690107/clone-object-without-reference-javascript
                        // var x = Object.create(v);
                        if (v[0] >= fromdate && v[0] <= todate) {
                            // the date values are strings - convert to Date objects
                            var x = [];
                            x[0] = (new Date(v[0]).getTime());
                            if (norm) {
                                // normalize value to per 100k for county
                                x[1] = v[1] * normfac[county];
                           } else {
                                x[1] = v[1];
                           }

                            if (x[1] > smax) {
                                smax = x[1];
                            }
                            ser.data.push(x);
                            // console.log(`${x[0]}, ${x[1]}`);
                        }
                    }
                    ser.color = n;
                    ser.label = agerange;
                    ser.yaxis = 1;
                    plseries.push(ser);
                    // console.log(`${plseries.length}: added ${agerange} ${ser.data.length}`);
                }

                // create accumulated totals for the (active) series, if requested.
                if (dototals) {
                    let newardata = [];
                    let accum = 0.0;
                    let totser = {};
                    totser.color = n;
                    totser.label = `total ${agerange}`;
                    $.each(alldata[county][active_sheet][agerange], function (an, dv) {
                        accum += dv[1];
                        if (dv[0] >= fromdate && dv[0] <= todate) {
                            // dv has date, value. replace value with accumulated total.
                            let newdv = [new Date(dv[0]), accum];
                            newardata.push(newdv);
                           } else if (dv[0] > enddate) {
                               return;
                           }
                    });
                    // value always positive, so last accum is always largest.
                    tmax = accum;
                    totser.data = newardata;
                    totser.yaxis = 2;
                    plseries.push(totser);
                }
            }
        });

        // smax has the max for the active age ranges on active sheets, norm or not
        options.yaxes[0].max = smax * 1.1;
        options.yaxes[1].max = tmax * 1.1;

        plot = $.plot(placeholder, plseries, options);

        // hide the table display cell
        let tabletablecell = document.querySelector(`#tabs_${active_sheet_ndx} .dispistable`);
        tabletablecell.classList.add("hidden");

        // unhide the chart table cell
        let charttablecell = document.querySelector(`#tabs_${active_sheet_ndx} .dispischart`);
        charttablecell.classList.remove("hidden");
    } else {
        // hide the chart table cell
        let charttablecell = document.querySelector(`#tabs_${active_sheet_ndx} .dispischart`);
        charttablecell.classList.add("hidden");

        // create the table html
        let html = tableHTML(county, active_sheet);

        // put the new html in the table table cell, and unhide it
        let tabletablecell = document.querySelector(`#tabs_${active_sheet_ndx} .dispistable`);
        tabletablecell.innerHTML = html;
        tabletablecell.classList.remove("hidden");

        // position to first td with class maxv
        let maxtd = document.querySelector(".maxv");
        if (maxtd) {
            maxtd.scrollIntoView();
        }
    }

    let h3el = document.querySelector(`#tabs_${active_sheet_ndx} > h3`);
    let normornot = norm ? " per 100k" : "";
    let dispCounty = county == "Statewide" ? county : (county + " County");
    h3el.innerText = `${dispCounty} ${active_sheet}${normornot}`;
}
function changeMode(ev) {
    // user selected Chart or Table button
    var who = ev.target.id;

    console.log(`in changeMode for ${who}, active_sheet is ${active_sheet}`);

    if (who == 'dtChart') {
        displayType = "c";
        let tdel = document.querySelector(`#tabs_${active_sheet_ndx} .dispischart`);
        if (tdel && tdel.classList.contains("hidden")) {
            tdel.classList.remove("hidden");
            let tdel2 = document.querySelector(`#tabs_${active_sheet_ndx} .dispistable`);
            if (tdel2) {
                tdel2.classList.add("hidden");
            }
        }
    } else if (who == 'dtTable') {
        displayType = "t";
    }
    plotAccordingToChoices();
}
function setClear(ev) {
    // target id is set_n or clear_n
    let funcid = ev.target.id;
    let func = funcid.substr(0, funcid.length - 2);
    // console.log(`setClear sheet ${active_sheet} funcid ${funcid} func ${func}`);

    let setOrClear = func == "set";
    let chn = `#choices_${active_sheet_ndx}`;
    $(chn).find("input[type='checkbox']").each(function (key, val) {
        val.checked = setOrClear;
    });
    plotAccordingToChoices();
}
function savetab() {
    saveCSV(county, active_sheet);
}
function setOpts(ev) {
    // get the current option settings, set plot options to new values.
    dodetail = $("#detail").prop("checked");
    norm = $("#norm").prop("checked");
    dototals = $("#totals").prop("checked");
 
    plotAccordingToChoices();
}
function showmeta() {
    $("#showmeta").prop("checked", false);
    window.location.href = "meta.html";
}
