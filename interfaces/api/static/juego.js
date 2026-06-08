// Juego de Alineaciones Históricas de la Universidad de Chile

let selectedMode = 'normal';
let selectedFormation = '4-4-2';
let activeSlotIndex = null;
let dreamTeam = Array(11).fill(null);
let draftProgress = 0;
let teamRating = 0.0;

// Datos de torneo
let teamName = "";
let tournamentStage = "groups"; // "groups", "octavos", "cuartos", "semis", "final", "winner", "gameover"
let currentMatchIndex = 0; // Para el fixture de grupos (0, 1, 2)
let tournamentTeams = []; // Array de los 32 equipos
let groupStandings = []; // Los 4 equipos del grupo del usuario
let playoffOpponent = null;
let playoffStageIndex = 0; // 0=Octavos, 1=Cuartos, 2=Semis, 3=Final
const playoffStageNames = ["Octavos de Final", "Cuartos de Final", "Semifinal", "Gran Final"];

// Estructura de posiciones para cada formación
const FORMACIONES = {
    '4-4-2': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 1, pos: 'DEF', label: 'DFD', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 4, pos: 'DEF', label: 'DFI', row: 2 },
        { id: 5, pos: 'MED', label: 'MC', row: 3 },
        { id: 6, pos: 'MED', label: 'MC', row: 3 },
        { id: 7, pos: 'MED', label: 'MD', row: 3 },
        { id: 8, pos: 'MED', label: 'MI', row: 3 },
        { id: 9, pos: 'DEL', label: 'DC', row: 4 },
        { id: 10, pos: 'DEL', label: 'DC', row: 4 }
    ],
    '4-3-3': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 1, pos: 'DEF', label: 'DFD', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 4, pos: 'DEF', label: 'DFI', row: 2 },
        { id: 5, pos: 'MED', label: 'MC', row: 3 },
        { id: 6, pos: 'MED', label: 'MC', row: 3 },
        { id: 7, pos: 'MED', label: 'MCO', row: 3 },
        { id: 8, pos: 'DEL', label: 'ED', row: 4 },
        { id: 9, pos: 'DEL', label: 'DC', row: 4 },
        { id: 10, pos: 'DEL', label: 'EI', row: 4 }
    ],
    '3-5-2': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 1, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 4, pos: 'MED', label: 'MCD', row: 3 },
        { id: 5, pos: 'MED', label: 'MC', row: 3 },
        { id: 6, pos: 'MED', label: 'MC', row: 3 },
        { id: 7, pos: 'MED', label: 'MD', row: 3 },
        { id: 8, pos: 'MED', label: 'MI', row: 3 },
        { id: 9, pos: 'DEL', label: 'DC', row: 4 },
        { id: 10, pos: 'DEL', label: 'DC', row: 4 }
    ],
    '4-2-3-1': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 1, pos: 'DEF', label: 'DFD', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 4, pos: 'DEF', label: 'DFI', row: 2 },
        { id: 5, pos: 'MED', label: 'MCD', row: 3 },
        { id: 6, pos: 'MED', label: 'MCD', row: 3 },
        { id: 7, pos: 'MED', label: 'MCO', row: 3 },
        { id: 8, pos: 'MED', label: 'MD', row: 3 },
        { id: 9, pos: 'MED', label: 'MI', row: 3 },
        { id: 10, pos: 'DEL', label: 'DC', row: 4 }
    ]
};

document.addEventListener("DOMContentLoaded", () => {
    // Inicializar listeners o configuraciones si se requiere
});

// Cambiar modo de juego (Normal / Solo Campeones)
function selectMode(mode) {
    selectedMode = mode;
    document.querySelectorAll('.mode-card').forEach(el => el.classList.remove('active'));
    document.getElementById(`mode-${mode}`).classList.add('active');
}

// Elegir formación
function selectFormation(formation, btnEl) {
    selectedFormation = formation;
    document.querySelectorAll('.formation-btn').forEach(el => el.classList.remove('active'));
    btnEl.classList.add('active');
}

