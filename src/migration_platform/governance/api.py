from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from .patcher import PatchManager

router = APIRouter()


def _render_ui() -> str:
        return """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Patch Review</title>
    <style>
        :root {
            color-scheme: dark;
            --bg: #0b1020;
            --text: #e5ecff;
            --muted: #9fb0d0;
            --accent: #7dd3fc;
            --good: #34d399;
            --warn: #fbbf24;
            --bad: #fb7185;
            --border: rgba(159, 176, 208, 0.18);
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Inter, Segoe UI, Arial, sans-serif;
            background:
                radial-gradient(circle at top left, rgba(167, 139, 250, 0.15), transparent 28%),
                radial-gradient(circle at top right, rgba(125, 211, 252, 0.12), transparent 24%),
                linear-gradient(180deg, #070b16 0%, var(--bg) 100%);
            color: var(--text);
            min-height: 100vh;
        }
        .wrap { max-width: 1280px; margin: 0 auto; padding: 32px 20px 48px; }
        .hero {
            display: flex; gap: 16px; justify-content: space-between; align-items: end;
            margin-bottom: 22px; padding: 24px; background: rgba(18, 26, 51, 0.78);
            border: 1px solid var(--border); border-radius: 20px; backdrop-filter: blur(8px);
            box-shadow: 0 20px 80px rgba(0,0,0,.25);
        }
        h1 { margin: 0 0 8px; font-size: clamp(28px, 4vw, 42px); }
        .sub { margin: 0; color: var(--muted); max-width: 70ch; line-height: 1.5; }
        .meta { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
        .chip { padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: var(--muted); font-size: 13px; }
        .toolbar { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; justify-content: space-between; margin: 18px 0; }
        .filters {
            display: grid; grid-template-columns: minmax(220px, 1fr) auto; gap: 12px; width: 100%; margin-top: 8px;
        }
        .search {
            width: 100%; padding: 12px 14px; border-radius: 14px; border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.05); color: var(--text); outline: none;
        }
        .search::placeholder { color: var(--muted); }
        .filter-bar { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
        .filter-btn {
            appearance: none; border: 1px solid var(--border); background: rgba(255,255,255,0.05);
            color: var(--text); box-shadow: none; font-weight: 600; padding: 10px 14px; border-radius: 14px; cursor: pointer;
        }
        .filter-btn.active { border-color: rgba(125, 211, 252, 0.45); background: rgba(125, 211, 252, 0.14); }
        button {
            appearance: none; border: 0; cursor: pointer; border-radius: 14px; padding: 11px 16px;
            font-weight: 700; color: #08111f; background: linear-gradient(135deg, var(--accent), #dbeafe);
            box-shadow: 0 12px 30px rgba(125, 211, 252, 0.18);
        }
        button.secondary { color: var(--text); background: rgba(255,255,255,0.06); border: 1px solid var(--border); box-shadow: none; }
        button:disabled { opacity: 0.55; cursor: not-allowed; }
        .grid { display: grid; gap: 14px; }
        .layout { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr); gap: 16px; align-items: start; }
        .card, .drawer, .modal {
            background: rgba(18, 26, 51, 0.86); border: 1px solid var(--border); border-radius: 18px;
        }
        .card { padding: 18px; display: grid; gap: 12px; }
        .drawer { position: sticky; top: 18px; padding: 18px; display: grid; gap: 12px; }
        .drawer h2 { margin: 0; font-size: 18px; }
        .card-head { display: flex; justify-content: space-between; gap: 12px; align-items: start; }
        .title { margin: 0; font-size: 18px; }
        .desc { margin: 0; color: var(--muted); line-height: 1.5; }
        .row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
        .pill {
            padding: 6px 10px; border-radius: 999px; font-size: 12px; border: 1px solid var(--border);
            color: var(--muted); background: rgba(255,255,255,0.04);
        }
        .pill.good { color: var(--good); border-color: rgba(52, 211, 153, 0.35); background: rgba(52, 211, 153, 0.08); }
        .pill.warn { color: var(--warn); border-color: rgba(251, 191, 36, 0.35); background: rgba(251, 191, 36, 0.08); }
        .pill.bad { color: var(--bad); border-color: rgba(251, 113, 133, 0.35); background: rgba(251, 113, 133, 0.08); }
        .pill.neutral { color: var(--accent); border-color: rgba(125, 211, 252, 0.35); background: rgba(125, 211, 252, 0.08); }
        code { background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 8px; }
        pre {
            margin: 0; padding: 14px; overflow: auto; border-radius: 14px; border: 1px solid var(--border);
            background: rgba(0,0,0,0.18); color: #d7e3ff; font-size: 12px; line-height: 1.5;
        }
        .state { color: var(--muted); }
        .state.error { color: var(--bad); }
        .state.ok { color: var(--good); }
        .count-line { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0 4px; }
        .empty, .muted-box {
            padding: 14px; border-radius: 14px; border: 1px dashed var(--border);
            color: var(--muted); background: rgba(255,255,255,0.03); line-height: 1.5;
        }
        .muted-box strong { color: var(--text); }
        .drawer pre { max-height: 240px; }
        .footer { margin-top: 24px; color: var(--muted); font-size: 13px; }
        .modal-backdrop {
            position: fixed; inset: 0; background: rgba(3, 7, 18, 0.72); display: none; align-items: center; justify-content: center;
            padding: 20px; z-index: 20;
        }
        .modal-backdrop.open { display: flex; }
        .modal {
            width: min(620px, 100%); padding: 20px; box-shadow: 0 30px 120px rgba(0, 0, 0, 0.55); display: grid; gap: 14px;
        }
        .modal h3 { margin: 0; font-size: 22px; }
        .modal p { margin: 0; color: var(--muted); line-height: 1.5; }
        .actions { display: flex; gap: 10px; justify-content: flex-end; flex-wrap: wrap; }
        @media (max-width: 980px) {
            .layout { grid-template-columns: 1fr; }
            .drawer { position: static; }
        }
    </style>
</head>
<body>
    <div class="wrap">
        <section class="hero">
            <div>
                <h1>Patch Review Desk</h1>
                <p class="sub">Review suggested patches produced by the orchestration runner, inspect metadata, and apply approved patches through the governance API.</p>
            </div>
            <div class="meta">
                <span class="chip">GET <code>/governance/patches</code></span>
                <span class="chip">POST <code>/governance/patches/{id}/apply</code></span>
            </div>
        </section>

        <div class="toolbar">
            <div class="row">
                <button id="refreshBtn" type="button">Refresh patches</button>
                <button id="applyAllBtn" class="secondary" type="button">Apply filtered patches</button>
            </div>
            <div id="status" class="state">Ready.</div>
        </div>

        <div class="filters">
            <input id="searchInput" class="search" type="search" placeholder="Search title, description, metadata, or patch id" />
            <div class="filter-bar" role="tablist" aria-label="Patch status filters">
                <button class="filter-btn active" data-filter="all" type="button">All</button>
                <button class="filter-btn" data-filter="suggested" type="button">Suggested</button>
                <button class="filter-btn" data-filter="applied" type="button">Applied</button>
            </div>
        </div>

        <div id="counts" class="count-line"></div>

        <div class="layout">
            <div id="patches" class="grid"></div>
            <aside class="drawer" id="drawer">
                <h2>Patch preview</h2>
                <div id="drawerMeta" class="drawer-meta">
                    <div class="muted-box">Select a patch to inspect its details, metadata, and remediation preview.</div>
                </div>
                <div class="row">
                    <button id="drawerApplyBtn" class="secondary" type="button" disabled>Apply selected patch</button>
                </div>
            </aside>
        </div>

        <div id="confirmModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-hidden="true">
            <div class="modal">
                <h3>Confirm patch application</h3>
                <p id="confirmMessage">Are you sure you want to apply this patch?</p>
                <div class="muted-box" id="confirmPreview"></div>
                <div class="actions">
                    <button id="confirmCancelBtn" class="secondary" type="button">Cancel</button>
                    <button id="confirmOkBtn" type="button">Apply patch</button>
                </div>
            </div>
        </div>

        <div class="footer">This UI uses the same API endpoints as the CLI for a single source of truth.</div>
    </div>

    <script>
        const statusEl = document.getElementById('status');
        const patchesEl = document.getElementById('patches');
        const refreshBtn = document.getElementById('refreshBtn');
        const applyAllBtn = document.getElementById('applyAllBtn');
        const searchInput = document.getElementById('searchInput');
        const filterButtons = Array.from(document.querySelectorAll('[data-filter]'));
        const countsEl = document.getElementById('counts');
        const drawerMeta = document.getElementById('drawerMeta');
        const drawerApplyBtn = document.getElementById('drawerApplyBtn');
        const confirmModal = document.getElementById('confirmModal');
        const confirmMessage = document.getElementById('confirmMessage');
        const confirmPreview = document.getElementById('confirmPreview');
        const confirmCancelBtn = document.getElementById('confirmCancelBtn');
        const confirmOkBtn = document.getElementById('confirmOkBtn');
        let allPatches = [];
        let activeFilter = 'all';
        let selectedPatch = null;
        let pendingApplyIds = [];

        function setStatus(message, kind) {
            statusEl.textContent = message;
            statusEl.className = 'state' + (kind ? ' ' + kind : '');
        }

        function getFilterUrl() {
            const url = new URL('/governance/patches', window.location.origin);
            const query = searchInput.value.trim();
            if (query) url.searchParams.set('q', query);
            if (activeFilter !== 'all') url.searchParams.set('status', activeFilter);
            return url;
        }

        async function loadPatches() {
            setStatus('Loading patches...', '');
            patchesEl.innerHTML = '';
            try {
                const response = await fetch(getFilterUrl().toString());
                if (!response.ok) throw new Error('HTTP ' + response.status);
                allPatches = await response.json();
                if (selectedPatch && !allPatches.some((patch) => patch.id === selectedPatch.id)) {
                    selectedPatch = allPatches.length ? allPatches[0] : null;
                }
                renderPatches();
                setStatus(allPatches.length + ' patch(es) loaded.', 'ok');
            } catch (error) {
                patchesEl.innerHTML = '<div class="empty">Failed to load patches.</div>';
                countsEl.innerHTML = '';
                renderDrawer(null);
                setStatus('Error loading patches: ' + error.message, 'error');
            }
        }

        function renderCounts(patches) {
            const counts = patches.reduce((acc, patch) => {
                acc.total += 1;
                acc[patch.status || 'unknown'] = (acc[patch.status || 'unknown'] || 0) + 1;
                return acc;
            }, { total: 0 });
            countsEl.innerHTML = [
                '<span class="pill neutral">Total: ' + counts.total + '</span>',
                '<span class="pill warn">Suggested: ' + (counts.suggested || 0) + '</span>',
                '<span class="pill good">Applied: ' + (counts.applied || 0) + '</span>',
            ].join('');
        }

        function renderPatches() {
            renderCounts(allPatches);
            if (!allPatches.length) {
                patchesEl.innerHTML = '<div class="empty">No patches match the current search or status filter.</div>';
                renderDrawer(null);
                return;
            }

            patchesEl.innerHTML = allPatches.map((patch) => {
                const meta = JSON.stringify(patch.metadata || {}, null, 2);
                const applied = patch.status === 'applied';
                const active = selectedPatch && selectedPatch.id === patch.id;
                return '\n          <article class="card" data-patch-id="' + patch.id + '">\n            <div class="card-head">\n              <div>\n                <h2 class="title">' + escapeHtml(patch.title || patch.id) + '</h2>\n                <p class="desc">' + escapeHtml(patch.description || '') + '</p>\n              </div>\n              <div class="row">\n                <span class="pill ' + (applied ? 'good' : 'warn') + '">' + escapeHtml(patch.status || 'unknown') + '</span>\n                <span class="pill">' + escapeHtml(patch.id) + '</span>\n              </div>\n            </div>\n            <div class="row">\n              <span class="pill">Created: ' + escapeHtml(patch.created_at || '-') + '</span>\n              <span class="pill">Applied: ' + escapeHtml(patch.applied_at || '-') + '</span>\n            </div>\n            <pre>' + escapeHtml(meta) + '</pre>\n            <div class="row">\n              <button class="secondary" type="button" onclick="selectPatch(\'' + patch.id + '\')">' + (active ? 'Selected' : 'View details') + '</button>\n              <button ' + (applied ? 'disabled' : '') + ' type="button" onclick="requestApply(\'' + patch.id + '\')">' + (applied ? 'Applied' : 'Apply patch') + '</button>\n            </div>\n          </article>\n        ';
            }).join('');

            if (!selectedPatch && allPatches.length) {
                selectedPatch = allPatches[0];
            }
            renderDrawer(selectedPatch);
        }

        function renderDrawer(patch) {
            selectedPatch = patch || null;
            if (!patch) {
                drawerMeta.innerHTML = '<div class="muted-box">Select a patch to inspect its details, metadata, and remediation preview.</div>';
                drawerApplyBtn.disabled = true;
                drawerApplyBtn.textContent = 'Apply selected patch';
                return;
            }

            const preview = buildPreview(patch);
            drawerMeta.innerHTML = '\n        <div class="row">\n          <span class="pill ' + (patch.status === 'applied' ? 'good' : 'warn') + '">' + escapeHtml(patch.status || 'unknown') + '</span>\n          <span class="pill neutral">' + escapeHtml(patch.id) + '</span>\n        </div>\n        <div><strong>' + escapeHtml(patch.title || 'Untitled patch') + '</strong></div>\n        <div class="desc">' + escapeHtml(patch.description || '') + '</div>\n        <div class="row">\n          <span class="pill">Created: ' + escapeHtml(patch.created_at || '-') + '</span>\n          <span class="pill">Applied: ' + escapeHtml(patch.applied_at || '-') + '</span>\n        </div>\n        <div class="muted-box"><strong>Preview</strong><br />' + escapeHtml(preview.summary) + '</div>\n        <pre>' + escapeHtml(JSON.stringify(patch.metadata || {}, null, 2)) + '</pre>\n      ';
            drawerApplyBtn.disabled = patch.status === 'applied';
            drawerApplyBtn.textContent = patch.status === 'applied' ? 'Already applied' : 'Apply selected patch';
        }

        function buildPreview(patch) {
            const metadata = patch.metadata || {};
            if (metadata.type === 'unique_constraint') {
                const columns = Array.isArray(metadata.columns) ? metadata.columns.join(', ') : 'unknown columns';
                return { summary: 'Suggested SQL preview: ALTER TABLE <table> ADD CONSTRAINT <name> UNIQUE (' + columns + ');' };
            }
            if (metadata.type === 'not_null') {
                return { summary: 'Suggested SQL preview: UPDATE <table> SET <column> = <backfill>; then ALTER TABLE <table> ALTER COLUMN <column> SET NOT NULL;' };
            }
            if (metadata.type === 'investigation') {
                return { summary: 'Suggested action: inspect source partitions, compare anomaly rows, and validate upstream feeds.' };
            }
            return { summary: 'Review the patch metadata and apply after verifying the expected change.' };
        }

        function openConfirmModal(message, preview, ids) {
            pendingApplyIds = ids.slice();
            confirmMessage.textContent = message;
            confirmPreview.textContent = preview;
            confirmModal.classList.add('open');
            confirmModal.setAttribute('aria-hidden', 'false');
        }

        function closeConfirmModal() {
            pendingApplyIds = [];
            confirmModal.classList.remove('open');
            confirmModal.setAttribute('aria-hidden', 'true');
        }

        async function applyPatch(patchId) {
            const response = await fetch('/governance/patches/' + patchId + '/apply', { method: 'POST' });
            if (!response.ok) throw new Error('HTTP ' + response.status);
        }

        function requestApply(patchId) {
            const patch = allPatches.find((item) => item.id === patchId);
            if (!patch || patch.status === 'applied') return;
            openConfirmModal(
                'Apply patch ' + patch.id + ' (' + (patch.title || 'untitled') + ')?',
                buildPreview(patch).summary,
                [patch.id]
            );
        }

        function applyFiltered() {
            const ids = allPatches.filter((patch) => patch.status !== 'applied').map((patch) => patch.id);
            if (!ids.length) {
                setStatus('No patches to apply.', '');
                return;
            }
            const preview = ids.slice(0, 3).join(', ') + (ids.length > 3 ? ', ...' : '');
            openConfirmModal('Apply ' + ids.length + ' filtered patch(es)?', preview, ids);
        }

        function setActiveFilter(filterName) {
            activeFilter = filterName;
            filterButtons.forEach((button) => {
                button.classList.toggle('active', button.dataset.filter === filterName);
            });
            loadPatches();
        }

        function escapeHtml(text) {
            return String(text)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        refreshBtn.addEventListener('click', loadPatches);
        applyAllBtn.addEventListener('click', applyFiltered);
        searchInput.addEventListener('input', loadPatches);
        filterButtons.forEach((button) => button.addEventListener('click', () => setActiveFilter(button.dataset.filter)));
        drawerApplyBtn.addEventListener('click', () => {
            if (selectedPatch && selectedPatch.status !== 'applied') {
                requestApply(selectedPatch.id);
            }
        });
        confirmCancelBtn.addEventListener('click', closeConfirmModal);
        confirmModal.addEventListener('click', (event) => {
            if (event.target === confirmModal) {
                closeConfirmModal();
            }
        });
        confirmOkBtn.addEventListener('click', async () => {
            if (!pendingApplyIds.length) return;
            try {
                setStatus('Applying ' + pendingApplyIds.length + ' patch(es)...', '');
                closeConfirmModal();
                for (const patchId of pendingApplyIds) {
                    await applyPatch(patchId);
                }
                setStatus('Applied ' + pendingApplyIds.length + ' patch(es).', 'ok');
                await loadPatches();
            } catch (error) {
                setStatus('Failed to apply patch: ' + error.message, 'error');
            }
        });

        loadPatches();
    </script>
</body>
</html>"""


@router.get("/governance/ui", response_class=HTMLResponse)
def governance_ui() -> HTMLResponse:
        return HTMLResponse(_render_ui())


@router.get("/governance/patches")
def list_patches(limit: int = 100, q: Optional[str] = None, status: Optional[str] = None):
        root = Path("./var/governance")
        mgr = PatchManager(root)
        patches = mgr.list_patches()
        if q:
                query = q.lower()
                patches = [
                        patch for patch in patches
                        if query in str(patch.get("id", "")).lower()
                        or query in str(patch.get("title", "")).lower()
                        or query in str(patch.get("description", "")).lower()
                        or query in str(patch.get("status", "")).lower()
                        or query in str(patch.get("metadata", "")).lower()
                ]
        if status and status != "all":
                patches = [patch for patch in patches if patch.get("status") == status]
        return patches[:limit]


@router.post("/governance/patches/{patch_id}/apply")
def apply_patch(patch_id: str):
        root = Path("./var/governance")
        mgr = PatchManager(root)
        rec = mgr.apply_patch(patch_id)
        if rec is None:
                raise HTTPException(status_code=404, detail="patch not found")
        return rec
