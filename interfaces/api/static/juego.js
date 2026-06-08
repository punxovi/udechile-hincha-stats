// Juego de Alineaciones Históricas de la Universidad de Chile

let selectedMode = 'normal';
let selectedFormation = '4-4-2';
let activeSlotIndex = null;
let dreamTeam = Array(11).fill(null);
let draftProgress = 0;
let teamRating = 0.0;

// Variables de Ruleta
let resortCount = 3;
let currentSorteadoPlantel = null;
let currentDraftOptions = [];
let rouletteInterval = null;
let isSpinning = false;

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
        { id: 1, pos: 'DEF', label: 'LD', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 4, pos: 'DEF', label: 'LI', row: 2 },
        { id: 5, pos: 'MED', label: 'MC', row: 3 },
        { id: 6, pos: 'MED', label: 'MC', row: 3 },
        { id: 7, pos: 'MED', label: 'MD', row: 3 },
        { id: 8, pos: 'MED', label: 'MI', row: 3 },
        { id: 9, pos: 'DEL', label: 'DC', row: 4 },
        { id: 10, pos: 'DEL', label: 'DC', row: 4 }
    ],
    '4-3-3': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 1, pos: 'DEF', label: 'LD', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 4, pos: 'DEF', label: 'LI', row: 2 },
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
        { id: 1, pos: 'DEF', label: 'LD', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 4, pos: 'DEF', label: 'LI', row: 2 },
        { id: 5, pos: 'MED', label: 'MCD', row: 3 },
        { id: 6, pos: 'MED', label: 'MCD', row: 3 },
        { id: 7, pos: 'MED', label: 'MCO', row: 3 },
        { id: 8, pos: 'MED', label: 'MD', row: 3 },
        { id: 9, pos: 'MED', label: 'MI', row: 3 },
        { id: 10, pos: 'DEL', label: 'DC', row: 4 }
    ]
};

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
    resortCount = 3;
    activeSlotIndex = null;
    isSpinning = false;
    currentSorteadoPlantel = null;
    currentDraftOptions = [];
    
    // Switch de pantalla
    switchScreen('screen-draft');
    
    // Configurar labels del resort
    updateResortLabels();
    
    // Dibujar el campo y el box score
    renderFieldSlots();
    renderBoxScore();
    
    // Limpiar ruleta e inputs
    document.getElementById('roulette-display').textContent = 'SELECCIONA SLOT';
    document.getElementById('btn-spin-roulette').disabled = true;
    document.getElementById('btn-resort-plantel').disabled = true;
    
    document.getElementById('draft-players-list').innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.75rem; padding: 2rem 0; text-transform: uppercase;">
            Toca un slot dashed del campo y gira la ruleta
        </div>
    `;
}

// Cambiar de pantalla del juego
function switchScreen(screenId) {
    document.querySelectorAll('.game-screen').forEach(el => el.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

// Actualizar textos de re-sorteo
function updateResortLabels() {
    const label = document.getElementById('resort-count-label');
    if (label) {
        label.textContent = `¿No te gustó? Re-sortea · ${resortCount} restantes`;
    }
}

// Renderizar grilla del campo tactico de circulos
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
            slotEl.id = `circle-slot-${slot.id}`;
            slotEl.className = 'field-circle-slot';
            slotEl.onclick = () => selectSlot(slot.id, slot.pos);
            
            // Si el slot activo esta seleccionado
            if (activeSlotIndex === slot.id) {
                slotEl.classList.add('active-slot');
            }
            
            // Si tiene jugador asignado
            const player = dreamTeam[slot.id];
            if (player) {
                slotEl.className = 'field-circle-slot filled';
                slotEl.innerHTML = `
                    <span class="filled-rating">${player.rating}</span>
                    <span class="filled-name-badge">${player.name.split(' ').pop()}</span>
                `;
            } else {
                slotEl.innerHTML = `
                    <span class="circle-pos-label">${slot.label}</span>
                `;
            }
            
            rowDiv.appendChild(slotEl);
        });
        
        container.appendChild(rowDiv);
    }
}

// Renderizar Box Score lateral derecho
function renderBoxScore() {
    const slots = FORMACIONES[selectedFormation];
    const container = document.getElementById('box-score-positions-list');
    container.innerHTML = '';
    
    slots.forEach(slot => {
        const player = dreamTeam[slot.id];
        const row = document.createElement('div');
        row.className = 'box-score-row';
        
        row.innerHTML = `
            <span class="box-score-row-pos">${slot.label}</span>
            <span class="box-score-row-name">${player ? player.name : '————'}</span>
            <span class="box-score-row-rating">${player ? player.rating : '--'}</span>
        `;
        
        container.appendChild(row);
    });
    
    // Actualizar progreso
    document.getElementById('box-score-count').textContent = `${draftProgress} / 11`;
    
    // Actualizar rating enorme
    const ratingHuge = document.getElementById('box-score-rating');
    if (draftProgress === 0) {
        ratingHuge.textContent = '--';
    } else {
        ratingHuge.textContent = Math.round(teamRating);
    }
    
    // Actualizar barra de balance
    calculateTeamBalance();
}

// Calcular balance de Ataque vs Defensa
function calculateTeamBalance() {
    const filled = dreamTeam.filter(p => p !== null);
    const fillBar = document.getElementById('balance-bar-fill');
    const ratioText = document.getElementById('balance-ratio-text');
    
    if (filled.length === 0) {
        fillBar.style.width = '50%';
        ratioText.textContent = '50% / 50%';
        return;
    }
    
    let sumDef = 0;
    let countDef = 0;
    let sumAtk = 0;
    let countAtk = 0;
    
    filled.forEach(p => {
        if (p.pos === 'ARQ' || p.pos === 'DEF') {
            sumDef += p.rating;
            countDef++;
        } else {
            sumAtk += p.rating;
            countAtk++;
        }
    });
    
    const avgDef = countDef > 0 ? (sumDef / countDef) : 75.0;
    const avgAtk = countAtk > 0 ? (sumAtk / countAtk) : 75.0;
    
    const total = avgDef + avgAtk;
    const atkPct = Math.round((avgAtk / total) * 100);
    const defPct = 100 - atkPct;
    
    fillBar.style.width = `${atkPct}%`;
    ratioText.textContent = `${atkPct}% / ${defPct}%`;
}

// Activar slot para sorteo
function selectSlot(slotId, pos) {
    if (dreamTeam[slotId] !== null || isSpinning) return;
    
    activeSlotIndex = slotId;
    
    // Redibujar slots para marcar activo
    renderFieldSlots();
    
    // Habilitar boton de girar ruleta
    document.getElementById('btn-spin-roulette').disabled = false;
    document.getElementById('btn-resort-plantel').disabled = true;
    document.getElementById('roulette-display').textContent = 'PRESIONA GIRAR';
    
    document.getElementById('draft-instructions').textContent = `Slot activo: ${FORMACIONES[selectedFormation][slotId].label}. Gira la ruleta para ver planteles.`;
    
    // Limpiar lista de jugadores anterior
    document.getElementById('draft-players-list').innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.75rem; padding: 2rem 0; text-transform: uppercase;">
            Gira la ruleta para revelar futbolistas
        </div>
    `;
}

