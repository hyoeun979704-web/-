/**
 * 청첩장 방명록 · RSVP → 구글시트 기록 (Google Apps Script)
 *
 * [연결 방법]
 * 1) 구글시트 열기:
 *    https://docs.google.com/spreadsheets/d/1_3axp-rTi2Y642MHc0QMExkNZlk61TI8diGYhr3exCs/edit
 * 2) 상단 메뉴 [확장 프로그램] → [Apps Script]
 * 3) 기본 코드를 지우고 이 파일 전체를 붙여넣고 저장
 * 4) 오른쪽 위 [배포] → [새 배포] → 유형 "웹 앱"
 *      - 실행: 나
 *      - 액세스 권한: "모든 사용자"
 *    → 배포하면 나오는 "웹 앱 URL"을 복사
 * 5) 그 URL을 app.js 상단의  var GAS_URL = "";  에 붙여넣으면 끝
 *    (방명록·RSVP가 이 시트의 '방명록' / 'RSVP' 탭에 자동 기록됩니다)
 */

var SHEET_ID = '1_3axp-rTi2Y642MHc0QMExkNZlk61TI8diGYhr3exCs';

function getSheet(name, headers) {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(headers); }
  return sh;
}

// 방명록 등록 / RSVP 제출 (POST)
function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    if (d.type === 'guestbook') {
      getSheet('방명록', ['시간', '이름', '메시지'])
        .appendRow([new Date(), d.name || '익명', d.msg || '']);
    } else if (d.type === 'rsvp') {
      getSheet('RSVP', ['시간', '구분', '참석 여부', '식사', '성함', '인원'])
        .appendRow([new Date(), d.side, d.attending, d.meal, d.name, d.count]);
    }
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

// 방명록 목록 조회 (GET, JSONP)
function doGet(e) {
  var sh = getSheet('방명록', ['시간', '이름', '메시지']);
  var values = sh.getDataRange().getValues();
  values.shift(); // 헤더 제거
  var list = values.filter(function (r) { return r[2]; }).map(function (r) {
    var dt = r[0] instanceof Date ? r[0] : new Date(r[0]);
    return { date: Utilities.formatDate(dt, 'GMT+9', 'yyyy.MM.dd'), name: r[1], msg: r[2] };
  });
  var out = JSON.stringify(list);
  var cb = e && e.parameter && e.parameter.callback;
  if (cb) return ContentService.createTextOutput(cb + '(' + out + ')')
    .setMimeType(ContentService.MimeType.JAVASCRIPT);
  return ContentService.createTextOutput(out).setMimeType(ContentService.MimeType.JSON);
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
