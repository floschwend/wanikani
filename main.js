const apikey = PropertiesService.getScriptProperties().getProperty("apikey");

String.prototype.addQuery = function (obj) {
  return (this == "" ? "" : `${this}?`) + Object.entries(obj).flatMap(([k, v]) => Array.isArray(v) ? `${k}=` + v.map(e => `${encodeURIComponent(e)}`) : `${k}=${encodeURIComponent(v)}`).join("&");
}

eval(UrlFetchApp.fetch('https://raw.githubusercontent.com/jmespath/jmespath.js/refs/heads/master/jmespath.js').getContentText());

function fetchAssignments() {

  const url = "https://api.wanikani.com/v2/assignments"
  const params = {
    srs_stages: Array(9).fill().map((element, index) => index + 1),
    subject_types: ["kanji","radical","vocabulary"]
  };

  const startUrl = url.addQuery(params).toString();
  var assignments = fetchAssignmentsPage(startUrl);

  var subjectIds = jmespath.search(assignments, "[*].subject_id");
  var subjects = fetchSubjects(subjectIds);

  var spreadSheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadSheet.getSheetByName("Kanji");
  spreadSheet.setActiveSheet(sheet);

  sheet.clear();
  sheet.appendRow(["Kanji", "Meaning", "Reading"]);

  for (const subject of subjects.filter(s => s.type == 'kanji')) {

    const character = subject.data.slug;
    const meaning = jmespath.search(subject.data, 'meanings[?primary==`true`].meaning | [0]')
    const reading = jmespath.search(subject.data, 'readings[?primary==`true`].reading | [0]')

    const rowData = [character, meaning, reading];
    Logger.log("Appending row: " + rowData)

    sheet.appendRow(rowData);
  }
}

function fetchSubjects(ids) {

  var subjects = [];

  const chunkSize = 300;
  for (let i = 0; i < ids.length; i += chunkSize) {
    const chunk = ids.slice(i, i + chunkSize);
    subjects = subjects.concat(fetchSubjectsPage(chunk));
  }

  Logger.log("Found total subjects: " + subjects.length)

  return subjects;
}

function fetchSubjectsPage(ids) {

  const url = "https://api.wanikani.com/v2/subjects"
  const params = {
    ids: ids.map((element, index) => element),
  };

  const pageUrl = url.addQuery(params).toString();

  const data = fetchAndParseUrl(pageUrl);
  var subjects = jmespath.search(data, 'data[*].{type: object, data: data}');

  Logger.log("Found subjects in page: " + subjects.length)

  return subjects;
}


function fetchAssignmentsPage(url) {

  const data = fetchAndParseUrl(url);

  var assignments = jmespath.search(data, 'data[*].data');

  Logger.log("Found assignments in page: " + assignments.length)

  if (data.pages.next_url?.length > 0) {
    assignments = assignments.concat(fetchAssignmentsPage(data.pages.next_url));
  }

  return assignments;
}

function fetchAndParseUrl(url) {

  Logger.log("Fetching: " + url);

  try {
    const options = {
      headers: { 'Wanikani-Revision': '20170710', Authorization: 'Bearer ' + apikey }
    };

    const response = UrlFetchApp.fetch(url, options);
    const data = JSON.parse(response.getContentText());

    return data;

  } catch (f) {
    Logger.log(f.message);
  }

}