// Iniciar animacion de ruleta en tiempo real
function startRouletteSpin() {
    if (activeSlotIndex === null || isSpinning) return;
    
    isSpinning = true;
    document.getElementById('btn-spin-roulette').disabled = true;
    document.getElementById('btn-resort-plantel').disabled = true;
    
    const display = document.getElementById('roulette-display');
    const allPlanteles = window.plantelesData;
    const keys = Object.keys(allPlanteles);
    
    // Filtrar planteles segun el modo
    let eligibleKeys = keys;
    if (selectedMode === 'champions') {
        eligibleKeys = keys.filter(k => allPlanteles[k].is_champion === true);
    }
    
    const targetSlot = FORMACIONES[selectedFormation][activeSlotIndex];
    
    // Buscamos un plantel al azar de antemano que contenga al menos un jugador en esa posicion
    let selectedPlantelKey = null;
    let eligiblePlayers = [];
    let attempts = 0;
    
    while (attempts < 50) {
        const randomKey = eligibleKeys[Math.floor(Math.random() * eligibleKeys.length)];
        const p = allPlanteles[randomKey];
        eligiblePlayers = p.players.filter(pl => pl.pos === targetSlot.pos);
        if (eligiblePlayers.length > 0) {
            selectedPlantelKey = randomKey;
            break;
        }
        attempts++;
    }
    
    if (!selectedPlantelKey) {
        selectedPlantelKey = eligibleKeys[0];
        eligiblePlayers = allPlanteles[selectedPlantelKey].players;
    }
    
    const targetPlantel = allPlanteles[selectedPlantelKey];
    
    // Animación de la ruleta (ciclado rapido desacelerando)
    let speed = 40; // ms por ciclo
    let duration = 0;
    const maxDuration = 1800; // 1.8 segundos de giro
    
    function spinCycle() {
        // Mostrar un plantel al azar en el display
        const randomKey = eligibleKeys[Math.floor(Math.random() * eligibleKeys.length)];
        display.textContent = allPlanteles[randomKey].name.replace(' (Campeón)', '').replace(' (Ballet Azul)', '').replace(' (Matador Salas)', '').replace(' (Racha Invicto)', '').replace(' (Vaccia)', '').replace(' (Apertura)', '').replace(' (Sampaoli)', '').replace(' (Triplete)', '').replace(' (Copa Chile)', '').replace(' (Soteldo)', '').replace(' (Transición)', '').replace(' (Larrivey)', '').replace(' (Osorio/Assadi)', '').replace(' (Pellegrino)', '').replace(' (Álvarez)', '').replace(' (Actual)', '').replace(' (Finalista)', '').replace(' (Semifinalista)', '');
        
        duration += speed;
        
        if (duration < maxDuration) {
            // Desacelerar gradualmente aumentando el tiempo de espera
            if (duration > maxDuration * 0.7) {
                speed += 25;
            } else if (duration > maxDuration * 0.4) {
                speed += 12;
            }
            setTimeout(spinCycle, speed);
        } else {
            // Detener en el plantel real asignado
            display.textContent = targetPlantel.name.toUpperCase();
            currentSorteadoPlantel = targetPlantel;
            
            // Elegir hasta 4 opciones de jugadores de esa posicion en el plantel sorteado
            const shuffled = [...eligiblePlayers].sort(() => 0.5 - Math.random());
            currentDraftOptions = shuffled.slice(0, 4);
            
            // Dibujar la lista de jugadores en la columna izquierda
            renderDraftPlayersList(currentDraftOptions, targetPlantel.year);
            
            isSpinning = false;
            
            // Habilitar re-sorteo si le quedan
            if (resortCount > 0) {
                document.getElementById('btn-resort-plantel').disabled = false;
            }
        }
    }
    
    spinCycle();
}

