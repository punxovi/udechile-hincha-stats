let resultsChartInstance = null;
let currentFilterType = 'general';
let currentFilterLabel = 'RENDIMIENTO GENERAL';
let currentSnapshotData = null;

document.addEventListener("DOMContentLoaded", () => {
    const data = window.dashboardData;
    if (!data) return;

    // Inicializar por defecto en el rendimiento general
    switchTab('general');
});

// Función para cambiar de pestaña en la interfaz
function switchTab(tabType) {
    currentFilterType = tabType;
    
    // Gestionar estilos activos de botones
    document.querySelectorAll('.tab-btn, .select-tab-container').forEach(el => {
        el.classList.remove('active');
    });

    const selectContainer = document.getElementById('tab-container-year');
    const classicsSection = document.getElementById('classics-breakdown-section');

    if (tabType === 'general') {
        document.getElementById('tab-general').classList.add('active');
        if (classicsSection) classicsSection.style.display = 'none';
        
        currentFilterLabel = 'RENDIMIENTO GENERAL';
        updateDashboardData(window.dashboardData.general, currentFilterLabel);
    } 
    else if (tabType === 'year') {
        if (selectContainer) selectContainer.classList.add('active');
        if (classicsSection) classicsSection.style.display = 'none';
        
        changeDashboardYear();
    } 
    else if (tabType === 'classics') {
        document.getElementById('tab-classics').classList.add('active');
        if (classicsSection) classicsSection.style.display = 'block';
        
        currentFilterLabel = 'CLÁSICOS COMBINADOS';
        
        // Cargar datos combinados de clásicos en la vista principal
        const classicsData = window.dashboardData.classics;
        updateDashboardData(classicsData.combined, currentFilterLabel);
        
        // Actualizar desgloses individuales vs Colo Colo y UC más abajo
        updateClassicsBreakdown(classicsData.cc, classicsData.uc);
    }
}

// Escuchar cambios en el selector de año
function changeDashboardYear() {
    // Si el usuario tocó el <select> directamente sin pasar por switchTab('year'),
    // activamos la pestaña de año primero (switchTab la llama de vuelta).
    if (currentFilterType !== 'year') {
        switchTab('year');
        return;
    }
    const yearSelect = document.getElementById('dashboard-year-select');
    if (!yearSelect) return;

    const selectedYear = yearSelect.value;
    const yearData = window.dashboardData.by_year[selectedYear] || {
        total_matches_attended: 0,
        wins: 0,
        draws: 0,
        losses: 0,
        win_percentage: 0.0,
        undefeated_percentage: 0.0,
        most_visited_stadiums: [],
        goals_scored_seen: 0,
        goals_conceded_seen: 0
    };

    currentFilterLabel = `TEMPORADA ${selectedYear}`;
    updateDashboardData(yearData);
}

// Actualizar contadores y estadios en la interfaz
function updateDashboardData(snapshot) {
    currentSnapshotData = snapshot;

    // 1. Encabezado de rendimiento
    document.getElementById('header-win-percentage').textContent = `RENDIMIENTO · ${snapshot.win_percentage.toFixed(1)}%`;
    document.getElementById('header-undefeated-percentage').textContent = `INVICTO · ${snapshot.undefeated_percentage.toFixed(1)}%`;

    // 2. Totales
    document.getElementById('stats-total-attended').textContent = snapshot.total_matches_attended;

    // 3. Box Score Resumen
    document.getElementById('stats-wins').textContent = snapshot.wins;
    document.getElementById('stats-draws').textContent = snapshot.draws;
    document.getElementById('stats-losses').textContent = snapshot.losses;

    // 4. Box Score Goles
    document.getElementById('stats-gf').textContent = snapshot.goals_scored_seen;
    document.getElementById('stats-gc').textContent = snapshot.goals_conceded_seen;

    const gd = snapshot.goals_scored_seen - snapshot.goals_conceded_seen;
    const gdEl = document.getElementById('stats-gd');
    gdEl.textContent = (gd > 0 ? '+' : '') + gd;
    
    // Asignar colores brutales de diferencia de gol
    if (gd > 0) {
        gdEl.style.color = 'var(--success)';
    } else if (gd < 0) {
        gdEl.style.color = 'var(--udechile-red)';
    } else {
        gdEl.style.color = 'var(--text-primary)';
    }

    // 5. Lista de estadios
    updateStadiumsList(snapshot.most_visited_stadiums);

    // 6. Redibujar gráfico
    drawChart(snapshot);
}

