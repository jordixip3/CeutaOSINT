// ============================================================
//  CeutaOSINT Dashboard — Unified Command Center app.js
//  Integrated OSINT Prompt AI, Live Date Filtering,
//  Instant Sync of Tables, Metrics, Gauges and Evidence Registries
// ============================================================

let allPosts = [];
let currentCategoryFilter = '';
let autoRefreshInterval = null;
let startDateFilter = '';
let endDateFilter = '';
let activePrompt = '';
let activeAiSynopsis = '';
let activePreset = 'all';

const CATEGORY_LABELS = {
    'CALL_TO_ACTION':           { label: 'Convocatoria',     cls: 'badge-cta' },
    'LOGISTICS_ROUTES':         { label: 'Ruta/Logística',   cls: 'badge-logistics' },
    'EARLY_WARNING':            { label: 'Señal Pre-Evento', cls: 'badge-early' },
    'OFFICIAL_DISCLAIMER':      { label: 'Oficial',          cls: 'badge-official' },
    'DISINFORMATION_PROPAGANDA':{ label: 'Desinformación',   cls: 'badge-logistics' },
};

const SOURCE_ICONS = {
    RSS:          '📰',
    SOCIAL_MEDIA: '📱',
    TELEGRAM:     '✈️',
    WEB:          '🌐',
};

// ── Boot ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Initial master load
    unifiedSearchAndRefresh(true);
    // Background auto-refresh every 30 seconds preserving user search & date filters
    autoRefreshInterval = setInterval(() => unifiedSearchAndRefresh(true), 30000);
});

// ── Tab Navigation ────────────────────────────────────────────
function switchTab(tab) {
    const titles = {
        dashboard: 'Investigación Forense — Evento Fronterizo Ceuta',
        evidence:  'Registro de Evidencias OSINT',
        loop:      'Bucle de Agente Autónomo & Scores',
        report:    'Informe Ejecutivo de Ciberinteligencia',
    };

    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    document.getElementById('nav-' + tab).classList.add('active');
    document.getElementById('topbar-title').textContent = titles[tab] || '';

    if (tab === 'loop')     renderIterationsTable();
    if (tab === 'report')   loadFullReport();
    if (tab === 'evidence') renderEvidenceTable(allPosts);
}

// ── UNIFIED MASTER ACTION: BUSCAR Y ACTUALIZAR ────────────────
async function unifiedSearchAndRefresh(silent = false) {
    const btnExecute = document.getElementById('btn-unified-execute');
    const statusBadge = document.getElementById('command-status-badge');
    const topbarRefreshBtn = document.querySelector('.btn-success');

    const promptInput = document.getElementById('ai-prompt-input');
    activePrompt = promptInput ? promptInput.value.trim() : '';

    const startInput = document.getElementById('start-date');
    startDateFilter = startInput ? startInput.value : '';

    const endInput = document.getElementById('end-date');
    endDateFilter = endInput ? endInput.value : '';

    if (!silent) {
        if (btnExecute) {
            btnExecute.disabled = true;
            btnExecute.textContent = '⏳ ACTUALIZANDO...';
        }
        if (statusBadge) {
            statusBadge.textContent = '⚡ ANALIZANDO EN VIVO...';
            statusBadge.style.color = 'var(--accent-blue)';
        }
        if (topbarRefreshBtn) {
            topbarRefreshBtn.disabled = true;
            topbarRefreshBtn.textContent = '⏳ Rastreando...';
        }
    }

    try {
        let posts = [];

        if (activePrompt) {
            // Case 1: Prompt sentence entered -> Execute through AI OSINT Engine
            const res = await fetch('/api/ai/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: activePrompt,
                    start_date: startDateFilter,
                    end_date: endDateFilter,
                    category: currentCategoryFilter
                })
            });

            if (res.ok) {
                const data = await res.json();
                posts = data.posts || [];
                if (data.ai_synopsis) {
                    activeAiSynopsis = data.ai_synopsis;
                    const banner = document.getElementById('ai-synopsis-banner');
                    const textDiv = document.getElementById('ai-synopsis-text');
                    if (banner && textDiv) {
                        textDiv.innerHTML = formatSynopsisMarkdown(data.ai_synopsis);
                        banner.style.display = 'block';
                    }
                }
            }
        } else {
            // Case 2: Standard or Date-filtered search -> Query posts with date & category parameters
            const banner = document.getElementById('ai-synopsis-banner');
            if (banner) banner.style.display = 'none';

            let queryParams = new URLSearchParams();
            if (startDateFilter) queryParams.append('start_date', startDateFilter);
            if (endDateFilter) queryParams.append('end_date', endDateFilter);
            if (currentCategoryFilter) queryParams.append('category', currentCategoryFilter);

            const res = await fetch(`/api/posts?${queryParams.toString()}`);
            if (res.ok) {
                const data = await res.json();
                posts = data.posts || [];
            }
        }

        allPosts = posts;

        // Synchronously update ALL dashboard views
        renderDashboardPostsTable();
        renderEvidenceTable(allPosts);
        updateMetricsFromPosts(allPosts);
        calculateAverageBreakdowns(allPosts);
        updateUnifiedFilterBadge();

    } catch (err) {
        console.error('[Unified Search Error]:', err);
    } finally {
        if (btnExecute) {
            btnExecute.disabled = false;
            btnExecute.textContent = '🔍 BUSCAR Y ACTUALIZAR';
        }
        if (statusBadge) {
            statusBadge.textContent = '🟢 SISTEMA VIVO';
            statusBadge.style.color = 'var(--accent-green)';
        }
        if (topbarRefreshBtn) {
            topbarRefreshBtn.disabled = false;
            topbarRefreshBtn.textContent = '🔄 Refrescar Evidencias';
        }
    }
}