// Dibujar lista de jugadores en la izquierda
function renderDraftPlayersList(players, year) {
    const container = document.getElementById('draft-players-list');
    container.innerHTML = '';
    
    players.forEach((player, idx) => {
        const item = document.createElement('div');
        item.className = 'player-select-item';
        item.onclick = () => recruitPlayer(player, year);
        
        // Numero dorsal ficticio
        const number = `#${idx + 10}`;
        
        item.innerHTML = `
            <div class="item-left">
                <span class="item-number">${number}</span>
                <span class="item-name">${player.name}</span>
                <span class="item-pos">${player.pos}</span>
            </div>
            <span class="item-rating">${player.rating}</span>
        `;
        
        container.appendChild(item);
    });
}

// Re-sortear plantel para el slot activo
function resortPlantel() {
    if (resortCount <= 0 || isSpinning || activeSlotIndex === null) return;
    
    resortCount--;
    updateResortLabels();
    
    // Volver a girar
    startRouletteSpin();
}

// Reclutar y asignar el jugador elegido
function recruitPlayer(player, year) {
    if (activeSlotIndex === null || isSpinning) return;
    
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
    
    // Redibujar todo
    renderFieldSlots();
    renderBoxScore();
    
    // Limpiar panel de ruleta y listado
    document.getElementById('roulette-display').textContent = 'SELECCIONA SLOT';
    document.getElementById('btn-spin-roulette').disabled = true;
    document.getElementById('btn-resort-plantel').disabled = true;
    
    document.getElementById('draft-players-list').innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.75rem; padding: 2rem 0; text-transform: uppercase;">
            Toca otro slot vacío del campo y gira la ruleta
        </div>
    `;
    
    document.getElementById('draft-instructions').textContent = 'Toca un círculo dashed del campo para seleccionarlo';
    
    // Comprobar si terminamos el draft
    if (draftProgress === 11) {
        document.getElementById('btn-advance-tournament').style.display = 'block';
        document.getElementById('draft-instructions').textContent = '¡11 COMPLETADO! Haz clic en el botón de abajo para avanzar.';
    }
}

// Recalcular rating general
function recalculateTeamRating() {
    const filled = dreamTeam.filter(p => p !== null);
    if (filled.length === 0) {
        teamRating = 0.0;
    } else {
        const sum = filled.reduce((acc, p) => acc + p.rating, 0);
        teamRating = sum / filled.length;
    }
}

// Pasar a setup de torneo
function goToTournamentSetup() {
    document.getElementById('summary-formation').textContent = selectedFormation;
    document.getElementById('summary-rating').textContent = teamRating.toFixed(1);
    switchScreen('screen-tournament-setup');
}

// Generar torneo y grupos (Copa de 32 equipos)
function generateTournament() {
    teamName = document.getElementById('input-team-name').value.trim() || "U. DE CHILE HISTÓRICA";
    teamName = teamName.toUpperCase();
    
    const userTeam = {
        id: 0,
        name: teamName,
        rating: teamRating,
        is_user: true,
        players: dreamTeam,
        pts: 0, pj: 0, gf: 0, gc: 0
    };
    
    tournamentTeams = [userTeam];
    
    const allPlanteles = window.plantelesData;
    const keys = Object.keys(allPlanteles);
    
    keys.forEach((key, idx) => {
        const p = allPlanteles[key];
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
    
    const rivals = tournamentTeams.filter(t => !t.is_user);
    const shuffledRivals = rivals.sort(() => 0.5 - Math.random());
    
    groupStandings = [userTeam, shuffledRivals[0], shuffledRivals[1], shuffledRivals[2]];
    
    groupStandings.forEach(t => {
        t.pts = 0; t.pj = 0; t.gf = 0; t.gc = 0;
    });
    
    currentMatchIndex = 0;
    tournamentStage = "groups";
    
    switchScreen('screen-tournament');
    document.getElementById('tournament-team-title').textContent = `MUNDIAL DE LEYENDAS · ${teamName}`;
    
    updateGroupTable();
    updateFixtureView();
    setupNextMatchSimulation();
}

// Actualizar tabla de grupo
function updateGroupTable() {
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
                ${idx + 1}. ${team.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '')} <span style="font-size:0.7rem; color:var(--text-secondary);">(${team.rating.toFixed(1)})</span>
            </td>
            <td style="text-align: center; font-weight: 800; color: var(--text-primary);">${team.pts}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.pj}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.gf}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.gc}</td>
        `;
        tbody.appendChild(row);
    });
}