// Pintar la lista de estadios de forma dinámica
function updateStadiumsList(stadiums) {
    const container = document.getElementById('stadiums-list-container');
    if (!container) return;
    
    if (!stadiums || stadiums.length === 0) {
        container.innerHTML = `<div style="padding: 2rem 1rem; text-align: center; font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; color: var(--text-secondary);">SIN REGISTROS</div>`;
        return;
    }
    
    let html = '';
    stadiums.slice(0, 10).forEach((entry, index) => {
        html += `
            <div class="box-list-row">
                <span style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; font-weight: 800; color: var(--text-secondary);">#${index + 1}</span>
                <span style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; padding-right: 0.5rem; color: var(--text-primary); line-height: 1.3; word-break: break-word;">${entry.stadium.name}</span>
                <span style="font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; text-align: right; color: var(--text-primary);">${entry.visit_count}</span>
            </div>
        `;
    });
    container.innerHTML = html;
}

// Actualizar desgloses individuales vs Colo Colo y UC
function updateClassicsBreakdown(cc, uc) {
    // Colo Colo
    document.getElementById('cc-perf-badge').textContent = `REND: ${cc.win_percentage.toFixed(1)}%`;
    document.getElementById('cc-total').textContent = cc.total_matches_attended;
    document.getElementById('cc-wins').textContent = cc.wins;
    document.getElementById('cc-draws').textContent = cc.draws;
    document.getElementById('cc-losses').textContent = cc.losses;
    document.getElementById('cc-gf').textContent = cc.goals_scored_seen;
    document.getElementById('cc-gc').textContent = cc.goals_conceded_seen;

    // UC
    document.getElementById('uc-perf-badge').textContent = `REND: ${uc.win_percentage.toFixed(1)}%`;
    document.getElementById('uc-total').textContent = uc.total_matches_attended;
    document.getElementById('uc-wins').textContent = uc.wins;
    document.getElementById('uc-draws').textContent = uc.draws;
    document.getElementById('uc-losses').textContent = uc.losses;
    document.getElementById('uc-gf').textContent = uc.goals_scored_seen;
    document.getElementById('uc-gc').textContent = uc.goals_conceded_seen;
}

// Dibujar/actualizar el gráfico Doughnut
function drawChart(snapshot) {
    const ctxResults = document.getElementById('resultsChart');
    if (!ctxResults) return;

    // Destruir instancia anterior si existe
    if (resultsChartInstance) {
        resultsChartInstance.destroy();
    }

    const style = getComputedStyle(document.documentElement);
    const textPrimary = style.getPropertyValue('--text-primary').trim() || '#002D72';
    const textSecondary = style.getPropertyValue('--text-secondary').trim() || '#475569';
    const textTertiary = style.getPropertyValue('--text-tertiary').trim() || '#64748b';
    const cardBg = style.getPropertyValue('--card-bg').trim() || '#FFFFFF';

    Chart.defaults.color = textSecondary;
    Chart.defaults.font.family = "'Montserrat', sans-serif";
    Chart.defaults.font.weight = 600;

    const centerTextPlugin = {
        id: 'centerText',
        afterDraw(chart) {
            const { ctx, chartArea: { left, top, width, height } } = chart;
            ctx.save();
            
            ctx.font = "800 0.75rem 'Montserrat', sans-serif";
            ctx.fillStyle = textTertiary;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('RENDIMIENTO', left + width / 2, top + height / 2 - 14);

            ctx.font = "800 2.8rem 'Bebas Neue', sans-serif";
            ctx.fillStyle = textPrimary;
            ctx.fillText(`${snapshot.win_percentage.toFixed(1)}%`, left + width / 2, top + height / 2 + 12);
            
            ctx.restore();
        }
    };

    const ctx = ctxResults.getContext('2d');
    const colorWin = '#2563EB';  // Azul suave/institucional
    const colorDraw = '#94A3B8'; // Gris pizarra
    const colorLoss = '#EF4444'; // Rojo suave

    resultsChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Victorias', 'Empates', 'Derrotas'],
            datasets: [{
                data: [snapshot.wins, snapshot.draws, snapshot.losses],
                backgroundColor: [colorWin, colorDraw, colorLoss],
                borderWidth: 3,
                borderColor: cardBg,
                hoverOffset: 4
            }]
        },
        plugins: [centerTextPlugin],
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    position: 'bottom',
                    labels: { 
                        padding: 15, 
                        usePointStyle: true, 
                        pointStyle: 'circle',
                        font: { family: "'Montserrat', sans-serif", size: 11, weight: 800 }
                    }
                },
                tooltip: {
                    backgroundColor: cardBg,
                    titleColor: textPrimary,
                    titleFont: { family: "'Montserrat', sans-serif", size: 12, weight: 800 },
                    bodyColor: textSecondary,
                    bodyFont: { family: "'Montserrat', sans-serif", size: 11, weight: 600 },
                    borderColor: textTertiary,
                    borderWidth: 1,
                    padding: 10,
                    boxPadding: 6,
                    usePointStyle: true,
                    cornerRadius: 0
                }
            },
            cutout: '78%'
        }
    });
}