// ── PRESET DATES HANDLER ──────────────────────────────────────
function applyPresetAndSearch(type) {
    activePreset = type;
    const startInput = document.getElementById('start-date');
    const endInput = document.getElementById('end-date');

    // Highlight active preset button
    document.querySelectorAll('.btn-preset').forEach(b => b.classList.remove('active-preset'));
    const btn = document.getElementById(
        type === 'all' ? 'preset-all' :
        type === 'recent' ? 'preset-recent' :
        type === 'pre-event' ? 'preset-pre' : 'preset-event'
    );
    if (btn) btn.classList.add('active-preset');

    const today = new Date();
    const formatDate = (d) => d.toISOString().split('T')[0];

    if (type === 'recent') {
        const fourDaysAgo = new Date();
        fourDaysAgo.setDate(today.getDate() - 4);
        startInput.value = formatDate(fourDaysAgo);
        endInput.value = formatDate(today);
    } else if (type === 'pre-event') {
        startInput.value = '2026-06-18';
        endInput.value = '2026-06-25';
    } else if (type === 'event') {
        startInput.value = '2026-06-26';
        endInput.value = '2026-06-30';
    } else { // 'all'
        startInput.value = '';
        endInput.value = '';
    }

    unifiedSearchAndRefresh();
}

// ── PROMPT SUGGESTIONS ────────────────────────────────────────
function setPromptAndRun(promptText) {
    const input = document.getElementById('ai-prompt-input');
    if (input) input.value = promptText;
    unifiedSearchAndRefresh();
}

function resetAllFiltersAndSearch() {
    const input = document.getElementById('ai-prompt-input');
    if (input) input.value = '';
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    currentCategoryFilter = '';
    activePrompt = '';
    closeSynopsis();

    // Reset category buttons visual state
    document.querySelectorAll('.category-filter-btn').forEach(b => b.classList.remove('active'));
    const allBtn = document.querySelector('.category-filter-btn[data-cat=""]');
    if (allBtn) allBtn.classList.add('active');

    applyPresetAndSearch('all');
}

function closeSynopsis() {
    const banner = document.getElementById('ai-synopsis-banner');
    if (banner) banner.style.display = 'none';
}

function formatSynopsisMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/• (.*?)(?=\n|$)/g, '<li>$1</li>');
}

// ── ACTIVE FILTER BADGE UPDATE ────────────────────────────────
function updateUnifiedFilterBadge() {
    const badge = document.getElementById('unified-active-filter-badge');
    if (!badge) return;

    let segments = [];

    if (activePrompt) {
        segments.push(`🤖 Prompt IA: <strong style="color:#ffffff;">"${activePrompt}"</strong>`);
    }

    if (startDateFilter || endDateFilter) {
        if (startDateFilter && endDateFilter) {
            segments.push(`📅 Fechas: <strong>${startDateFilter}</strong> al <strong>${endDateFilter}</strong>`);
        } else if (startDateFilter) {
            segments.push(`📅 Desde: <strong>${startDateFilter}</strong>`);
        } else {
            segments.push(`📅 Hasta: <strong>${endDateFilter}</strong>`);
        }
    } else {
        segments.push(`📅 Rango: <strong>Todo el histórico</strong>`);
    }

    if (currentCategoryFilter) {
        const catInfo = CATEGORY_LABELS[currentCategoryFilter] || { label: currentCategoryFilter };
        segments.push(`🏷️ Categoría: <strong>${catInfo.label}</strong>`);
    }

    segments.push(`📊 <strong>${allPosts.length}</strong> evidencias activas`);

    badge.innerHTML = segments.join(' &nbsp;|&nbsp; ');
}

