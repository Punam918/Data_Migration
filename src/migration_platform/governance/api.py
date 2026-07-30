from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path

from .patcher import PatchManager

router = APIRouter()


def _render_ui() -> str:
        return """<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Patch Review</title>
    <style>
        :root {
            color-scheme: dark;
            --bg: #0b1020;
            --panel: #121a33;
            --panel-2: #18213f;
            --text: #e5ecff;
            --muted: #9fb0d0;
            --accent: #7dd3fc;
            --accent-2: #a78bfa;
            --good: #34d399;
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
        button {
            appearance: none; border: 0; cursor: pointer; border-radius: 14px; padding: 11px 16px;
            font-weight: 700; color: #08111f; background: linear-gradient(135deg, var(--accent), #dbeafe);
            box-shadow: 0 12px 30px rgba(125, 211, 252, 0.18);
        }
        button.secondary { color: var(--text); background: rgba(255,255,255,0.06); border: 1px solid var(--border); box-shadow: none; }
        button.danger { color: #fff; background: linear-gradient(135deg, #fb7185, #fda4af); }
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
        .pill { padding: 6px 10px; border-radius: 999px; font-size: 12px; border: 1px solid var(--border); color: var(--muted); }
        .pill.good { color: var(--good); }
        .pill.bad { color: var(--bad); }
        code { background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 8px; }
        pre {
            margin: 0; padding: 14px; overflow: auto; border-radius: 14px; border: 1px solid var(--border);
            background: rgba(0,0,0,0.18); color: #d7e3ff; font-size: 12px; line-height: 1.5;
        }
        .state { color: var(--muted); }
        .state.error { color: var(--bad); }
        .state.ok { color: var(--good); }
        .empty {
            padding: 28px; text-align: center; border-radius: 18px; border: 1px dashed var(--border);
            color: var(--muted); background: rgba(255,255,255,0.03);
        }
        .footer { margin-top: 24px; color: var(--muted); font-size: 13px; }
    </style>
</head>
<body>
    <div class=\"wrap\">
        <section class=\"hero\">
            <div>
                <h1>Patch Review Desk</h1>
                <p class=\"sub\">Review suggested patches produced by the orchestration runner, inspect metadata, and apply approved patches through the governance API.</p>
            </div>
            <div class=\"meta\">
                <span class=\"chip\">GET <code>/governance/patches</code></span>
                <span class=\"chip\">POST <code>/governance/patches/{id}/apply</code></span>
            </div>
        </section>

        <div class=\"toolbar\">
            <div class=\"row\">
                <button id=\"refreshBtn\">Refresh patches</button>
                <button id=\"applyAllBtn\" class=\"secondary\">Apply all applied/suggested patches</button>
            </div>
            <div id=\"status\" class=\"state\">Ready.</div>
        </div>

        <div id=\"patches\" class=\"grid\"></div>

        <div class=\"footer\">This UI is intentionally minimal and uses the same API endpoints as the CLI for a single source of truth.</div>
    </div>

    <script>
        const statusEl = document.getElementById('status');
        const patchesEl = document.getElementById('patches');
        const refreshBtn = document.getElementById('refreshBtn');
        const applyAllBtn = document.getElementById('applyAllBtn');

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
                const patches = await response.json();
                renderPatches(patches);
                setStatus(patches.length + ' patch(es) loaded.', 'ok');
            } catch (error) {
                patchesEl.innerHTML = '<div class="empty">Failed to load patches.</div>';
                setStatus('Error loading patches: ' + error.message, 'error');
            }
        }

        function renderPatches(patches) {
            if (!patches.length) {
                patchesEl.innerHTML = '<div class="empty">No patches found. Run a workflow that suggests patches, then refresh.</div>';
                return;
            }

            patchesEl.innerHTML = patches.map((patch) => {
                const meta = JSON.stringify(patch.metadata || {}, null, 2);
                const applied = patch.status === 'applied';
                return `
                    <article class="card" data-patch-id="${patch.id}">
                        <div class="card-head">
                            <div>
                                <h2 class="title">${escapeHtml(patch.title || patch.id)}</h2>
                                <p class="desc">${escapeHtml(patch.description || '')}</p>
                            </div>
                            <div class="row">
                                <span class="pill ${applied ? 'good' : 'bad'}">${escapeHtml(patch.status || 'unknown')}</span>
                                <span class="pill">${escapeHtml(patch.id)}</span>
                            </div>
                        </div>
                        <div class="row">
                            <span class="pill">Created: ${escapeHtml(patch.created_at || '-')}</span>
                            <span class="pill">Applied: ${escapeHtml(patch.applied_at || '-')}</span>
                        </div>
                        <pre>${escapeHtml(meta)}</pre>
                        <div class="row">
                            <button ${applied ? 'disabled' : ''} onclick="applyPatch('${patch.id}')">${applied ? 'Applied' : 'Apply patch'}</button>
                        </div>
                    </article>
                `;
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

        async function applyAll() {
            const cards = Array.from(document.querySelectorAll('[data-patch-id]'));
            const ids = cards.map((card) => card.getAttribute('data-patch-id')).filter(Boolean);
            if (!ids.length) {
                setStatus('No patches to apply.', '');
                return;
            }
            if (!confirm('Apply ' + ids.length + ' patch(es)?')) return;
            for (const id of ids) {
                await applyPatch(id);
            }
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
        applyAllBtn.addEventListener('click', applyAll);
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
