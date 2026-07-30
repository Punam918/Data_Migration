from __future__ import annotations

from pathlib import Path

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
            --panel: #121a33;
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
        .wrap { max-width: 1100px; margin: 0 auto; padding: 32px 20px 48px; }
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
        .toolbar {
            display: flex; gap: 12px; flex-wrap: wrap; align-items: center; justify-content: space-between;
            margin: 18px 0;
        }
        .filters {
            display: grid;
            grid-template-columns: minmax(220px, 1fr) auto;
            gap: 12px;
            width: 100%;
            margin-top: 8px;
        }
        .search {
            width: 100%;
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.05);
            color: var(--text);
            outline: none;
        }
        .search::placeholder { color: var(--muted); }
        .filter-bar { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
        .filter-btn {
            appearance: none; border: 1px solid var(--border); background: rgba(255,255,255,0.05);
            color: var(--text); box-shadow: none; font-weight: 600; padding: 10px 14px; border-radius: 14px;
            cursor: pointer;
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
        .card {
            background: rgba(18, 26, 51, 0.86); border: 1px solid var(--border); border-radius: 18px;
            padding: 18px; display: grid; gap: 12px;
        }
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
        .empty {
            padding: 28px; text-align: center; border-radius: 18px; border: 1px dashed var(--border);
            color: var(--muted); background: rgba(255,255,255,0.03);
        }
        .footer { margin-top: 24px; color: var(--muted); font-size: 13px; }
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
                <button id="refreshBtn">Refresh patches</button>
                <button id="applyAllBtn" class="secondary">Apply filtered patches</button>
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
        <div id="patches" class="grid"></div>

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
        let allPatches = [];
        let activeFilter = 'all';

        function setStatus(message, kind) {
            statusEl.textContent = message;
            statusEl.className = 'state' + (kind ? ' ' + kind : '');
        }

        async function loadPatches() {
            setStatus('Loading patches...', '');
            patchesEl.innerHTML = '';
            try {
                const response = await fetch('/governance/patches');
                if (!response.ok) throw new Error('HTTP ' + response.status);
                allPatches = await response.json();
                renderPatches();
                setStatus(allPatches.length + ' patch(es) loaded.', 'ok');
            } catch (error) {
                patchesEl.innerHTML = '<div class="empty">Failed to load patches.</div>';
                countsEl.innerHTML = '';
                setStatus('Error loading patches: ' + error.message, 'error');
            }
        }

        function matchesQuery(patch, query) {
            if (!query) return true;
            const haystack = [patch.id, patch.title, patch.description, patch.status, JSON.stringify(patch.metadata || {})].join(' ').toLowerCase();
            return haystack.indexOf(query.toLowerCase()) !== -1;
        }

        function matchesFilter(patch) {
            return activeFilter === 'all' || patch.status === activeFilter;
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
            const query = searchInput.value.trim();
            const filtered = allPatches.filter((patch) => matchesQuery(patch, query) && matchesFilter(patch));
            renderCounts(allPatches);

            if (!filtered.length) {
                patchesEl.innerHTML = '<div class="empty">No patches match the current search or status filter.</div>';
                return;
            }

            patchesEl.innerHTML = filtered.map((patch) => {
                const meta = JSON.stringify(patch.metadata || {}, null, 2);
                const applied = patch.status === 'applied';
                return '\n          <article class="card" data-patch-id="' + patch.id + '">\n            <div class="card-head">\n              <div>\n                <h2 class="title">' + escapeHtml(patch.title || patch.id) + '</h2>\n                <p class="desc">' + escapeHtml(patch.description || '') + '</p>\n              </div>\n              <div class="row">\n                <span class="pill ' + (applied ? 'good' : 'warn') + '">' + escapeHtml(patch.status || 'unknown') + '</span>\n                <span class="pill">' + escapeHtml(patch.id) + '</span>\n              </div>\n            </div>\n            <div class="row">\n              <span class="pill">Created: ' + escapeHtml(patch.created_at || '-') + '</span>\n              <span class="pill">Applied: ' + escapeHtml(patch.applied_at || '-') + '</span>\n            </div>\n            <pre>' + escapeHtml(meta) + '</pre>\n            <div class="row">\n              <button ' + (applied ? 'disabled' : '') + ' onclick="applyPatch(\'' + patch.id + '\')">' + (applied ? 'Applied' : 'Apply patch') + '</button>\n            </div>\n          </article>\n        ';
            }).join('');
        }

        async function applyPatch(patchId) {
            setStatus('Applying patch ' + patchId + '...', '');
            try {
                const response = await fetch('/governance/patches/' + patchId + '/apply', { method: 'POST' });
                if (!response.ok) throw new Error('HTTP ' + response.status);
                setStatus('Patch ' + patchId + ' applied.', 'ok');
                await loadPatches();
            } catch (error) {
                setStatus('Failed to apply patch: ' + error.message, 'error');
            }
        }

        async function applyFiltered() {
            const query = searchInput.value.trim();
            const ids = allPatches
                .filter((patch) => patch.status !== 'applied' && matchesQuery(patch, query) && matchesFilter(patch))
                .map((patch) => patch.id)
                .filter(Boolean);
            if (!ids.length) {
                setStatus('No patches to apply.', '');
                return;
            }
            if (!confirm('Apply ' + ids.length + ' patch(es)?')) return;
            for (const id of ids) {
                await applyPatch(id);
            }
        }

        function setActiveFilter(filterName) {
            activeFilter = filterName;
            filterButtons.forEach((button) => {
                button.classList.toggle('active', button.dataset.filter === filterName);
            });
            renderPatches();
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
        searchInput.addEventListener('input', renderPatches);
        filterButtons.forEach((button) => button.addEventListener('click', () => setActiveFilter(button.dataset.filter)));
        loadPatches();
    </script>
</body>
</html>"""


@router.get("/governance/ui", response_class=HTMLResponse)
def governance_ui() -> HTMLResponse:
        return HTMLResponse(_render_ui())


@router.get("/governance/patches")
def list_patches(limit: int = 100):
        root = Path("./var/governance")
        mgr = PatchManager(root)
        return mgr.list_patches()[:limit]


@router.post("/governance/patches/{patch_id}/apply")
def apply_patch(patch_id: str):
        root = Path("./var/governance")
        mgr = PatchManager(root)
        rec = mgr.apply_patch(patch_id)
        if rec is None:
                raise HTTPException(status_code=404, detail="patch not found")
        return rec