// ── METRICS RECALCULATION (SYNCHRONIZED WITH POSTS) ───────────
function updateMetricsFromPosts(posts) {
    const totalCount = posts.length;
    let avgScore = 0.0;
    let preEventCount = 0;

    if (totalCount > 0) {
        const sumScores = posts.reduce((acc, p) => acc + (p.score || 0), 0);
        avgScore = (sumScores / totalCount).toFixed(1);

        preEventCount = posts.filter(p => {
            return p.category === 'EARLY_WARNING' ||
                (p.publish_time && p.publish_time.includes('2026-06-2') && parseInt(p.publish_time.split('2026-06-')[1].substring(0, 2)) <= 25);
        }).length;
    }

    // Update Top Metric Cards
    document.getElementById('metric-total-posts').textContent = totalCount;
    document.getElementById('metric-avg-score').textContent   = `${avgScore} / 10`;
    document.getElementById('metric-pre-events').textContent  = preEventCount;
    document.getElementById('metric-iterations').textContent  = '5';

    // Update Score Gauge
    const scoreEl  = document.getElementById('gauge-score-val');
    const statusEl = document.getElementById('gauge-status-lbl');
    if (scoreEl) scoreEl.textContent = `${avgScore} / 10`;

    if (statusEl) {
        if (avgScore >= 7.0) {
            statusEl.textContent = '✓ ALTA CONFIDENCIA (≥ 7.0/10)';
            statusEl.style.background = 'rgba(0, 230, 118, 0.15)';
            statusEl.style.color      = '#00e676';
            statusEl.style.border     = '1px solid #00e676';
        } else {
            statusEl.textContent = '⚠️ CONFIDENCIA MODERADA (< 7.0/10)';
            statusEl.style.background = 'rgba(255, 171, 0, 0.15)';
            statusEl.style.color      = '#ffab00';
            statusEl.style.border     = '1px solid #ffab00';
        }
    }
}

// ── Score Breakdown Averages ──────────────────────────────────
function calculateAverageBreakdowns(posts) {
    let sumAuth = 0, sumCorr = 0, sumTemp = 0, sumSpec = 0, count = 0;
    posts.forEach(p => {
        if (p.score_breakdown && typeof p.score_breakdown === 'object') {
            sumAuth += p.score_breakdown.source_authority    || 0;
            sumCorr += p.score_breakdown.cross_corroboration || 0;
            sumTemp += p.score_breakdown.temporal_lead_time  || 0;
            sumSpec += p.score_breakdown.specificity         || 0;
            count++;
        }
    });

    const elAuth = document.getElementById('score-auth');
    const elCorr = document.getElementById('score-corr');
    const elTemp = document.getElementById('score-temp');
    const elSpec = document.getElementById('score-spec');

    if (count > 0) {
        if (elAuth) elAuth.textContent = (sumAuth / count).toFixed(1);
        if (elCorr) elCorr.textContent = (sumCorr / count).toFixed(1);
        if (elTemp) elTemp.textContent = (sumTemp / count).toFixed(1);
        if (elSpec) elSpec.textContent = (sumSpec / count).toFixed(1);
    } else {
        if (elAuth) elAuth.textContent = '0.0';
        if (elCorr) elCorr.textContent = '0.0';
        if (elTemp) elTemp.textContent = '0.0';
        if (elSpec) elSpec.textContent = '0.0';
    }
}