// Iniciar pantalla del Draft
function startDraft() {
    dreamTeam = Array(11).fill(null);
    draftProgress = 0;
    teamRating = 0.0;
    
    // Switch de pantalla
    switchScreen('screen-draft');
    
    // Dibujar el campo de futbol y sus slots vacios
    renderFieldSlots();
}

// Cambiar de pantalla del juego
function switchScreen(screenId) {
    document.querySelectorAll('.game-screen').forEach(el => el.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

// Renderizar grilla del campo tactico
function renderFieldSlots() {
    const container = document.getElementById('field-rows-container');
    container.innerHTML = '';
    
    const slots = FORMACIONES[selectedFormation];
    
    // Dividir en filas de abajo hacia arriba (1=ARQ, 2=DEF, 3=MED, 4=DEL)
    for (let r = 4; r >= 1; r--) {
        const rowSlots = slots.filter(s => s.row === r);
        const rowDiv = document.createElement('div');
        rowDiv.className = 'field-row';
        
        rowSlots.forEach(slot => {
            const slotEl = document.createElement('div');
            slotEl.id = `slot-${slot.id}`;
            slotEl.className = 'player-slot';
            slotEl.onclick = () => selectSlot(slot.id, slot.pos);
            
            // Si tiene jugador asignado
            const player = dreamTeam[slot.id];
            if (player) {
                slotEl.className = 'player-slot filled';
                slotEl.innerHTML = `
                    <span class="slot-pos-badge" style="background: var(--text-secondary);">${slot.label}</span>
                    <span class="slot-card-rating">${player.rating}</span>
                    <span class="slot-card-name">${player.name.split(' ').pop()}</span>
                    <span class="slot-card-year">'${String(player.year).substring(2)}</span>
                `;
            } else {
                slotEl.innerHTML = `
                    <span class="slot-pos-badge">${slot.label}</span>
                    <span class="slot-empty-text">+</span>
                `;
            }
            
            rowDiv.appendChild(slotEl);
        });
        
        container.appendChild(rowDiv);
    }
}

// Activar un slot del campo táctico para iniciar el draft en esa posicion
function selectSlot(slotId, pos) {
    // Si ya esta lleno, no permitir cambiarlo (para añadir mas estrategia de FUT Draft)
    if (dreamTeam[slotId] !== null) return;
    
    activeSlotIndex = slotId;
    
    // Quitar activa de otros slots
    document.querySelectorAll('.player-slot').forEach(el => el.classList.remove('active-slot'));
    
    // Añadir activa al seleccionado
    const activeEl = document.getElementById(`slot-${slotId}`);
    if (activeEl) activeEl.classList.add('active-slot');
    
    // Generar opciones de draft para esa posicion
    generateDraftPool(pos);
}

// Generar una tanda de 4 jugadores elegibles de un plantel al azar
function generateDraftPool(position) {
    const allPlanteles = window.plantelesData;
    const keys = Object.keys(allPlanteles);
    
    // Filtrar planteles segun el modo (champions o todos)
    let eligibleKeys = keys;
    if (selectedMode === 'champions') {
        eligibleKeys = keys.filter(k => allPlanteles[k].is_champion === true);
    }
    
    // Intentar buscar un plantel al azar que tenga al menos un jugador en esta posicion
    let randomPlantel = null;
    let eligiblePlayers = [];
    let attempts = 0;
    
    while (attempts < 50) {
        const randomKey = eligibleKeys[Math.floor(Math.random() * eligibleKeys.length)];
        randomPlantel = allPlanteles[randomKey];
        eligiblePlayers = randomPlantel.players.filter(p => p.pos === position);
        
        // Si encontramos jugadores en este plantel en esa posicion, lo seleccionamos
        if (eligiblePlayers.length > 0) {
            break;
        }
        attempts++;
    }
    
    // En caso extremo de no hallar (no ocurrira con nuestro dataset), buscar en todos
    if (eligiblePlayers.length === 0) {
        const firstKey = keys[0];
        randomPlantel = allPlanteles[firstKey];
        eligiblePlayers = randomPlantel.players;
    }
    
    // Elegir hasta 4 jugadores al azar de esa lista sin repetir
    const shuffled = [...eligiblePlayers].sort(() => 0.5 - Math.random());
    const selectedOptions = shuffled.slice(0, 4);
    
    // Dibujar las opciones en el panel lateral
    const container = document.getElementById('draft-options-container');
    document.getElementById('draft-pool-origin').textContent = `Plantel asignado: ${randomPlantel.name}`;
    
    container.innerHTML = '';
    selectedOptions.forEach(player => {
        const card = document.createElement('div');
        card.className = 'player-card';
        card.onclick = () => recruitPlayer(player, randomPlantel.year);
        
        card.innerHTML = `
            <div style="display: flex; align-items: center;">
                <div class="card-rating-badge">${player.rating}</div>
                <div style="display: flex; flex-direction: column; align-items: flex-start; text-align: left;">
                    <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.95rem; color: var(--text-primary); text-transform: uppercase;">
                        ${player.name}
                    </span>
                    <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase;">
                        Posición: ${player.pos}
                    </span>
                </div>
            </div>
            <i data-lucide="plus-circle" style="width: 1.5rem; height: 1.5rem; color: var(--text-secondary);"></i>
        `;
        
        container.appendChild(card);
    });
    
    if (window.lucide) {
        lucide.createIcons();
    }
}

// Reclutar al jugador seleccionado
function recruitPlayer(player, year) {
    if (activeSlotIndex === null) return;
    
    // Guardar en la alineacion
    dreamTeam[activeSlotIndex] = {
        name: player.name,
        pos: player.pos,
        rating: player.rating,
        year: year
    };
    
    draftProgress++;
    activeSlotIndex = null;
    
    // Recalcular media
    recalculateTeamRating();
    
    // Actualizar progreso en la vista
    document.getElementById('draft-progress').textContent = `${draftProgress}/11`;
    
    // Redibujar campo
    renderFieldSlots();
    
    // Limpiar panel de draft
    const container = document.getElementById('draft-options-container');
    container.innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.8rem; padding: 2rem 0; text-transform: uppercase;">
            Toca otro espacio en el campo para revelar jugadores
        </div>
    `;
    document.getElementById('draft-pool-origin').textContent = `Plantel al azar asignado: --`;
    
    // Si completamos el 11
    if (draftProgress === 11) {
        document.getElementById('btn-advance-tournament').style.display = 'block';
        document.getElementById('draft-instructions').textContent = '¡11 completado con éxito! Haz clic en el botón de abajo para registrar tu equipo.';
    }
}

// Recalcular la media general
function recalculateTeamRating() {
    const filled = dreamTeam.filter(p => p !== null);
    if (filled.length === 0) {
        teamRating = 0.0;
    } else {
        const sum = filled.reduce((acc, p) => acc + p.rating, 0);
        teamRating = sum / filled.length;
    }
    
    document.getElementById('draft-rating-badge').textContent = `Media: ${teamRating.toFixed(1)}`;
}

// Pasar a la pantalla de setup de torneo
function goToTournamentSetup() {
    document.getElementById('summary-formation').textContent = selectedFormation;
    document.getElementById('summary-rating').textContent = teamRating.toFixed(1);
    switchScreen('screen-tournament-setup');
}

// Generar torneo y oponentes
function generateTournament() {
    teamName = document.getElementById('input-team-name').value.trim() || "U. DE CHILE HISTÓRICA";
    teamName = teamName.toUpperCase();
    
    // Creamos los 32 equipos. El equipo 1 es el del usuario
    const userTeam = {
        id: 0,
        name: teamName,
        rating: teamRating,
        is_user: true,
        players: dreamTeam,
        pts: 0, pj: 0, gf: 0, gc: 0
    };
    
    tournamentTeams = [userTeam];
    
    // Obtenemos los otros 31 rivales de los planteles de la BD
    const allPlanteles = window.plantelesData;
    const keys = Object.keys(allPlanteles);
    
    keys.forEach((key, idx) => {
        const p = allPlanteles[key];
        // Calcular la media promedio del rival
        const sum = p.players.reduce((acc, pl) => acc + pl.rating, 0);
        const avg = sum / p.players.length;
        
        tournamentTeams.push({
            id: idx + 1,
            name: p.name.toUpperCase(),
            rating: avg,
            is_user: false,
            players: p.players,
            pts: 0, pj: 0, gf: 0, gc: 0
        });
    });
    
    // Si faltan para llegar a 32 (nuestro dataset tiene 31, así que con el usuario es exactamente 32)
    while (tournamentTeams.length < 32) {
        tournamentTeams.push({
            id: tournamentTeams.length,
            name: `U. DE CHILE CLÁSICA ${tournamentTeams.length}`,
            rating: 77.0,
            is_user: false,
            players: [],
            pts: 0, pj: 0, gf: 0, gc: 0
        });
    }
    
    // Barajar los rivales para asignarlos a los grupos
    const rivals = tournamentTeams.filter(t => !t.is_user);
    const shuffledRivals = rivals.sort(() => 0.5 - Math.random());
    
    // Asignar al Grupo A con el usuario y otros 3 rivales
    groupStandings = [userTeam, shuffledRivals[0], shuffledRivals[1], shuffledRivals[2]];
    
    // Resetear standings
    groupStandings.forEach(t => {
        t.pts = 0; t.pj = 0; t.gf = 0; t.gc = 0;
    });
    
    currentMatchIndex = 0;
    tournamentStage = "groups";
    
    // Switch de pantalla
    switchScreen('screen-tournament');
    document.getElementById('tournament-team-title').textContent = `MUNDIAL DE LEYENDAS · ${teamName}`;
    
    updateGroupTable();
    updateFixtureView();
    setupNextMatchSimulation();
}

// Actualizar tabla del grupo en la pantalla
function updateGroupTable() {
    // Ordenar standings por Puntos, Diferencia de Gol, Goles Favor
    const sorted = [...groupStandings].sort((a, b) => {
        if (b.pts !== a.pts) return b.pts - a.pts;
        const diffA = a.gf - a.gc;
        const diffB = b.gf - b.gc;
        if (diffB !== diffA) return diffB - diffA;
        return b.gf - a.gf;
    });
    
    const tbody = document.getElementById('group-table-body');
    tbody.innerHTML = '';
    
    sorted.forEach((team, idx) => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid rgba(0,0,0,0.1)';
        if (team.is_user) {
            row.style.background = 'rgba(37,99,235,0.08)';
            row.style.fontWeight = '800';
        }
        
        row.innerHTML = `
            <td style="padding: 0.6rem 0; font-family: 'Montserrat', sans-serif; font-weight: 800; color: var(--text-primary);">
                ${idx + 1}. ${team.name} <span style="font-size:0.7rem; color:var(--text-secondary);">(${team.rating.toFixed(1)})</span>
            </td>
            <td style="text-align: center; font-weight: 800; color: var(--text-primary);">${team.pts}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.pj}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.gf}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.gc}</td>
        `;
        tbody.appendChild(row);
    });
}

// Actualizar el listado del Fixture
function updateFixtureView() {
    const container = document.getElementById('fixture-matches-container');
    container.innerHTML = '';
    
    if (tournamentStage === "groups") {
        document.getElementById('fixture-stage-title').textContent = 'Fase de Grupos (Clasifican 2)';
        
        // Las 3 fechas del grupo del usuario
        const matches = [
            { stage: "Fecha 1", home: groupStandings[0], away: groupStandings[1], played: currentMatchIndex > 0 },
            { stage: "Fecha 2", home: groupStandings[0], away: groupStandings[2], played: currentMatchIndex > 1 },
            { stage: "Fecha 3", home: groupStandings[0], away: groupStandings[3], played: currentMatchIndex > 2 }
        ];
        
        matches.forEach((m, idx) => {
            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.padding = '0.6rem';
            row.style.border = '2px solid var(--text-primary)';
            if (idx === currentMatchIndex) {
                row.style.background = 'rgba(37,99,235,0.04)';
                row.style.borderColor = 'var(--udechile-red)';
            }
            
            row.innerHTML = `
                <span style="font-weight: 800; font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">${m.stage}</span>
                <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; color: var(--text-primary);">
                    ${m.home.name.substring(0, 15)} vs ${m.away.name.substring(0, 15)}
                </span>
                <span style="font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; color: var(--text-primary);">
                    ${m.played ? "JUGADO" : (idx === currentMatchIndex ? "POR JUGAR" : "PENDIENTE")}
                </span>
            `;
            container.appendChild(row);
        });
    } else {
        // Fase de Playoffs
        document.getElementById('fixture-stage-title').textContent = playoffStageNames[playoffStageIndex];
        
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.justifyContent = 'space-between';
        row.style.alignItems = 'center';
        row.style.padding = '0.8rem';
        row.style.border = '3px solid var(--text-primary)';
        row.style.background = 'rgba(37,99,235,0.05)';
        
        row.innerHTML = `
            <span style="font-weight: 800; font-size: 0.8rem; color: var(--udechile-red); text-transform: uppercase;">MANDATORIO</span>
            <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.9rem; text-transform: uppercase; color: var(--text-primary);">
                ${groupStandings[0].name.substring(0, 15)} vs ${playoffOpponent.name.substring(0, 15)}
            </span>
            <span style="font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; color: var(--text-primary);">
                PLAYOFFS
            </span>
        `;
        container.appendChild(row);
    }
}

// Configurar los datos en la tarjeta del próximo partido de simulación
function setupNextMatchSimulation() {
    let home, away;
    
    if (tournamentStage === "groups") {
        document.getElementById('match-sim-phase').textContent = `Fase de Grupos · Fecha ${currentMatchIndex + 1}`;
        home = groupStandings[0];
        if (currentMatchIndex === 0) away = groupStandings[1];
        else if (currentMatchIndex === 1) away = groupStandings[2];
        else away = groupStandings[3];
    } else {
        document.getElementById('match-sim-phase').textContent = playoffStageNames[playoffStageIndex];
        home = groupStandings[0];
        away = playoffOpponent;
    }
    
    document.getElementById('sim-home-name').textContent = home.name;
    document.getElementById('sim-home-rating').textContent = `Media: ${home.rating.toFixed(1)}`;
    document.getElementById('sim-away-name').textContent = away.name;
    document.getElementById('sim-away-rating').textContent = `Media: ${away.rating.toFixed(1)}`;
    document.getElementById('sim-scoreboard').textContent = "0 - 0";
    
    // Ocultar bitácora anterior
    document.getElementById('sim-timer').style.display = 'none';
    document.getElementById('sim-events-log').style.display = 'none';
    document.getElementById('sim-events-log').innerHTML = '';
    
    // Habilitar botón
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = false;
    btn.textContent = "JUGAR PARTIDO";
}

// Simular el partido en tiempo real
function simulateActiveMatch() {
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = true;
    
    const logEl = document.getElementById('sim-events-log');
    const timerEl = document.getElementById('sim-timer');
    
    logEl.style.display = 'block';
    timerEl.style.display = 'block';
    logEl.innerHTML = '';
    
    let home, away;
    if (tournamentStage === "groups") {
        home = groupStandings[0];
        if (currentMatchIndex === 0) away = groupStandings[1];
        else if (currentMatchIndex === 1) away = groupStandings[2];
        else away = groupStandings[3];
    } else {
        home = groupStandings[0];
        away = playoffOpponent;
    }
    
    let scoreHome = 0;
    let scoreAway = 0;
    let minute = 0;
    
    logEl.innerHTML += `<div>[00'] ¡PITAZO INICIAL! Arranca el partido en el coloso de Ñuñoa.</div>`;
    
    // Motor de simulación en vivo por intervalos de tiempo
    const interval = setInterval(() => {
        minute += 5;
        timerEl.textContent = `${minute}'`;
        
        // Simular eventos de goles en ciertos tramos
        const diff = home.rating - away.rating;
        
        // Probabilidades de gol basadas en la media
        const probHome = Math.max(0.01, Math.min(0.25, 0.07 + (diff * 0.012)));
        const probAway = Math.max(0.01, Math.min(0.25, 0.07 - (diff * 0.012)));
        
        // Intentos de gol de Home (Usuario)
        if (Math.random() < probHome) {
            scoreHome++;
            // Elegir goleador al azar
            const scorer = chooseScorer(home);
            logEl.innerHTML += `<div style="color: #60A5FA;">[${minute}'] ¡GOOOOOL DE ${home.name}! Anota ${scorer} con un derechazo potente.</div>`;
            document.getElementById('sim-scoreboard').textContent = `${scoreHome} - ${scoreAway}`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        // Intentos de gol de Away (Rival)
        if (Math.random() < probAway) {
            scoreAway++;
            const scorer = chooseScorer(away);
            logEl.innerHTML += `<div style="color: #F87171;">[${minute}'] ¡Gol del rival ${away.name}! Marca ${scorer} tras un rebote en el área.</div>`;
            document.getElementById('sim-scoreboard').textContent = `${scoreHome} - ${scoreAway}`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        // Añadir incidencias aleatorias (tarjetas, tiros al palo, etc.)
        if (Math.random() < 0.08) {
            const teams = [home, away];
            const chosenTeam = teams[Math.floor(Math.random() * 2)];
            const player = chooseScorer(chosenTeam); // Elegir un jugador cualquiera
            const incidents = [
                `¡Tiro en el travesaño de ${player}! Se salva el pórtico.`,
                `Tarjeta amarilla para ${player} por juego peligroso.`,
                `Johnny Herrera desvía un remate a quemarropa de ${player}.`,
                `¡Espectacular atajada del arquero frente al cabezazo de ${player}!`
            ];
            const msg = incidents[Math.floor(Math.random() * incidents.length)];
            logEl.innerHTML += `<div style="color: #94A3B8;">[${minute}'] ${msg}</div>`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        if (minute >= 90) {
            clearInterval(interval);
            logEl.innerHTML += `<div style="font-weight: 800; margin-top:0.5rem;">[90'] ¡FINAL DEL PARTIDO! Marcador final: ${home.name} ${scoreHome} - ${scoreAway} ${away.name}.</div>`;
            logEl.scrollTop = logEl.scrollHeight;
            
            // Procesar resultado final
            processMatchResult(scoreHome, scoreAway, home, away);
        }
    }, 400);
}

// Elegir goleador al azar de un plantel ponderado por su posicion
function chooseScorer(team) {
    if (!team.players || team.players.length === 0) {
        return "Leyenda de la U";
    }
    
    // Ponderación por posición
    const weighted = [];
    team.players.forEach(p => {
        let weight = 1;
        if (p.pos === 'DEL') weight = 6;
        else if (p.pos === 'MED') weight = 3;
        else if (p.pos === 'DEF') weight = 1;
        else weight = 0.01;
        
        for (let i = 0; i < weight * 10; i++) {
            weighted.push(p.name);
        }
    });
    
    return weighted[Math.floor(Math.random() * weighted.length)];
}

// Procesar el fin del partido y actualizar el torneo
function processMatchResult(scoreHome, scoreAway, home, away) {
    if (tournamentStage === "groups") {
        // Actualizar puntos y goles del grupo del usuario
        home.pj++;
        away.pj++;
        home.gf += scoreHome;
        home.gc += scoreAway;
        away.gf += scoreAway;
        away.gc += scoreHome;
        
        if (scoreHome > scoreAway) {
            home.pts += 3;
        } else if (scoreHome < scoreAway) {
            away.pts += 3;
        } else {
            home.pts += 1;
            away.pts += 1;
        }
        
        // Simular el otro partido del grupo de forma rápida en background
        simulateOtherGroupMatches();
        
        currentMatchIndex++;
        
        // Actualizar UI
        updateGroupTable();
        updateFixtureView();
        
        const btn = document.getElementById('btn-start-sim');
        
        if (currentMatchIndex < 3) {
            btn.textContent = "SIGUIENTE FECHA";
            btn.disabled = false;
            btn.onclick = () => {
                setupNextMatchSimulation();
            };
        } else {
            // Fin de la fase de grupos. Evaluar si clasificó
            const sorted = [...groupStandings].sort((a, b) => {
                if (b.pts !== a.pts) return b.pts - a.pts;
                const diffA = a.gf - a.gc;
                const diffB = b.gf - b.gc;
                if (diffB !== diffA) return diffB - diffA;
                return b.gf - a.gf;
            });
            
            const userRank = sorted.findIndex(t => t.is_user) + 1;
            
            if (userRank <= 2) {
                // Avanza a Octavos
                tournamentStage = "playoffs";
                playoffStageIndex = 0;
                // Seleccionar rival al azar de los clasificados del torneo
                playoffOpponent = selectPlayoffOpponent();
                
                btn.textContent = "AVANZAR A OCTAVOS DE FINAL";
                btn.disabled = false;
                btn.onclick = () => {
                    updateFixtureView();
                    setupNextMatchSimulation();
                };
            } else {
                // Eliminado en grupos
                endGame(false, `Quedaste en el puesto #${userRank} del grupo de clasificación. ¡Casi logras la hazaña!`);
            }
        }
    } else {
        // Modo Playoffs (Eliminación Directa)
        if (scoreHome > scoreAway) {
            // Avanza de ronda
            advancePlayoffs();
        } else if (scoreHome < scoreAway) {
            // Eliminado en playoffs
            endGame(false, `Caíste derrotado en ${playoffStageNames[playoffStageIndex]} frente a ${away.name}. ¡Sigue intentándolo!`);
        } else {
            // Empate: Simular penales al instante de forma dramática
            simulatePenalties(home, away);
        }
    }
}

// Simular penales en Playoffs
function simulatePenalties(home, away) {
    const logEl = document.getElementById('sim-events-log');
    logEl.innerHTML += `<div style="font-weight: 800; color: #EAB308; margin-top: 0.5rem;">[PENALES] ¡Empate en los 90 minutos! Nos vamos a la definición a penales.</div>`;
    
    let pensHome = 0;
    let pensAway = 0;
    
    // Simular 5 tiros reglamentarios
    for (let r = 1; r <= 5; r++) {
        const goalHome = Math.random() < 0.75;
        const goalAway = Math.random() < 0.75;
        
        if (goalHome) pensHome++;
        if (goalAway) pensAway++;
    }
    
    // Muerte súbita si empatan
    let attempts = 0;
    while (pensHome === pensAway && attempts < 15) {
        const goalHome = Math.random() < 0.75;
        const goalAway = Math.random() < 0.75;
        
        if (goalHome) pensHome++;
        if (goalAway) pensAway++;
        attempts++;
    }
    
    // En caso extremo
    if (pensHome === pensAway) {
        if (Math.random() < 0.5) pensHome++;
        else pensAway++;
    }
    
    logEl.innerHTML += `<div style="font-weight: 800; color: #EAB308;">[PENALES] Marcador de Penales: ${home.name} ${pensHome} - ${pensAway} ${away.name}</div>`;
    logEl.scrollTop = logEl.scrollHeight;
    
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = false;
    
    if (pensHome > pensAway) {
        logEl.innerHTML += `<div style="color: #60A5FA; font-weight:800;">¡U. de Chile clasifica en tanda de penales espectacular! Johnny Herrera atajó el penal decisivo.</div>`;
        btn.textContent = "AVANZAR DE RONDA";
        btn.onclick = () => {
            advancePlayoffs();
        };
    } else {
        logEl.innerHTML += `<div style="color: #F87171; font-weight:800;">¡Eliminados en penales! El meta rival contuvo el remate definitivo.</div>`;
        btn.textContent = "VER RESULTADOS";
        btn.onclick = () => {
            endGame(false, `Fuiste eliminado en penales en la ronda de ${playoffStageNames[playoffStageIndex]} frente a ${away.name}.`);
        };
    }
}

// Avanzar en las rondas de Playoffs (Octavos -> Cuartos -> Semis -> Final -> Ganador)
function advancePlayoffs() {
    playoffStageIndex++;
    
    const btn = document.getElementById('btn-start-sim');
    
    if (playoffStageIndex < 4) {
        // Siguiente rival en playoffs
        playoffOpponent = selectPlayoffOpponent();
        updateFixtureView();
        setupNextMatchSimulation();
    } else {
        // ¡CAMPEÓN DEL MUNDO!
        endGame(true, `¡Increíble hazaña! Tu Dream Team venció a todos los rivales históricos y se coronó Campeón del Torneo Mundial de Leyendas.`);
    }
}

// Elegir un oponente al azar para la siguiente ronda de Playoffs
function selectPlayoffOpponent() {
    const rivals = tournamentTeams.filter(t => !t.is_user);
    const chosen = rivals[Math.floor(Math.random() * rivals.length)];
    return chosen;
}

// Simular el resto de los partidos del grupo de forma instantánea
function simulateOtherGroupMatches() {
    let home, away;
    if (currentMatchIndex === 0) {
        home = groupStandings[2];
        away = groupStandings[3];
    } else if (currentMatchIndex === 1) {
        home = groupStandings[1];
        away = groupStandings[3];
    } else {
        home = groupStandings[1];
        away = groupStandings[2];
    }
    
    const diff = home.rating - away.rating;
    
    // Simulación simplificada basada en medias
    const probHome = 0.35 + (diff * 0.02);
    const probDraw = 0.30;
    
    const roll = Math.random();
    let gfHome = 0;
    let gfAway = 0;
    
    if (roll < probHome) {
        gfHome = Math.floor(Math.random() * 3) + 1;
        gfAway = Math.floor(Math.random() * gfHome);
    } else if (roll < probHome + probDraw) {
        gfHome = Math.floor(Math.random() * 2);
        gfAway = gfHome;
    } else {
        gfAway = Math.floor(Math.random() * 3) + 1;
        gfHome = Math.floor(Math.random() * gfAway);
    }
    
    home.pj++;
    away.pj++;
    home.gf += gfHome;
    home.gc += gfAway;
    away.gf += gfAway;
    away.gc += gfHome;
    
    if (gfHome > gfAway) {
        home.pts += 3;
    } else if (gfHome < gfAway) {
        away.pts += 3;
    } else {
        home.pts += 1;
        away.pts += 1;
    }
}

// Terminar el juego y mostrar pantalla final
function endGame(isWinner, message) {
    switchScreen('screen-gameover');
    
    const icon = document.getElementById('gameover-status-icon');
    const title = document.getElementById('gameover-title');
    const msg = document.getElementById('gameover-msg');
    const btnSave = document.getElementById('btn-save-muro');
    
    if (isWinner) {
        icon.textContent = "🏆";
        title.textContent = "¡CAMPEÓN DEL MUNDO!";
        title.style.color = "var(--text-primary)";
        msg.textContent = message;
        if (btnSave) btnSave.style.display = 'block';
    } else {
        icon.textContent = "❌";
        title.textContent = "ELIMINADO";
        title.style.color = "var(--udechile-red)";
        msg.textContent = message;
        if (btnSave) btnSave.style.display = 'none';
    }
}

// Enviar y guardar el Dream Team en el Muro de Honor mediante fetch API
function saveToHallOfFame() {
    const btn = document.getElementById('btn-save-muro');
    if (!btn) return;
    
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.textContent = "GUARDANDO...";
    
    const payload = {
        team_name: teamName,
        formation: selectedFormation,
        rating: teamRating,
        players: dreamTeam
    };
    
    fetch('/api/juego/guardar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.status === 401) {
            alert("Debes iniciar sesión para registrar tu Dream Team en el Muro de Honor.");
            throw new Error("No autenticado");
        }
        return res.json();
    })
    .then(data => {
        alert(data.message || "¡Tu equipo ha sido inmortalizado!");
        window.location.href = "/juego"; // Redireccionar para ver el muro actualizado
    })
    .catch(err => {
        console.error(err);
        btn.disabled = false;
        btn.innerHTML = originalText;
    });
}

// Reiniciar y volver a jugar
function restartGame() {
    switchScreen('screen-setup');
}