// Exportar ficha del hincha brutalista como imagen PNG
// ── Temas de la ficha exportable ─────────────────────────────────────────────
const CARD_THEMES = {
    dark: {
        bg: '#0A1628',
        border: '#FFFFFF',
        text: '#FFFFFF',
        secondary: '#CBD5E1',
        accent: '#69C0FF',
        accentRed: '#FC8181',
        success: '#4ADE80',
        divider: 'rgba(255,255,255,0.35)',
        dividerLight: 'rgba(255,255,255,0.15)',
    },
    light: {
        bg: '#E8EDFA',
        border: '#002D72',
        text: '#0F172A',
        secondary: '#475569',
        accent: '#0050B3',
        accentRed: '#C6002A',
        success: '#166534',
        divider: 'rgba(0,45,114,0.35)',
        dividerLight: 'rgba(0,45,114,0.15)',
    }
};

let _exportDataUrl = null;
let _exportCardData = null;

function _buildShareCardHTML(t, data) {
    const stadiumsHTML = data.stadiums.length === 0
        ? `<div style="color:${t.secondary};font-family:'Montserrat',sans-serif;font-weight:800;font-size:0.75rem;text-transform:uppercase;">SIN REGISTROS DE ESTADIOS</div>`
        : data.stadiums.slice(0, 3).map((s, i) => `
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid ${t.dividerLight};padding-bottom:0.3rem;margin-bottom:0.3rem;font-size:0.75rem;font-weight:800;text-transform:uppercase;">
                <span style="color:${t.text};">${i + 1}. ${s.stadium.name}</span>
                <span style="color:${t.accentRed};font-family:'Bebas Neue',sans-serif;font-size:1.1rem;letter-spacing:1px;">${s.visit_count} VISITAS</span>
            </div>`).join('');

    const row = (label, value, color) => `
        <div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px dashed ${t.divider};padding-bottom:0.2rem;">
            <span style="font-weight:800;font-size:0.82rem;text-transform:uppercase;color:${t.text};">${label}</span>
            <span style="font-family:'Bebas Neue',sans-serif;font-size:1.75rem;line-height:1;color:${color};">${value}</span>
        </div>`;

    return `<div style="width:800px;height:500px;background:${t.bg};color:${t.text};border:6px double ${t.border};padding:2rem;box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between;font-family:'Montserrat',sans-serif;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid ${t.border};padding-bottom:1rem;">
            <div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:3.5rem;margin:0;line-height:0.9;letter-spacing:2px;color:${t.text};">CAMPAÑA DE HINCHA</div>
                <span style="font-size:0.85rem;font-weight:800;letter-spacing:2px;color:${t.accent};text-transform:uppercase;">U DE CHILE STATS</span>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.75rem;font-weight:800;color:${t.secondary};letter-spacing:1px;text-transform:uppercase;">HINCHA</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;margin:0;color:${t.accentRed};letter-spacing:1px;">${data.hincha}</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:2rem;flex:1;align-items:center;margin:1.2rem 0;">
            <div style="display:flex;flex-direction:column;gap:0.7rem;">
                ${row('FILTRO ACTIVO', data.filterTitle, t.accent)}
                ${row('PARTIDOS EN EL TABLÓN', data.totalAttended, t.text)}
                ${row('RENDIMIENTO', data.winPct + '%', t.accent)}
                ${row('INVICTO', data.undefeatedPct + '%', t.success)}
                ${row('RÉCORD (V · E · D)', data.record, t.text)}
            </div>
            <div style="display:flex;flex-direction:column;justify-content:space-between;border-left:2px solid ${t.border};padding-left:2rem;height:100%;">
                <div>
                    <span style="font-size:0.75rem;font-weight:800;letter-spacing:1px;color:${t.secondary};text-transform:uppercase;display:block;margin-bottom:0.8rem;">RECINTOS MÁS VISITADOS</span>
                    ${stadiumsHTML}
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid ${t.divider};padding-top:0.8rem;margin-top:auto;">
                    <span style="font-weight:800;font-size:0.85rem;text-transform:uppercase;color:${t.text};">GOLES VISTOS</span>
                    <span style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;line-height:1;">
                        <span style="color:${t.accent};">${data.gf}</span>
                        <span style="color:${t.text};"> F / </span>
                        <span style="color:${t.text};">${data.gc}</span>
                        <span style="color:${t.text};"> C</span>
                    </span>
                </div>
            </div>
        </div>
        <div style="display:flex;justify-content:center;align-items:center;border-top:2px solid ${t.border};padding-top:0.8rem;font-size:0.7rem;font-weight:800;color:${t.secondary};">
            <span>"DENTRO DE LA CANCHA O DESDE EL TABLÓN"</span>
        </div>
    </div>`;
}