// ── Dashboard Posts Table (Evidencias Recientes) ──────────────
function renderDashboardPostsTable() {
    const tbody = document.getElementById('posts-tbody-dashboard');
    if (!tbody) return;
    tbody.innerHTML = '';

    let posts = allPosts;
    if (currentCategoryFilter) {
        posts = allPosts.filter(p => p.category === currentCategoryFilter);
    }

    if (!posts.length) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-muted);font-size:13px;">
            ⚠️ No se encontraron evidencias para los parámetros seleccionados. Prueba a seleccionar <strong>"Todo el Histórico"</strong> o limpiar la búsqueda.
        </td></tr>`;
        return;
    }

    posts.forEach((p, idx) => {
        const { label, cls } = CATEGORY_LABELS[p.category] || { label: p.category, cls: 'badge-early' };
        const icon    = SOURCE_ICONS[p.source_type] || '🔎';
        const pubDate = (p.publish_time || '').replace('T', ' ').substring(0, 16);
        const excerpt = p.content.length > 140 ? p.content.substring(0, 140) + '…' : p.content;
        const scoreColor = p.score >= 8.5 ? '#00e676' : p.score >= 7.0 ? '#00f2fe' : '#ffab00';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight:700;color:var(--accent-blue);font-family:'JetBrains Mono',monospace;">#${idx + 1}</td>
            <td>
                <strong>${icon} ${p.source_name}</strong><br>
                <span style="font-size:11px;color:var(--text-muted);">${p.author || 'Anónimo'}</span>
            </td>
            <td style="font-size:12px;color:var(--text-muted);">${pubDate}</td>
            <td><span class="badge ${cls}">${label}</span></td>
            <td>
                <div style="font-weight:600;margin-bottom:4px;">${p.title}</div>
                <div style="font-size:12px;color:var(--text-muted);line-height:1.4;">${excerpt}</div>
            </td>
            <td>
                <strong style="color:${scoreColor};font-size:15px;font-family:'JetBrains Mono',monospace;">${p.score}</strong>
            </td>
            <td>
                <button class="btn btn-ghost btn-sm" onclick="openPostModal(${p.id})">🔎 Ver</button>
                <a href="${p.url}" target="_blank" class="btn btn-ghost btn-sm" style="text-decoration:none;">🔗 Enlace</a>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function selectCategoryFilter(btn, cat) {
    document.querySelectorAll('.category-filter-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    filterCategory(cat);
}

function filterCategory(cat) {
    currentCategoryFilter = cat;
    renderDashboardPostsTable();
    updateUnifiedFilterBadge();
}

// ── Evidence Tab Table (Registro Completo) ────────────────────
function renderEvidenceTable(posts) {
    const tbody = document.getElementById('posts-tbody-evidence');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!posts.length) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted);padding:20px;">Sin evidencias para este filtro.</td></tr>';
        return;
    }

    posts.forEach((p, idx) => {
        const { label, cls } = CATEGORY_LABELS[p.category] || { label: p.category, cls: 'badge-early' };
        const icon    = SOURCE_ICONS[p.source_type] || '🔎';
        const pubDate = (p.publish_time || '').replace('T', ' ').substring(0, 16);
        const excerpt = p.content.length > 110 ? p.content.substring(0, 110) + '…' : p.content;
        const scoreColor = p.score >= 8.5 ? '#00e676' : p.score >= 7.0 ? '#00f2fe' : '#ffab00';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight:700;color:var(--accent-blue);font-family:'JetBrains Mono',monospace;">#${idx + 1}</td>
            <td><strong>${p.source_name}</strong><br><span style="font-size:11px;color:var(--text-muted);">${p.author || 'Anónimo'}</span></td>
            <td><span style="font-size:12px;">${icon} ${p.source_type}</span></td>
            <td style="font-size:12px;color:var(--text-muted);">${pubDate}</td>
            <td><span class="badge ${cls}">${label}</span></td>
            <td>
                <div style="font-weight:600;font-size:13px;">${p.title}</div>
                <div style="font-size:11px;color:var(--text-muted);">${excerpt}</div>
            </td>
            <td><strong style="color:${scoreColor};font-size:15px;font-family:'JetBrains Mono',monospace;">${p.score}</strong></td>
            <td>
                <button class="btn btn-ghost btn-sm" onclick="openPostModal(${p.id})">🔎 Detalle</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function searchEvidenceTable() {
    const term = document.getElementById('search-evidence').value.toLowerCase();
    const filtered = allPosts.filter(p =>
        (p.title && p.title.toLowerCase().includes(term)) ||
        (p.content && p.content.toLowerCase().includes(term)) ||
        (p.author && p.author.toLowerCase().includes(term)) ||
        (p.source_name && p.source_name.toLowerCase().includes(term))
    );
    renderEvidenceTable(filtered);
}

// ── Agent Iterations History ──────────────────────────────────
async function renderIterationsTable() {
    const tbody = document.getElementById('iterations-tbody');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted);">Cargando...</td></tr>';

    try {
        const res = await fetch('/api/iterations');
        if (res.ok) {
            const data = await res.json();
            const iters = data.iterations || [];

            document.getElementById('loop-total-iter').textContent = iters.length;
            if (iters.length) {
                const maxS = Math.max(...iters.map(i => i.max_score || 0));
                document.getElementById('loop-max-score').textContent = `${maxS.toFixed(1)} / 10`;
            }

            tbody.innerHTML = '';
            iters.forEach(it => {
                const badgeCls = it.status === 'THRESHOLD_REACHED' ? 'badge-cta' : 'badge-early';
                const statusLbl = it.status === 'THRESHOLD_REACHED' ? '✓ UMBRAL SUPERADO' : '🔄 REFINANDO';
                const kws = Array.isArray(it.query_keywords) ? it.query_keywords.slice(0, 6).join(', ') + '…' : (it.query_keywords || '');

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight:700;color:var(--accent-purple);font-family:'JetBrains Mono',monospace;">Iteración #${it.iteration}</td>
                    <td><strong>${it.posts_harvested}</strong> evidencias</td>
                    <td><strong style="color:var(--accent-green);">${it.avg_score} / 10</strong></td>
                    <td><strong style="color:var(--accent-blue);">${it.max_score} / 10</strong></td>
                    <td><span class="badge ${badgeCls}">${statusLbl}</span></td>
                    <td style="font-size:12px;color:var(--text-muted);">${kws}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error('Error fetching iterations:', e);
    }
}

// ── Global Modal State ────────────────────────────────────────
let activeModalPostId = null;

// ── Full Intelligence Report ──────────────────────────────────
async function loadFullReport() {
    const container = document.getElementById('report-content-full');
    if (!container) return;
    container.innerHTML = '<p style="color:var(--text-muted);"><span class="pulse-dot" style="display:inline-block;vertical-align:middle;margin-right:8px;"></span>Cargando informe forense y hallazgos clave...</p>';

    try {
        const res = await fetch('/api/reports');
        if (res.ok) {
            const data = await res.json();
            const r = data.report;
            if (r) {
                let findingsHtml = '';
                let rawFindings = r.key_findings;

                if (typeof rawFindings === 'string') {
                    try { rawFindings = json.loads(rawFindings); } catch (e) { rawFindings = [rawFindings]; }
                }

                if (Array.isArray(rawFindings) && rawFindings.length > 0) {
                    findingsHtml = rawFindings.map((f, idx) => {
                        if (typeof f === 'object' && f !== null) {
                            const vector = f.vector || `Vector Táctico #${idx + 1}`;
                            const desc = f.description || '';
                            const evCount = f.evidence_count ? `${f.evidence_count} fuentes` : 'Multi-fuente';
                            const conf = f.confidence_score ? `${f.confidence_score}/10` : '8.5/10';
                            return `
                                <div class="finding-card" onclick="openFindingModal(${idx + 1})" title="Haz clic para abrir el Dossier Forense y descargar PDF">
                                    <div class="finding-bullet">🎯</div>
                                    <div class="finding-content">
                                        <div style="font-weight:700;color:var(--accent-blue);font-size:13.5px;margin-bottom:4px;">
                                            #${idx + 1} [${vector}]
                                        </div>
                                        <div class="finding-text">${desc}</div>
                                        <div class="finding-meta">
                                            <span>Corroboración: <strong>${evCount}</strong> &nbsp;|&nbsp; Certeza: <strong style="color:var(--accent-green);">${conf}</strong></span>
                                            <span class="finding-action-tag">📄 Ver Dossier & PDF ➔</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            return `
                                <div class="finding-card" onclick="openFindingModal(${idx + 1})" title="Haz clic para abrir el Dossier Forense y descargar PDF">
                                    <div class="finding-bullet">🎯</div>
                                    <div class="finding-content">
                                        <div style="font-weight:700;color:var(--accent-blue);font-size:13.5px;margin-bottom:4px;">
                                            Hallazgo Forense #${idx + 1}
                                        </div>
                                        <div class="finding-text">${String(f)}</div>
                                        <div class="finding-meta">
                                            <span>Verificado por correlación multi-fuente OSINT</span>
                                            <span class="finding-action-tag">📄 Ver Dossier & PDF ➔</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                    }).join('');
                } else {
                    findingsHtml = '<p style="color:var(--text-muted);font-size:13px;padding:12px;background:rgba(255,255,255,0.02);border-radius:6px;">No se registraron hallazgos adicionales en el informe actual.</p>';
                }

                const execText = formatSynopsisMarkdown(r.executive_summary || 'Análisis en tiempo real procesado.');

                container.innerHTML = `
                    <div style="margin-bottom:18px;display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                        <div>
                            <h4 style="font-size:17px;color:#fff;margin-bottom:4px;">${r.title || 'Informe Ejecutivo de Inteligencia OSINT'}</h4>
                            <div style="font-size:12px;color:var(--text-muted);">
                                📅 Generado: ${r.generated_at || 'En tiempo real'} &nbsp;|&nbsp; 
                                ⭐ Confianza Global: <strong style="color:var(--accent-green);font-size:14px;">${r.overall_score || 8.0}/10</strong> &nbsp;|&nbsp; 
                                📊 Evidencias: <strong>${r.total_sources || allPosts.length}</strong>
                            </div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border);padding:16px;border-radius:10px;margin-bottom:20px;line-height:1.7;">
                        <div style="font-size:11px;font-weight:800;color:var(--accent-blue);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">DICTAMEN OPERATIVO CONSOLIDADO</div>
                        ${execText}
                    </div>
                    <h5 style="font-size:13px;font-weight:800;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
                        HALLAZGOS CLAVE & VECTORES DE INCIDENTE:
                    </h5>
                    ${findingsHtml}
                `;
            } else {
                container.innerHTML = '<p style="color:var(--text-muted);">No se dispone de un informe ejecutivo previo. Ejecuta una búsqueda para generarlo.</p>';
            }
        }
    } catch (e) {
        console.error('Error loading report:', e);
        container.innerHTML = '<p style="color:#ff5252;">Error de conexión al cargar el informe ejecutivo.</p>';
    }
}