// Actualizar vista del Fixture
function updateFixtureView() {
    const container = document.getElementById('fixture-matches-container');
    container.innerHTML = '';
    
    if (tournamentStage === "groups") {
        document.getElementById('fixture-stage-title').textContent = 'Fase de Grupos (Clasifican 2)';
        
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
                row.style.borderColor = 'var(--accent-red)';
            }
            
            row.innerHTML = `
                <span style="font-weight: 800; font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">${m.stage}</span>
                <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; color: var(--text-primary);">
                    ${m.home.name.substring(0, 14)} vs ${m.away.name.substring(0, 14)}
                </span>
                <span style="font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; color: var(--text-primary);">
                    ${m.played ? "JUGADO" : (idx === currentMatchIndex ? "POR JUGAR" : "PENDIENTE")}
                </span>
            `;
            container.appendChild(row);
        });
    } else {
        document.getElementById('fixture-stage-title').textContent = playoffStageNames[playoffStageIndex];
        
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.justifyContent = 'space-between';
        row.style.alignItems = 'center';
        row.style.padding = '0.8rem';
        row.style.border = '3px solid var(--text-primary)';
        row.style.background = 'rgba(37,99,235,0.05)';
        
        row.innerHTML = `
            <span style="font-weight: 800; font-size: 0.8rem; color: var(--accent-red); text-transform: uppercase;">MANDATORIO</span>
            <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.9rem; text-transform: uppercase; color: var(--text-primary);">
                ${groupStandings[0].name.substring(0, 14)} vs ${playoffOpponent.name.substring(0, 14)}
            </span>
            <span style="font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; color: var(--text-primary);">
                PLAYOFFS
            </span>
        `;
        container.appendChild(row);
    }
}

