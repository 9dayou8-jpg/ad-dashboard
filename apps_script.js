// ============================================================
// Google Apps Script - Web App
// 배포 설정: Execute as "Me", Access "Anyone, even anonymous"
// ============================================================

const SHEET_NAME_OVERALL = "all";  // 전체 데이터 시트
const SHEET_NAME_TEAM = "team";    // 팀 데이터 시트

function doGet(e) {
  const type = e.parameter.type || "overall";

  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let data;

    if (type === "team") {
      data = getSheetData(ss, SHEET_NAME_TEAM);
    } else {
      data = getSheetData(ss, SHEET_NAME_OVERALL);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ status: "ok", data: data }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getSheetData(ss, sheetName) {
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error("시트를 찾을 수 없습니다: " + sheetName);

  const range = sheet.getDataRange();
  const values = range.getValues();

  if (values.length < 2) return [];

  const headers = values[0].map(h => String(h).trim());
  const rows = [];

  for (let i = 1; i < values.length; i++) {
    const row = values[i];
    // 빈 행 스킵
    if (row.every(cell => cell === "" || cell === null)) continue;

    const obj = {};
    headers.forEach((header, idx) => {
      let val = row[idx];
      // 숫자형 변환
      if (typeof val === "number") {
        obj[header] = val;
      } else if (val instanceof Date) {
        obj[header] = Utilities.formatDate(val, "Asia/Seoul", "yyyy-MM-dd");
      } else {
        obj[header] = String(val).trim();
      }
    });
    rows.push(obj);
  }

  return rows;
}