// ── Modal Tabs Navigation ─────────────────────────────────────
function switchModalTab(tab) {
    const btnPdf = document.getElementById('modal-tab-btn-pdf');
    const btnData = document.getElementById('modal-tab-btn-data');
    const panelPdf = document.getElementById('modal-panel-pdf');
    const panelData = document.getElementById('modal-panel-data');

    if (tab === 'pdf') {
        if (btnPdf) btnPdf.classList.add('active');
        if (btnData) btnData.classList.remove('active');
        if (panelPdf) panelPdf.style.display = 'block';
        if (panelData) panelData.style.display = 'none';
    } else {
        if (btnData) btnData.classList.add('active');
        if (btnPdf) btnPdf.classList.remove('active');
        if (panelPdf) panelPdf.style.display = 'none';
        if (panelData) panelData.style.display = 'block';
    }
}

// ── Post Modal Detail & PDF Preview ───────────────────────────
async function openPostModal(postId) {
    activeModalPostId = postId;
    const modal = document.getElementById('post-modal');
    if (!modal) return;

    modal.classList.add('open');
    modal.classList.add('active');

    // Switch to PDF tab by default
    switchModalTab('pdf');

    // Set PDF Iframe URL for immediate native preview
    const iframe = document.getElementById('modal-pdf-iframe');
    if (iframe) {
        iframe.src = `/api/posts/${postId}/pdf#toolbar=1`;
    }

    // Set placeholder loading states for structured fields
    const titleEl = document.getElementById('modal-title');
    if (titleEl) titleEl.textContent = 'Cargando evidencia...';

    try {
        const res = await fetch(`/api/posts/${postId}`);
        if (res.ok) {
            const data = await res.json();
            const p = data.post;
            if (!p) return;

            const { label, cls } = CATEGORY_LABELS[p.category] || { label: p.category || 'General', cls: 'badge-early' };

            const catEl = document.getElementById('modal-category');
            if (catEl) {
                catEl.textContent = label;
                catEl.className = `badge ${cls}`;
            }

            const scoreBadge = document.getElementById('modal-score-badge');
            if (scoreBadge) {
                scoreBadge.textContent = `SCORE: ${p.score || 0.0} / 10`;
            }

            if (titleEl) titleEl.textContent = p.title || 'Sin Título';

            const pubDate = (p.publish_time || '').replace('T', ' ').substring(0, 16);
            const sourceEl = document.getElementById('modal-source');
            if (sourceEl) sourceEl.textContent = `${p.source_name || 'Desconocido'} (${p.author || 'Anónimo'})`;

            const dateEl = document.getElementById('modal-date');
            if (dateEl) dateEl.textContent = pubDate || 'Fecha no disponible';

            const urlEl = document.getElementById('modal-url');
            if (urlEl) {
                urlEl.href = p.url || '#';
                urlEl.style.display = p.url ? 'inline-block' : 'none';
            }

            const contentEl = document.getElementById('modal-content-full');
            if (contentEl) contentEl.textContent = p.content || 'Sin extracto disponible.';

            // Render Entities
            const entBox = document.getElementById('modal-entities');
            if (entBox) {
                if (p.entities && p.entities.length) {
                    entBox.innerHTML = p.entities.map(e => `
                        <div class="entity-tag">
                            <strong>${e.entity_type || e.type}:</strong> ${e.entity_value || e.value}
                        </div>
                    `).join('');
                } else {
                    entBox.innerHTML = '<span style="color:var(--text-muted);font-size:12px;">Sin entidades estructuradas adicionales.</span>';
                }
            }

            // Score breakdown
            const sb = p.score_breakdown || {};
            const authEl = document.getElementById('modal-score-auth');
            const corrEl = document.getElementById('modal-score-corr');
            const tempEl = document.getElementById('modal-score-temp');
            const specEl = document.getElementById('modal-score-spec');

            if (authEl) authEl.textContent = sb.source_authority || '7.0';
            if (corrEl) corrEl.textContent = sb.cross_corroboration || '7.0';
            if (tempEl) tempEl.textContent = sb.temporal_lead_time || '7.5';
            if (specEl) specEl.textContent = sb.specificity || '6.0';
        }
    } catch (e) {
        console.error('Error loading post detail:', e);
    }
}

