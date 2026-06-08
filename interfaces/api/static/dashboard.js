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
    if (currentFilterType !== 'year') return;
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
    updateDashboardData(yearData, currentFilterLabel);
}

// Actualizar contadores y estadios en la interfaz
function updateDashboardData(snapshot, filterLabel) {
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
            const { ctx, chartArea: { left, right, top, bottom, width, height } } = chart;
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
function exportDashboardImage() {
    const btn = document.getElementById('btn-export-dashboard');
    if (!btn || !currentSnapshotData) return;

    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="lucide-spin" style="width: 1.2rem; height: 1.2rem;"></i> GENERANDO...';
    if (window.lucide) {
        lucide.createIcons();
    }

    // Rellenar datos en el template de compartir
    document.getElementById('share-filter-title').textContent = currentFilterLabel;
    document.getElementById('share-total-attended').textContent = currentSnapshotData.total_matches_attended;
    document.getElementById('share-win-percentage').textContent = currentSnapshotData.win_percentage.toFixed(1) + '%';
    document.getElementById('share-undefeated-percentage').textContent = currentSnapshotData.undefeated_percentage.toFixed(1) + '%';
    document.getElementById('share-record').textContent = `${currentSnapshotData.wins} - ${currentSnapshotData.draws} - ${currentSnapshotData.losses}`;
    document.getElementById('share-gf').textContent = currentSnapshotData.goals_scored_seen;
    document.getElementById('share-gc').textContent = currentSnapshotData.goals_conceded_seen;

    // Rellenar estadios en el template de compartir
    const shareStadiumsContainer = document.getElementById('share-stadiums-container');
    shareStadiumsContainer.innerHTML = '';
    const stadiums = currentSnapshotData.most_visited_stadiums || [];
    
    if (stadiums.length === 0) {
        shareStadiumsContainer.innerHTML = '<div style="color: #CBD5E1;">SIN REGISTROS DE ESTADIOS</div>';
    } else {
        stadiums.slice(0, 3).forEach((entry, idx) => {
            const row = document.createElement('div');
            row.style.borderBottom = '1px solid rgba(255,255,255,0.2)';
            row.style.paddingBottom = '0.3rem';
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.innerHTML = `
                <span>${idx + 1}. ${entry.stadium.name}</span>
                <span style="color: #FC8181; font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; letter-spacing: 1px;">${entry.visit_count} VISITAS</span>
            `;
            shareStadiumsContainer.appendChild(row);
        });
    }

    // Renderizar con html2canvas
    const shareCard = document.getElementById('share-card-template');
    
    html2canvas(shareCard, {
        scale: 2, // Alta calidad
        useCORS: true,
        backgroundColor: '#001B42'
    }).then(canvas => {
        const url = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = url;
        
        const safeName = currentFilterLabel.toLowerCase().replace(/\s+/g, '_');
        a.download = `campana_hincha_${safeName}.png`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        btn.disabled = false;
        btn.innerHTML = originalText;
        if (window.lucide) {
            lucide.createIcons();
        }
    }).catch(err => {
        console.error(err);
        btn.disabled = false;
        btn.innerHTML = originalText;
        if (window.lucide) {
            lucide.createIcons();
        }
    });
}
