// ============================================================
// 新闻公告管理系统 — 后台交互脚本
// ============================================================

function getCSRF() {
  var cookie = document.cookie.match(/csrftoken=([^;]+)/);
  return cookie ? cookie[1] : "";
}

function postJSON(url, data) {
  return fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRF(), "X-Requested-With": "XMLHttpRequest" },
    body: data,
  }).then(function (r) { return r.json(); });
}

function show(id, msg) {
  var el = document.getElementById(id);
  if (el) { el.textContent = msg; el.style.display = "block"; }
}
function hide(id) {
  var el = document.getElementById(id);
  if (el) { el.style.display = "none"; }
}

// ============================================================
// 栏目管理弹窗
// ============================================================
function openTypeModal(id, name) {
  hide("typeModalError");
  document.getElementById("typeId").value = id || "";
  document.getElementById("typeName").value = name || "";
  document.getElementById("typeModalTitle").textContent = id ? "编辑栏目" : "新增栏目";
  document.getElementById("typeModal").style.display = "flex";
  document.getElementById("typeName").focus();
}
function closeTypeModal() { document.getElementById("typeModal").style.display = "none"; }

function saveType() {
  var id = document.getElementById("typeId").value;
  var name = document.getElementById("typeName").value.trim();
  if (!name) { show("typeModalError", "栏目名称不能为空"); return; }
  var url = id ? "/admin/type/" + id + "/edit/" : "/admin/type/add/";
  var data = new FormData(); data.append("type_name", name);
  var btn = document.getElementById("typeSaveBtn");
  btn.disabled = true; btn.textContent = "保存中...";
  postJSON(url, data).then(function (res) {
    if (res.ok) { location.reload(); }
    else { show("typeModalError", res.msg); btn.disabled = false; btn.textContent = "保存"; }
  });
}

function deleteType(id, name) {
  if (!confirm("确定删除栏目「" + name + "」？")) return;
  postJSON("/admin/type/" + id + "/delete/", new FormData()).then(function (res) {
    if (res.ok) { location.reload(); } else { alert(res.msg); }
  });
}

// ============================================================
// 新闻公告弹窗
// ============================================================
function openNewsModal(id) {
  hide("newsModalError");
  document.getElementById("newsId").value = id || "";
  document.getElementById("newsTitle").value = "";
  document.getElementById("newsContent").value = "";
  document.getElementById("newsAuthor").value = "";
  document.getElementById("newsType").value = "";
  document.getElementById("newsModalTitle").textContent = id ? "编辑公告" : "新增公告";
  document.getElementById("newsModal").style.display = "flex";
  document.getElementById("newsTitle").focus();
}

function openNewsModalFromRow(btn) {
  var row = btn.closest("tr");
  var id = row.getAttribute("data-news-id");
  var title = row.getAttribute("data-title");
  var content = row.getAttribute("data-content");
  var author = row.getAttribute("data-author");
  var typeId = row.getAttribute("data-type-id");

  hide("newsModalError");
  document.getElementById("newsId").value = id;
  document.getElementById("newsTitle").value = title;
  document.getElementById("newsContent").value = content;
  document.getElementById("newsAuthor").value = author;
  document.getElementById("newsType").value = typeId;
  document.getElementById("newsModalTitle").textContent = "编辑公告";
  document.getElementById("newsModal").style.display = "flex";
  document.getElementById("newsTitle").focus();
}

function closeNewsModal() { document.getElementById("newsModal").style.display = "none"; }

function saveNews() {
  var id = document.getElementById("newsId").value;
  var title = document.getElementById("newsTitle").value.trim();
  var content = document.getElementById("newsContent").value.trim();
  var author = document.getElementById("newsAuthor").value.trim();
  var typeId = document.getElementById("newsType").value;
  if (!title) { show("newsModalError", "标题不能为空"); return; }
  if (!typeId) { show("newsModalError", "请选择所属栏目"); return; }

  var url = id ? "/admin/news/" + id + "/edit/" : "/admin/news/add/";
  var data = new FormData();
  data.append("title", title);
  data.append("content", content);
  data.append("author", author);
  data.append("type_id", typeId);

  var btn = document.getElementById("newsSaveBtn");
  btn.disabled = true; btn.textContent = "保存中...";
  postJSON(url, data).then(function (res) {
    if (res.ok) { location.reload(); }
    else { show("newsModalError", res.msg); btn.disabled = false; btn.textContent = "保存"; }
  });
}

function deleteNews(id, title) {
  if (!confirm("确定删除公告「" + title + "」？")) return;
  postJSON("/admin/news/" + id + "/delete/", new FormData()).then(function (res) {
    if (res.ok) { location.reload(); } else { alert(res.msg); }
  });
}

function toggleSelectAll() {
  var checked = document.getElementById("selectAll").checked;
  document.querySelectorAll(".news-check").forEach(function (c) { c.checked = checked; });
}

function batchDelete() {
  var checks = document.querySelectorAll(".news-check:checked");
  if (checks.length === 0) { alert("请至少选择一条公告"); return; }
  if (!confirm("确定删除选中的 " + checks.length + " 条公告？")) return;
  var data = new FormData();
  checks.forEach(function (c) { data.append("ids[]", c.value); });
  postJSON("/admin/news/batch-delete/", data).then(function (res) {
    if (res.ok) { location.reload(); } else { alert(res.msg); }
  });
}

// 点击遮罩关闭弹窗
document.getElementById("typeModal") && document.getElementById("typeModal").addEventListener("click", function (e) { if (e.target === this) closeTypeModal(); });
document.getElementById("newsModal") && document.getElementById("newsModal").addEventListener("click", function (e) { if (e.target === this) closeNewsModal(); });

// ESC 关闭
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") { closeTypeModal(); closeNewsModal(); }
});