function closePostModal() {
    const modal = document.getElementById('post-modal');
    if (modal) {
        modal.classList.remove('open');
        modal.classList.remove('active');
    }
    const iframe = document.getElementById('modal-pdf-iframe');
    if (iframe) iframe.src = '';
    activeModalPostId = null;
}

// ── PDF Action Handlers ───────────────────────────────────────
function downloadCurrentPostPDF() {
    if (activeModalPostId) {
        window.open(`/api/posts/${activeModalPostId}/pdf?download=1`, '_blank');
    }
}

function openCurrentPostPDFInNewTab() {
    if (activeModalPostId) {
        window.open(`/api/posts/${activeModalPostId}/pdf`, '_blank');
    }
}

function downloadExecutiveReportPDF() {
    window.open('/api/reports/pdf?download=1', '_blank');
}

function openExecutiveReportPDFInNewTab() {
    window.open('/api/reports/pdf', '_blank');
}

// ── Topbar Refresh Evidencias (invoca el mismo buscador maestro)
function refreshNewIntelligence() {
    unifiedSearchAndRefresh();
}

// ── Export Functions ──────────────────────────────────────────
function exportReportJSON() {
    const blob = new Blob([JSON.stringify(allPosts, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `osint_evidencias_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
}

function exportReportTXT() {
    let txt = `===========================================================\n`;
    txt += `  OSINT CYBER INTEL — INFORME DE EVIDENCIAS\n`;
    txt += `  Generado: ${new Date().toLocaleString()}\n`;
    txt += `  Total de Evidencias: ${allPosts.length}\n`;
    txt += `===========================================================\n\n`;

    allPosts.forEach((p, i) => {
        txt += `[#${i + 1}] ${p.title}\n`;
        txt += `Fuente: ${p.source_name} (${p.source_type}) | Autor: ${p.author}\n`;
        txt += `Fecha: ${p.publish_time} | Categoría: ${p.category} | Score: ${p.score}/10\n`;
        txt += `URL: ${p.url}\n`;
        txt += `Contenido:\n${p.content}\n`;
        txt += `-----------------------------------------------------------\n\n`;
    });

    const blob = new Blob([txt], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `osint_evidencias_${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
}

// ── Global Finding Modal State & Handlers ─────────────────────
let activeFindingIndex = 1;

function switchFindingModalTab(tab) {
    const btnPdf = document.getElementById('finding-tab-btn-pdf');
    const btnData = document.getElementById('finding-tab-btn-data');
    const panelPdf = document.getElementById('finding-panel-pdf');
    const panelData = document.getElementById('finding-panel-data');

    if (tab === 'pdf') {
        if (btnPdf) btnPdf.classList.add('active');
        if (btnData) btnData.classList.remove('active');
        if (panelPdf) panelPdf.style.display = 'block';
        if (panelData) panelData.style.display = 'none';
    } else {
        if (btnData) btnData.classList.add('active');
        if (btnPdf) btnPdf.classList.remove('active');
        if (panelPdf) panelPdf.style.display = 'none';
        if (panelData) panelData.style.display = 'block';
    }
}

async function openFindingModal(findingIdx) {
    activeFindingIndex = findingIdx;
    const modal = document.getElementById('finding-modal');
    if (!modal) return;

    modal.classList.add('open');
    modal.classList.add('active');

    // Default to PDF preview tab
    switchFindingModalTab('pdf');

    // Embed PDF
    const iframe = document.getElementById('finding-pdf-iframe');
    if (iframe) {
        iframe.src = `/api/reports/findings/${findingIdx}/pdf#toolbar=1`;
    }

    const titleEl = document.getElementById('finding-modal-title');
    if (titleEl) titleEl.textContent = `Consultando Dossier Forense #${findingIdx}...`;

    try {
        const res = await fetch(`/api/reports/findings/${findingIdx}`);
        if (res.ok) {
            const data = await res.json();
            const f = data.finding;
            if (!f) return;

            if (titleEl) titleEl.textContent = `Dossier Forense: Hallazgo #${findingIdx}`;

            const vectorEl = document.getElementById('finding-modal-vector');
            if (vectorEl) vectorEl.textContent = f.vector || `VECTOR #${findingIdx}`;

            const scoreEl = document.getElementById('finding-modal-score');
            if (scoreEl) scoreEl.textContent = `CONFIANZA: ${f.confidence_score} / 10`;

            const descEl = document.getElementById('finding-modal-desc');
            if (descEl) descEl.textContent = f.description;

            const detailsEl = document.getElementById('finding-modal-details');
            if (detailsEl) detailsEl.textContent = f.analysis_details;

            // Render Indicators
            const indBox = document.getElementById('finding-modal-indicators');
            if (indBox) {
                indBox.innerHTML = (f.key_indicators || []).map(k => `
                    <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border);padding:8px 12px;border-radius:6px;margin-bottom:6px;font-size:12px;display:flex;justify-content:space-between;align-items:center;">
                        <span><strong style="color:var(--accent-blue);">•</strong> ${k.indicator || k}</span>
                        <span style="color:var(--accent-green);font-weight:700;font-size:11px;">${k.type || 'Señal OSINT'}</span>
                    </div>
                `).join('');
            }

            // Corroborating posts
            const postsBox = document.getElementById('finding-modal-posts');
            if (postsBox) {
                postsBox.innerHTML = (f.corroborating_posts || []).map(p => `
                    <div style="background:rgba(255,255,255,0.02);border:1px solid var(--border);padding:8px 12px;border-radius:6px;margin-bottom:6px;font-size:12px;">
                        <div style="display:flex;justify-content:space-between;color:var(--accent-blue);font-weight:700;margin-bottom:2px;">
                            <span>${p.source_name || 'Prensa'} (${p.source_type || 'OSINT'})</span>
                            <span style="color:var(--accent-green);">Score: ${p.score || 8.5}/10</span>
                        </div>
                        <div style="color:#fff;font-weight:600;">${p.title}</div>
                    </div>
                `).join('');
            }

            // Recommendations
            const recsBox = document.getElementById('finding-modal-recs');
            if (recsBox) {
                recsBox.innerHTML = (f.recommendations || []).map(r => `<li>${r}</li>`).join('');
            }
        }
    } catch (e) {
        console.error('Error loading finding detail:', e);
    }
}

function closeFindingModal() {
    const modal = document.getElementById('finding-modal');
    if (modal) {
        modal.classList.remove('open');
        modal.classList.remove('active');
    }
    const iframe = document.getElementById('finding-pdf-iframe');
    if (iframe) iframe.src = '';
}

function downloadCurrentFindingPDF() {
    if (activeFindingIndex) {
        window.open(`/api/reports/findings/${activeFindingIndex}/pdf?download=1`, '_blank');
    }
}

function openCurrentFindingPDFInNewTab() {
    if (activeFindingIndex) {
        window.open(`/api/reports/findings/${activeFindingIndex}/pdf`, '_blank');
    }
}