function exportDashboardImage() {
    const btn = document.getElementById('btn-export-dashboard');
    if (!btn || !currentSnapshotData) return;

    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="lucide-spin" style="width:1.2rem;height:1.2rem;"></i> GENERANDO...';
    if (window.lucide) lucide.createIcons();

    const isDark = document.documentElement.getAttribute('data-theme') === 'blue';
    const t = isDark ? CARD_THEMES.dark : CARD_THEMES.light;

    _exportCardData = {
        hincha: (window.hinchaName || 'HINCHA').toUpperCase(),
        filterTitle: currentFilterLabel,
        totalAttended: currentSnapshotData.total_matches_attended,
        winPct: currentSnapshotData.win_percentage.toFixed(1),
        undefeatedPct: currentSnapshotData.undefeated_percentage.toFixed(1),
        record: `${currentSnapshotData.wins} · ${currentSnapshotData.draws} · ${currentSnapshotData.losses}`,
        gf: currentSnapshotData.goals_scored_seen,
        gc: currentSnapshotData.goals_conceded_seen,
        stadiums: (currentSnapshotData.most_visited_stadiums || []).slice(0, 3),
    };

    const container = document.getElementById('share-card-render');
    container.innerHTML = _buildShareCardHTML(t, _exportCardData);

    html2canvas(container.firstElementChild, {
        scale: 2,
        useCORS: true,
        backgroundColor: t.bg,
        logging: false,
    }).then(canvas => {
        _exportDataUrl = canvas.toDataURL('image/png');
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        if (window.lucide) lucide.createIcons();
        _openExportModal();
    }).catch(err => {
        console.error('html2canvas error:', err);
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        if (window.lucide) lucide.createIcons();
    });
}

function _openExportModal() {
    document.getElementById('export-preview-img').src = _exportDataUrl;
    document.getElementById('export-tweet-hint').style.display = 'none';
    document.getElementById('export-modal').classList.add('open');
    if (window.lucide) lucide.createIcons();
}

function closeExportModal() {
    document.getElementById('export-modal').classList.remove('open');
}

function downloadExportImage() {
    if (!_exportDataUrl) return;
    const a = document.createElement('a');
    a.href = _exportDataUrl;
    const safeName = (_exportCardData?.filterTitle || 'general').toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    a.download = `campana_hincha_${safeName}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function tweetExportImage() {
    if (!_exportDataUrl || !_exportCardData) return;
    downloadExportImage();
    document.getElementById('export-tweet-hint').style.display = 'block';
    const text = `Mi campaña como hincha de la U 🔵 ${_exportCardData.totalAttended} partidos en el tablón · ${_exportCardData.winPct}% de rendimiento 💪 #UdeChile #HinchaStats`;
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
    window.open(twitterUrl, '_blank', 'width=560,height=450,noopener,noreferrer');
}

// Hook global llamado desde base.html al alternar el tema
window.updateChartTheme = () => {
    // Retrasar levemente para permitir al DOM actualizar los estilos
    setTimeout(() => {
        if (currentSnapshotData) {
            drawChart(currentSnapshotData);
        }
    }, 50);
};