// Configurar partido
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
    
    document.getElementById('sim-home-name').textContent = home.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '');
    document.getElementById('sim-home-rating').textContent = `Media: ${home.rating.toFixed(1)}`;
    document.getElementById('sim-away-name').textContent = away.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '');
    document.getElementById('sim-away-rating').textContent = `Media: ${away.rating.toFixed(1)}`;
    document.getElementById('sim-scoreboard').textContent = "0 - 0";
    
    document.getElementById('sim-timer').style.display = 'none';
    document.getElementById('sim-events-log').style.display = 'none';
    document.getElementById('sim-events-log').innerHTML = '';
    
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = false;
    btn.textContent = "JUGAR PARTIDO";
}

// Simular el partido activo
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
    
    logEl.innerHTML += `<div>[00'] ¡PITAZO INICIAL! Arranca el partido en el Estadio Nacional.</div>`;
    
    const interval = setInterval(() => {
        minute += 5;
        timerEl.textContent = `${minute}'`;
        
        const diff = home.rating - away.rating;
        const probHome = Math.max(0.01, Math.min(0.25, 0.07 + (diff * 0.012)));
        const probAway = Math.max(0.01, Math.min(0.25, 0.07 - (diff * 0.012)));
        
        if (Math.random() < probHome) {
            scoreHome++;
            const scorer = chooseScorer(home);
            logEl.innerHTML += `<div style="color: #60A5FA;">[${minute}'] ¡GOOOOOL DE ${home.name.replace(' (CAMPEÓN)', '')}! Anota ${scorer} con definición impecable.</div>`;
            document.getElementById('sim-scoreboard').textContent = `${scoreHome} - ${scoreAway}`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        if (Math.random() < probAway) {
            scoreAway++;
            const scorer = chooseScorer(away);
            logEl.innerHTML += `<div style="color: #F87171;">[${minute}'] ¡Gol del rival ${away.name.replace(' (CAMPEÓN)', '')}! Marca ${scorer}.</div>`;
            document.getElementById('sim-scoreboard').textContent = `${scoreHome} - ${scoreAway}`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        if (Math.random() < 0.08) {
            const teams = [home, away];
            const chosenTeam = teams[Math.floor(Math.random() * 2)];
            const player = chooseScorer(chosenTeam);
            const incidents = [
                `¡Zambombazo de ${player} al travesaño!`,
                `Tarjeta amarilla para ${player} por juego fuerte.`,
                `El arquero contiene un cabezazo letal de ${player}.`,
                `¡Tiro libre peligroso ejecutado por ${player} desviado por el portero!`
            ];
            const msg = incidents[Math.floor(Math.random() * incidents.length)];
            logEl.innerHTML += `<div style="color: #94A3B8;">[${minute}'] ${msg}</div>`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        if (minute >= 90) {
            clearInterval(interval);
            logEl.innerHTML += `<div style="font-weight: 800; margin-top:0.5rem;">[90'] ¡FINAL DEL PARTIDO! Marcador final: ${scoreHome} - ${scoreAway}.</div>`;
            logEl.scrollTop = logEl.scrollHeight;
            
            processMatchResult(scoreHome, scoreAway, home, away);
        }
    }, 400);
}

// Goleador al azar
function chooseScorer(team) {
    if (!team.players || team.players.length === 0) {
        return "Leyenda Azul";
    }
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

// Procesar partido
function processMatchResult(scoreHome, scoreAway, home, away) {
    if (tournamentStage === "groups") {
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
        
        simulateOtherGroupMatches();
        currentMatchIndex++;
        
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
            const sorted = [...groupStandings].sort((a, b) => {
                if (b.pts !== a.pts) return b.pts - a.pts;
                const diffA = a.gf - a.gc;
                const diffB = b.gf - b.gc;
                if (diffB !== diffA) return diffB - diffA;
                return b.gf - a.gf;
            });
            
            const userRank = sorted.findIndex(t => t.is_user) + 1;
            
            if (userRank <= 2) {
                tournamentStage = "playoffs";
                playoffStageIndex = 0;
                playoffOpponent = selectPlayoffOpponent();
                
                btn.textContent = "AVANZAR A OCTAVOS DE FINAL";
                btn.disabled = false;
                btn.onclick = () => {
                    updateFixtureView();
                    setupNextMatchSimulation();
                };
            } else {
                endGame(false, `Quedaste en el puesto #${userRank} del grupo. ¡Casi clasificas!`);
            }
        }
    } else {
        if (scoreHome > scoreAway) {
            advancePlayoffs();
        } else if (scoreHome < scoreAway) {
            endGame(false, `Derrotado en ${playoffStageNames[playoffStageIndex]} frente a ${away.name.replace(' (CAMPEÓN)', '')}.`);
        } else {
            simulatePenalties(home, away);
        }
    }
}

// Simular penales en Playoffs
function simulatePenalties(home, away) {
    const logEl = document.getElementById('sim-events-log');
    logEl.innerHTML += `<div style="font-weight: 800; color: #EAB308; margin-top: 0.5rem;">[PENALES] ¡Empate! Nos vamos a penales.</div>`;
    
    let pensHome = 0;
    let pensAway = 0;
    
    for (let r = 1; r <= 5; r++) {
        const goalHome = Math.random() < 0.75;
        const goalAway = Math.random() < 0.75;
        if (goalHome) pensHome++;
        if (goalAway) pensAway++;
    }
    
    let attempts = 0;
    while (pensHome === pensAway && attempts < 15) {
        const goalHome = Math.random() < 0.75;
        const goalAway = Math.random() < 0.75;
        if (goalHome) pensHome++;
        if (goalAway) pensAway++;
        attempts++;
    }
    
    if (pensHome === pensAway) {
        if (Math.random() < 0.5) pensHome++;
        else pensAway++;
    }
    
    logEl.innerHTML += `<div style="font-weight: 800; color: #EAB308;">[PENALES] Tanda Final: ${pensHome} - ${pensAway}</div>`;
    logEl.scrollTop = logEl.scrollHeight;
    
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = false;
    
    if (pensHome > pensAway) {
        logEl.innerHTML += `<div style="color: #60A5FA; font-weight:800;">¡U. de Chile clasifica en penales!</div>`;
        btn.textContent = "AVANZAR DE RONDA";
        btn.onclick = () => {
            advancePlayoffs();
        };
    } else {
        logEl.innerHTML += `<div style="color: #F87171; font-weight:800;">¡Eliminados en penales!</div>`;
        btn.textContent = "VER RESULTADOS";
        btn.onclick = () => {
            endGame(false, `Fuiste eliminado en penales en ${playoffStageNames[playoffStageIndex]} frente a ${away.name.replace(' (CAMPEÓN)', '')}.`);
        };
    }
}

// Avanzar playoffs
function advancePlayoffs() {
    playoffStageIndex++;
    if (playoffStageIndex < 4) {
        playoffOpponent = selectPlayoffOpponent();
        updateFixtureView();
        setupNextMatchSimulation();
    } else {
        endGame(true, `¡Increíble hazaña! Tu Dream Team se coronó Campeón del Torneo Mundial de Leyendas.`);
    }
}

// Oponente de playoffs
function selectPlayoffOpponent() {
    const rivals = tournamentTeams.filter(t => !t.is_user);
    return rivals[Math.floor(Math.random() * rivals.length)];
}

// Simular resto del grupo
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

// Fin del juego
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
        title.style.color = "var(--accent-red)";
        msg.textContent = message;
        if (btnSave) btnSave.style.display = 'none';
    }
}

// Guardar
function saveToHallOfFame() {
    const btn = document.getElementById('btn-save-muro');
    if (!btn) return;
    
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
        headers: { 'Content-Type': 'application/json' },
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
        window.location.href = "/juego";
    })
    .catch(err => {
        console.error(err);
        btn.disabled = false;
        btn.textContent = "INMORTALIZAR EN MURO DE HONOR";
    });
}

// Reiniciar
function restartGame() {
    switchScreen('screen-setup');
}
