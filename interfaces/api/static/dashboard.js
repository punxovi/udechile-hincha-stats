document.addEventListener("DOMContentLoaded", () => {
    const data = window.dashboardData;
    if (!data) return;

    // Configuración general Chart.js (UI/UX Pro Max Rules)
    Chart.defaults.color = '#475569'; // var(--text-secondary)
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.weight = 500;

    // Plugin personalizado para dibujar texto en el centro del Doughnut (Rendimiento)
    const centerTextPlugin = {
        id: 'centerText',
        afterDraw(chart) {
            const { ctx, chartArea: { left, right, top, bottom, width, height } } = chart;
            ctx.save();
            
            // Título de arriba
            ctx.font = "600 0.8rem 'Plus Jakarta Sans', sans-serif";
            ctx.fillStyle = '#64748b'; // text-tertiary
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('RENDIMIENTO', left + width / 2, top + height / 2 - 14);

            // Porcentaje del medio
            ctx.font = "800 2.2rem 'Plus Jakarta Sans', sans-serif";
            ctx.fillStyle = '#0050b3'; // udechile-blue
            ctx.fillText(`${data.win_percentage.toFixed(1)}%`, left + width / 2, top + height / 2 + 12);
            
            ctx.restore();
        }
    };

    // Gráfico de Resultados (Doughnut)
    const ctxResults = document.getElementById('resultsChart');
    if(ctxResults) {
        const ctx = ctxResults.getContext('2d');

        // Gradientes lineales premium para cada sección
        const gradWin = ctx.createLinearGradient(0, 0, 0, 200);
        gradWin.addColorStop(0, '#0050b3'); // Azul Chuncho
        gradWin.addColorStop(1, '#1890ff'); // Azul brillante

        const gradDraw = ctx.createLinearGradient(0, 0, 0, 200);
        gradDraw.addColorStop(0, '#94a3b8'); // Slate
        gradDraw.addColorStop(1, '#cbd5e1');

        const gradLoss = ctx.createLinearGradient(0, 0, 0, 200);
        gradLoss.addColorStop(0, '#d90429'); // Rojo Pasión
        gradLoss.addColorStop(1, '#ff4d4f');

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Victorias', 'Empates', 'Derrotas'],
                datasets: [{
                    data: [data.wins, data.draws, data.losses],
                    backgroundColor: [gradWin, gradDraw, gradLoss],
                    borderWidth: 2,
                    borderColor: 'rgba(255, 255, 255, 0.9)',
                    hoverOffset: 6
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
                            padding: 20, 
                            usePointStyle: true, 
                            pointStyle: 'circle',
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 600 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(10, 25, 49, 0.95)',
                        titleColor: '#ffffff',
                        titleFont: { family: "'Plus Jakarta Sans', sans-serif", size: 13, weight: 700 },
                        bodyColor: '#ffffff',
                        bodyFont: { family: "'Inter', sans-serif", size: 12 },
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 8,
                        usePointStyle: true,
                        cornerRadius: 12
                    }
                },
                cutout: '75%'
            }
        });
    }
});
