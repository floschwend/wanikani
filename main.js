String.prototype.addQuery = function (obj) {
    return (this == "" ? "" : `${this}?`) + Object.entries(obj).flatMap(([k, v]) => Array.isArray(v) ? `${k}=` + v.map(e => `${encodeURIComponent(e)}`) : `${k}=${encodeURIComponent(v)}`).join("&");
}

eval(UrlFetchApp.fetch('https://raw.githubusercontent.com/jmespath/jmespath.js/refs/heads/master/jmespath.js').getContentText());

function fetchKanjis() {

    url = "https://api.wanikani.com/v2/assignments"
    const params = {
        srs_stages: Array(9).fill().map((element, index) => index + 1),
        subject_types: "kanji"
    };

    startUrl = url.addQuery(params).toString();
    subjects = fetchKanjiIdsPage(startUrl);

    var ids = jmespath.search(subjects, "[*].subject_id");
    var subjects = fetchSubjects(ids);

    for (const subject of subjects) {
        var sheet = SpreadsheetApp.getActiveSheet();

        var character = subject.slug;
        var meaning = jmespath.search(subject, 'meanings[?primary==`true`].meaning | [0]')

        var rowData = [character, meaning];
        Logger.log("Appending row: " + rowData)

        sheet.appendRow(rowData);
    }
}

function fetchSubjects(ids) {

    subjects = [];

    const chunkSize = 500;
    for (let i = 0; i < ids.length; i += chunkSize) {
        const chunk = ids.slice(i, i + chunkSize);
        subjects = subjects.concat(fetchSubjectsPage(chunk));
    }

    Logger.log("Found total subjects: " + subjects.length)

    return subjects;
}

function fetchSubjectsPage(ids) {

    url = "https://api.wanikani.com/v2/subjects"
    const params = {
        ids: ids.map((element, index) => element),
    };

    pageUrl = url.addQuery(params).toString();

    const data = fetchAndParseUrl(pageUrl);
    var subjects = jmespath.search(data, 'data[*].data');

    Logger.log("Found subjects in page: " + subjects.length)

    return subjects;
}

function fetchKanjiIdsPage(url) {

    const data = fetchAndParseUrl(url);

    subjects = jmespath.search(data, 'data[*].data');

    if (data.pages.next_url?.length > 0) {
        subjects = subjects.concat(fetchKanjiIdsPage(data.pages.next_url));
    }

    return subjects;
}

function fetchAndParseUrl(url) {

    Logger.log("Fetching: " + url);

    try {
        const options = {
            headers: { 'Wanikani-Revision': '20170710', Authorization: 'Bearer <API-KEY>' }
        };

        const response = UrlFetchApp.fetch(url, options);
        const data = JSON.parse(response.getContentText());

        return data;

    } catch (f) {
        Logger.log(f.message);
    }

}

