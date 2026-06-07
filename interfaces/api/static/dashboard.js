document.addEventListener("DOMContentLoaded", () => {
    const data = window.dashboardData;
    if (!data) return;

    // Obtener colores dinámicos del tema actual
    const style = getComputedStyle(document.documentElement);
    const textPrimary = style.getPropertyValue('--text-primary').trim() || '#002D72';
    const textSecondary = style.getPropertyValue('--text-secondary').trim() || '#475569';
    const textTertiary = style.getPropertyValue('--text-tertiary').trim() || '#64748b';
    const cardBg = style.getPropertyValue('--card-bg').trim() || '#FFFFFF';

    // Configuración general Chart.js alineada a la tipografía del proyecto
    Chart.defaults.color = textSecondary;
    Chart.defaults.font.family = "'Montserrat', sans-serif";
    Chart.defaults.font.weight = 600;

    // Plugin personalizado para dibujar texto en el centro del Doughnut (Rendimiento)
    const centerTextPlugin = {
        id: 'centerText',
        afterDraw(chart) {
            const { ctx, chartArea: { left, right, top, bottom, width, height } } = chart;
            ctx.save();
            
            // Título superior
            ctx.font = "800 0.75rem 'Montserrat', sans-serif";
            ctx.fillStyle = textTertiary;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('RENDIMIENTO', left + width / 2, top + height / 2 - 14);

            // Porcentaje central (Brutalista en Bebas Neue)
            ctx.font = "800 2.8rem 'Bebas Neue', sans-serif";
            ctx.fillStyle = textPrimary;
            ctx.fillText(`${data.win_percentage.toFixed(1)}%`, left + width / 2, top + height / 2 + 12);
            
            ctx.restore();
        }
    };

    // Gráfico de Resultados (Doughnut)
    const ctxResults = document.getElementById('resultsChart');
    if(ctxResults) {
        const ctx = ctxResults.getContext('2d');

        // Colores planos y limpios (sin degradados)
        const colorWin = '#2563EB';  // Azul suave/institucional plano
        const colorDraw = '#94A3B8'; // Gris pizarra plano
        const colorLoss = '#EF4444'; // Rojo suave plano

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Victorias', 'Empates', 'Derrotas'],
                datasets: [{
                    data: [data.wins, data.draws, data.losses],
                    backgroundColor: [colorWin, colorDraw, colorLoss],
                    borderWidth: 3,
                    borderColor: cardBg, // Borde del mismo color de la tarjeta para un look cortado limpio
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
                        cornerRadius: 0 // Estilo brutalista sin esquinas redondeadas
                    }
                },
                cutout: '78%'
            }
        });
    }
});
