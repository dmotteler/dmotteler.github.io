function fmtDate(dstr) {
    // expecting dstr like "2028-02-29T23:04", but anything Date 
    // will accept should do. 
    let monam = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];

    let d;
    if (dstr == null) {
        d = new Date();
    } else {
        d = new Date(dstr);
    }
    let longmon = monam[d.getMonth()];
    let day = d.getDate();
    let dmon = d.getMonth() + 1;
    let yr = d.getFullYear();
    let hr = d.getHours();
    let dmin = d.getMinutes();

    let ampm = "AM";
    if (hr > 11) {
        ampm = "PM";
    }
    if (hr > 12) {
        hr -= 12;
    }

    let mons = dmon.toString().padStart(2, 0);
    let days = day.toString().padStart(2, 0);
    let hrs = hr.toString().padStart(2, 0);
    let mins = dmin.toString().padStart(2, 0);

    // e.g., September 9, 2020 12:29PM
    // let datstr = longmon + " " + day + ", " + yr + " " + hrs + ":" + mins + ampm;
    let datstr = `${longmon} ${day}, ${yr} ${hrs}:${mins}${ampm}`;
    // 202009091229
    // let datndx = yr + mons + days + hrs + mins;
    let datndx = `${yr}${mons}${days}${hrs}${mins}`;
    // 2020-09-09
    let ymd = `${yr}-${mons}-${days}`;
    return([datstr,datndx,ymd]);
}
